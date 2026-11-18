# Heritage Atlas Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, rerunnable Python data pipeline that fetches, classifies, filters, and enriches world heritage and destination data into the static files defined by the data contract.

**Architecture:** A modular Python package (`pipeline/`) managed with `uv`, separating cached raw data downloaders from pure functional transformation steps (classification, per-country adaptive fame filtering, global richness scoring, practical destination metrics) and JSON Schema-validated output emission.

**Tech Stack:** Python 3.12+ (via `uv`), `httpx`, `pydantic` / `jsonschema`, `shapely`, `pyyaml`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-11-18-heritage-atlas-design.md` and `docs/superpowers/plans/2026-11-18-data-contract.md`

## Global Constraints

- Output must strictly conform to `docs/superpowers/plans/2026-11-18-data-contract.md` (`countries.json`, `boundaries.geojson`, `sites/{ISO3}.geojson`, `report.md`).
- Exact 8 categories in display order: `ancient`, `sacred`, `castles`, `towns`, `palaces`, `landscapes`, `modern`, `natural`.
- Richness must be computed as `sqrt(3 * unesco_count + notable_at_global_floor) / max_across_countries`, using a single fixed global fame floor (`sitelinks >= 5`) across all countries so per-country marker tuning does not distort globe glow.
- Per-country marker selection tunes the non-UNESCO fame threshold per country (target band 30–250 non-UNESCO sites, hard floor `sitelinks >= 3`) while keeping all UNESCO sites.
- All network calls must cache raw responses under `pipeline/.cache/` so builds are deterministic and rerunnable offline once cached.
- Licensing & attribution fields (`summarySource`, `image.author`, `image.license`, `image.sourceUrl`) must be populated for every sourced summary and image.

## Review Focus

- Transboundary UNESCO sites (e.g. shared by 2+ countries): must appear in each member country's `sites/{ISO3}.geojson` and increment each country's UNESCO and category counts without crashing or duplicating within a single country.
- Overseas territories & antimeridian bboxes (e.g. France with French Guiana, Fiji/Russia crossing 180°): `main_bbox` must cluster around the main territory (largest polygon + polygons within 500 km) so flying to France doesn't zoom out to the whole globe, and antimeridian countries produce valid `[west, south, east, north]` with `west > east`.
- Duplicate physical sites between UNESCO and Wikidata queries: a Wikidata item that already has `P757` (UNESCO ID) or sits within 250 m of a UNESCO site with normalized matching name must merge into the UNESCO record rather than emitting a duplicate non-UNESCO marker.
- Countries with zero UNESCO sites or missing World Bank / advisory / climate records: must emit valid `countries.json` entries (`null` for missing optional blocks, `0` counts) and an empty `FeatureCollection` in `sites/{ISO3}.geojson`.
- HTML tags and broken entities in UNESCO descriptions or Wikipedia extracts: must be stripped to clean plain text (`1–3` sentences, no `<b>`, `<p>`, `&nbsp;`).

---

### File Structure

- `contract/countries.schema.json` — JSON Schema (draft 2020-12) for `countries.json`
- `contract/sites.schema.json` — JSON Schema (draft 2020-12) for `sites/{ISO3}.geojson`
- `pipeline/pyproject.toml` — `uv` project configuration and dependencies
- `pipeline/src/whs_pipeline/__init__.py`
- `pipeline/src/whs_pipeline/types.py` — Data classes / models matching the contract
- `pipeline/src/whs_pipeline/validate.py` — Schema validator and text sanitizer
- `pipeline/src/whs_pipeline/boundaries.py` — Natural Earth admin-0 loader, main-territory bbox calculator, antimeridian handling
- `pipeline/src/whs_pipeline/unesco.py` — UNESCO WHS ingestion, HTML cleaning, transboundary country resolution, Wikidata P757 join
- `pipeline/src/whs_pipeline/wikidata.py` — Notable non-UNESCO SPARQL fetcher, deduplication against UNESCO sites, Commons image & Wikipedia summary hydration
- `pipeline/src/whs_pipeline/classify.py` — Wikidata QID-to-category mapping, UNESCO criteria fallback, manual overrides loader (`pipeline/curated/category_overrides.yaml`)
- `pipeline/src/whs_pipeline/select.py` — Per-country fame threshold tuning, fame level bucketing, global richness calculation
- `pipeline/src/whs_pipeline/practical.py` — Site spread metric, monthly climate comfort sampling, World Bank PPP cost tier, US State Dept safety advisory, UNESCO Intangible Heritage traditions, curated country teasers (`pipeline/curated/teasers.yaml`)
- `pipeline/src/whs_pipeline/build.py` — End-to-end CLI builder writing `web/static/data/` and `report.md`, plus seeded sample mode (`--sample`) for fast testing

---

### Task 1: Repository Init, Toolchain (`uv`), and Data Contract Schemas

**Files:**
- Create: `pipeline/pyproject.toml`
- Create: `contract/countries.schema.json`
- Create: `contract/sites.schema.json`
- Create: `pipeline/src/whs_pipeline/__init__.py`
- Create: `pipeline/src/whs_pipeline/types.py`
- Create: `pipeline/src/whs_pipeline/validate.py`
- Test: `pipeline/tests/test_validate.py`

**Interfaces:**
- Produces:
  - `whs_pipeline.types.CATEGORIES: tuple[str, ...]`
  - `whs_pipeline.validate.validate_countries_payload(payload: dict) -> None`
  - `whs_pipeline.validate.validate_sites_geojson(payload: dict) -> None`
  - `whs_pipeline.validate.clean_summary(raw_html: str | None, max_sentences: int = 3) -> str`

- [ ] **Step 1: Initialize git repo and `uv` Python project**

Run:
```powershell
git init s:\Projekte\WHSMAP
uv python install 3.12
```
Create `pipeline/pyproject.toml` defining package `whs-pipeline`, Python `>=3.12`, dependencies `httpx`, `jsonschema`, `shapely`, `pyyaml`, and dev dependency `pytest`.

- [ ] **Step 2: Write `contract/countries.schema.json` and `contract/sites.schema.json`**

Encode the exact JSON structures, required keys, enum values (`CATEGORIES`), nullable blocks (`spread`, `climate`, `cost`, `safety`), and array lengths (`bbox` length 4, `climate.tempC` length 12) from `docs/superpowers/plans/2026-11-18-data-contract.md`.

- [ ] **Step 3: Write failing tests in `pipeline/tests/test_validate.py`**

```python
import pytest
from jsonschema import ValidationError
from whs_pipeline.validate import (
    clean_summary,
    validate_countries_payload,
    validate_sites_geojson,
)


def test_clean_summary_strips_html_and_limits_sentences():
    raw = "<p>First sentence &amp; intro. <b>Second</b> sentence! Third one. Fourth ignored.</p>"
    assert clean_summary(raw, max_sentences=3) == "First sentence & intro. Second sentence! Third one."
    assert clean_summary(None) == ""


def test_validate_countries_accepts_zero_site_country_with_null_optionals():
    payload = {
        "generatedAt": "2026-11-18",
        "countries": [
            {
                "iso3": "ISL",
                "name": "Iceland",
                "aliases": [],
                "teaser": "Volcanic landscapes and sagas.",
                "bbox": [-24.5, 63.3, -13.5, 66.6],
                "counts": {
                    "unesco": 0,
                    "notable": 0,
                    "byCategory": {c: 0 for c in ("ancient", "sacred", "castles", "towns", "palaces", "landscapes", "modern", "natural")},
                },
                "richness": 0.0,
                "richnessRaw": 0,
                "spread": None,
                "climate": None,
                "cost": None,
                "safety": None,
                "traditions": {"count": 0, "examples": []},
            }
        ],
    }
    validate_countries_payload(payload)


def test_validate_sites_rejects_invalid_category():
    bad = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": 0,
                "geometry": {"type": "Point", "coordinates": [12.5, 41.9]},
                "properties": {
                    "siteId": "whs-1",
                    "name": "Rome",
                    "category": "invalid-cat",
                    "unesco": True,
                    "inDanger": False,
                    "yearInscribed": 1980,
                    "fame": 100,
                    "fameLevel": 4,
                    "summary": "Text.",
                    "summarySource": "unesco",
                    "image": None,
                    "wikipediaUrl": None,
                    "unescoUrl": "https://whc.unesco.org/en/list/1",
                    "wikidataId": "Q1",
                    "countries": ["ITA"],
                },
            }
        ],
    }
    with pytest.raises(ValidationError):
        validate_sites_geojson(bad)
```

- [ ] **Step 4: Run pytest to verify failure**

Run: `uv run --project pipeline pytest pipeline/tests/test_validate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'whs_pipeline'`

- [ ] **Step 5: Implement `types.py` and `validate.py`**

Implement `CATEGORIES`, schema loading from `contract/*.schema.json` with `jsonschema.validate`, and `clean_summary` using `html.unescape`, regex HTML tag stripping, whitespace normalization, and sentence splitting.

- [ ] **Step 6: Run pytest to verify pass**

Run: `uv run --project pipeline pytest pipeline/tests/test_validate.py -v`
Expected: PASS (3 passed)

- [ ] **Step 7: Commit**

```powershell
git -C s:\Projekte\WHSMAP add .gitignore docs/ contract/ pipeline/
git -C s:\Projekte\WHSMAP commit -m "feat(pipeline): init uv project and data contract schemas"
```

---

### Task 2: Country Boundaries and Main-Territory Bounding Boxes

**Files:**
- Create: `pipeline/src/whs_pipeline/boundaries.py`
- Test: `pipeline/tests/test_boundaries.py`

**Interfaces:**
- Produces:
  - `whs_pipeline.boundaries.compute_main_bbox(geom: dict, cluster_km: float = 500.0) -> list[float]`
  - `whs_pipeline.boundaries.build_boundaries_feature_collection(raw_ne_geojson: dict) -> tuple[dict, dict[str, dict]]` (returns `(boundaries_geojson, country_meta_by_iso3)`)

- [ ] **Step 1: Write failing tests in `pipeline/tests/test_boundaries.py`**

```python
from whs_pipeline.boundaries import compute_main_bbox, build_boundaries_feature_collection


def test_compute_main_bbox_ignores_distant_overseas_polygon():
    # Metropolitan France polygon near (2E, 46N) + small French Guiana polygon near (-53W, 4N)
    geom = {
        "type": "MultiPolygon",
        "coordinates": [
            [[[-5.0, 42.0], [8.0, 42.0], [8.0, 51.0], [-5.0, 51.0], [-5.0, 42.0]]],
            [[[-54.0, 2.0], [-51.0, 2.0], [-51.0, 6.0], [-54.0, 6.0], [-54.0, 2.0]]],
        ],
    }
    bbox = compute_main_bbox(geom, cluster_km=500.0)
    assert bbox == [-5.0, 42.0, 8.0, 51.0]


def test_compute_main_bbox_handles_antimeridian_crossing():
    # Two islands straddling 180°: one at 178..179.9E, one at -179.9..-178W
    geom = {
        "type": "MultiPolygon",
        "coordinates": [
            [[[178.0, -18.0], [179.9, -18.0], [179.9, -16.0], [178.0, -16.0], [178.0, -18.0]]],
            [[[-179.9, -18.0], [-178.0, -18.0], [-178.0, -16.0], [-179.9, -16.0], [-179.9, -18.0]]],
        ],
    }
    west, south, east, north = compute_main_bbox(geom, cluster_km=500.0)
    assert west == 178.0 and east == -178.0
    assert west > east
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `uv run --project pipeline pytest pipeline/tests/test_boundaries.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'whs_pipeline.boundaries'`

- [ ] **Step 3: Implement `pipeline/src/whs_pipeline/boundaries.py`**

Use `shapely.geometry.shape` to find the largest polygon by area, keep all component polygons whose minimum distance to the largest polygon is `<= cluster_km` (converting degrees to approximate km via cosine of mid-latitude, handling antimeridian wrap by checking shifted longitudes `[lon + 360 if lon < 0 else lon]`), and compute `[west, south, east, north]` (choosing the narrower longitude span between standard `[-180, 180]` and wrapped `[0, 360]` so antimeridian countries yield `west > east`). Assign sequential numeric `feature.id` (`0, 1, ...`) and normalize ISO3 codes (`ADM0_A3` / `ISO_A3`).

- [ ] **Step 4: Run pytest to verify pass**

Run: `uv run --project pipeline pytest pipeline/tests/test_boundaries.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```powershell
git -C s:\Projekte\WHSMAP add pipeline/src/whs_pipeline/boundaries.py pipeline/tests/test_boundaries.py
git -C s:\Projekte\WHSMAP commit -m "feat(pipeline): add country boundary normalization and main-territory bbox"
```

---

### Task 3: Category Classification and Overrides

**Files:**
- Create: `pipeline/src/whs_pipeline/classify.py`
- Create: `pipeline/curated/category_overrides.yaml`
- Test: `pipeline/tests/test_classify.py`

**Interfaces:**
- Produces:
  - `whs_pipeline.classify.classify_site(site_id: str, instance_of_qids: list[str], unesco_type: str | None, name: str, overrides: dict[str, str]) -> str`
  - `whs_pipeline.classify.load_overrides(path: Path) -> dict[str, str]`

- [ ] **Step 1: Write failing tests in `pipeline/tests/test_classify.py`**

```python
from whs_pipeline.classify import classify_site


def test_override_wins_over_everything():
    assert classify_site("whs-91", ["Q23413"], "Cultural", "Historic Centre of Rome", {"whs-91": "towns"}) == "towns"


def test_wikidata_qid_mapping_resolves_categories():
    assert classify_site("wd-Q1", ["Q23413"], None, "Burg Eltz", {}) == "castles"
    assert classify_site("wd-Q2", ["Q44613"], None, "Monastery", {}) == "sacred"
    assert classify_site("wd-Q3", ["Q839954"], None, "Pompeii", {}) == "ancient"


def test_unesco_natural_and_keyword_fallbacks():
    assert classify_site("whs-2", [], "Natural", "Serengeti National Park", {}) == "natural"
    assert classify_site("whs-3", [], "Cultural", "Cathedral of Chartres", {}) == "sacred"
    assert classify_site("whs-4", [], "Cultural", "Palace and Park of Versailles", {}) == "palaces"
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `uv run --project pipeline pytest pipeline/tests/test_classify.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'whs_pipeline.classify'`

- [ ] **Step 3: Implement `classify.py` and seed `pipeline/curated/category_overrides.yaml`**

Implement deterministic priority rules in `classify_site`:
1. Exact `site_id` match in `overrides` (validated against `CATEGORIES`).
2. `unesco_type == "Natural"` → `"natural"`.
3. Wikidata `instance_of_qids` lookup against curated QID sets for `castles` (`Q23413`, `Q57821`, `Q1785071`), `sacred` (`Q16970`, `Q2977`, `Q32815`, `Q44613`, `Q24398318`, `Q44539`), `ancient` (`Q839954`, `Q109607`, `Q15661340`), `palaces` (`Q16560`, `Q1802963`), `towns` (`Q30198`, `Q15284`, `Q515`), `modern` (`Q16695773`, `Q4989906`), `landscapes` (`Q1129474`, `Q1107656`), `natural` (`Q46169`, `Q8502`).
4. Keyword matcher on `name` (case-insensitive) for castle/fortress, cathedral/temple/mosque/monastery/church/shrine, archaeological/ruins/tomb/necropolis/rock art, historic centre/old town/medina, palace/residence/villa, industrial/mine/railway/bridge, landscape/garden/vineyard.
5. Fallback: `"natural"` if `unesco_type == "Mixed"`, else `"ancient"`.

Create `pipeline/curated/category_overrides.yaml` with initial overrides for ambiguous iconic UNESCO sites.

- [ ] **Step 4: Run pytest to verify pass**

Run: `uv run --project pipeline pytest pipeline/tests/test_classify.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```powershell
git -C s:\Projekte\WHSMAP add pipeline/src/whs_pipeline/classify.py pipeline/curated/category_overrides.yaml pipeline/tests/test_classify.py
git -C s:\Projekte\WHSMAP commit -m "feat(pipeline): add site category classification and overrides"
```

---

### Task 4: UNESCO & Wikidata Ingestion and Spatial/ID Deduplication

**Files:**
- Create: `pipeline/src/whs_pipeline/unesco.py`
- Create: `pipeline/src/whs_pipeline/wikidata.py`
- Test: `pipeline/tests/test_ingest_dedup.py`

**Interfaces:**
- Consumes: `clean_summary` from `whs_pipeline.validate`, `classify_site` from `whs_pipeline.classify`
- Produces:
  - `whs_pipeline.unesco.parse_unesco_records(raw_records: list[dict], wikidata_by_whs_id: dict[str, dict], overrides: dict[str, str]) -> list[dict]`
  - `whs_pipeline.wikidata.merge_and_deduplicate_notable(unesco_sites: list[dict], raw_notable: list[dict], overrides: dict[str, str]) -> list[dict]`

- [ ] **Step 1: Write failing tests in `pipeline/tests/test_ingest_dedup.py`**

```python
from whs_pipeline.unesco import parse_unesco_records
from whs_pipeline.wikidata import merge_and_deduplicate_notable


def test_transboundary_unesco_site_preserves_all_iso3_codes():
    raw = [
        {
            "id_no": "91",
            "name_en": "Historic Centre of Rome, the Properties of the Holy See",
            "short_description_en": "<p>Founded by Romulus and Remus.</p>",
            "category": "Cultural",
            "danger": 0,
            "date_inscribed": 1980,
            "longitude": 12.4922,
            "latitude": 41.8902,
            "iso_code": "it,va",
        }
    ]
    wd = {"91": {"qid": "Q152874", "sitelinks": 112, "instance_of": ["Q30198"], "image": None, "wikipedia_url": "https://en.wikipedia.org/wiki/Historic_Centre_of_Rome"}}
    sites = parse_unesco_records(raw, wd, {"whs-91": "towns"})
    assert len(sites) == 1
    assert sites[0]["siteId"] == "whs-91"
    assert sites[0]["countries"] == ["ITA", "VAT"]
    assert sites[0]["summary"] == "Founded by Romulus and Remus."


def test_deduplicate_drops_notable_matching_unesco_by_qid_or_proximity():
    unesco = [
        {
            "siteId": "whs-91",
            "name": "Colosseum",
            "wikidataId": "Q10285",
            "lon": 12.4922,
            "lat": 41.8902,
            "countries": ["ITA"],
        }
    ]
    notable_raw = [
        # Duplicate by Wikidata QID
        {"qid": "Q10285", "name": "Colosseum", "lon": 12.4922, "lat": 41.8902, "sitelinks": 150, "iso3": "ITA", "instance_of": ["Q839954"]},
        # Duplicate by <250m proximity + matching normalized name
        {"qid": "Q99999", "name": "The Colosseum", "lon": 12.4925, "lat": 41.8904, "sitelinks": 45, "iso3": "ITA", "instance_of": ["Q839954"]},
        # Distinct site
        {"qid": "Q47891", "name": "Pantheon", "lon": 12.4769, "lat": 41.8986, "sitelinks": 120, "iso3": "ITA", "instance_of": ["Q44539"]},
    ]
    kept = merge_and_deduplicate_notable(unesco, notable_raw, {})
    assert [s["siteId"] for s in kept] == ["wd-Q47891"]
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `uv run --project pipeline pytest pipeline/tests/test_ingest_dedup.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'whs_pipeline.unesco'`

- [ ] **Step 3: Implement `unesco.py` and `wikidata.py`**

In `unesco.py`:
- Map 2-letter ISO codes (`iso_code` comma-separated) to ISO3 codes via a complete ISO2→ISO3 dictionary.
- Clean HTML descriptions via `clean_summary`, join Wikidata enrichment by `id_no` (P757), and classify via `classify_site`.
- Provide cached HTTP downloader `fetch_unesco_raw(cache_dir: Path) -> list[dict]`.

In `wikidata.py`:
- Provide cached SPARQL fetcher `fetch_wikidata_sites(cache_dir: Path)` querying heritage items with coordinates, P17 country ISO3, P31 instance-of, P18 Commons image filename, English Wikipedia sitelink, and total sitelink count.
- Convert Commons filenames into deterministic thumbnail URLs (`https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/{encoded_filename}&width=640`) and license metadata.
- In `merge_and_deduplicate_notable`: drop any candidate whose `qid` equals a UNESCO site's `wikidataId`, or that has `whs_id` set, or that sits within 250 m (Haversine distance) of a UNESCO site in the same country with normalized token overlap in `name`.

- [ ] **Step 4: Run pytest to verify pass**

Run: `uv run --project pipeline pytest pipeline/tests/test_ingest_dedup.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```powershell
git -C s:\Projekte\WHSMAP add pipeline/src/whs_pipeline/unesco.py pipeline/src/whs_pipeline/wikidata.py pipeline/tests/test_ingest_dedup.py
git -C s:\Projekte\WHSMAP commit -m "feat(pipeline): add UNESCO and Wikidata ingestion with spatial deduplication"
```

---

### Task 5: Per-Country Fame Threshold Tuning and Global Richness Scoring

**Files:**
- Create: `pipeline/src/whs_pipeline/select.py`
- Test: `pipeline/tests/test_select.py`

**Interfaces:**
- Produces:
  - `whs_pipeline.select.fame_level(sitelinks: int) -> int`
  - `whs_pipeline.select.select_country_sites(unesco_sites: list[dict], notable_candidates: list[dict], min_floor: int = 3, default_floor: int = 5, target_min: int = 15, target_max: int = 180) -> list[dict]`
  - `whs_pipeline.select.compute_global_richness(unesco_by_iso3: dict[str, int], notable_candidates_by_iso3: dict[str, list[dict]], global_floor: int = 5) -> dict[str, tuple[int, float]]`

- [ ] **Step 1: Write failing tests in `pipeline/tests/test_select.py`**

```python
from whs_pipeline.select import compute_global_richness, fame_level, select_country_sites


def test_fame_level_buckets():
    assert fame_level(0) == 1
    assert fame_level(9) == 1
    assert fame_level(10) == 2
    assert fame_level(29) == 2
    assert fame_level(30) == 3
    assert fame_level(80) == 4


def test_select_country_sites_tunes_threshold_and_sorts_unesco_first():
    unesco = [{"siteId": "whs-1", "unesco": True, "fame": 12}]
    # Sparse country: only 4 notable sites with fame 3..4; threshold lowers to min_floor=3
    sparse_notable = [{"siteId": f"wd-{i}", "unesco": False, "fame": 3 + (i % 2)} for i in range(4)]
    selected = select_country_sites(unesco, sparse_notable, min_floor=3, default_floor=5, target_min=10, target_max=50)
    assert selected[0]["siteId"] == "whs-1"
    assert len(selected) == 5

    # Dense country: 100 notable sites with varying fame; threshold raises so <= target_max are kept
    dense_notable = [{"siteId": f"wd-{i}", "unesco": False, "fame": i} for i in range(1, 101)]
    dense_selected = select_country_sites([], dense_notable, min_floor=3, default_floor=5, target_min=10, target_max=25)
    assert len(dense_selected) <= 25
    assert dense_selected[0]["fame"] >= dense_selected[-1]["fame"] >= 5


def test_global_richness_uses_fixed_global_floor_not_tuned_counts():
    unesco_counts = {"ITA": 60, "IRL": 2, "NRU": 0}
    notable_by_iso3 = {
        "ITA": [{"fame": 10}] * 200 + [{"fame": 3}] * 500,
        "IRL": [{"fame": 10}] * 15 + [{"fame": 3}] * 40,
        "NRU": [],
    }
    res = compute_global_richness(unesco_counts, notable_by_iso3, global_floor=5)
    assert res["ITA"][0] == 3 * 60 + 200
    assert res["ITA"][1] == 1.0
    assert res["IRL"][0] == 3 * 2 + 15
    assert 0.0 < res["IRL"][1] < 1.0
    assert res["NRU"] == (0, 0.0)
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `uv run --project pipeline pytest pipeline/tests/test_select.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'whs_pipeline.select'`

- [ ] **Step 3: Implement `pipeline/src/whs_pipeline/select.py`**

Implement:
- `fame_level(sitelinks)`: `1` if `< 10`, `2` if `< 30`, `3` if `< 80`, `4` if `>= 80`.
- `select_country_sites`: never filter out `unesco_sites`. Filter `notable_candidates` starting at `default_floor=5`: if count `< target_min`, lower threshold down to `min_floor=3`; if count `> target_max`, raise threshold and take top `target_max` by `fame` descending (tie-broken by `siteId`). Return `unesco_sites` (sorted by `fame` desc, `siteId`) followed by selected notable sites (sorted by `fame` desc, `siteId`).
- `compute_global_richness`: for each country, `raw = 3 * unesco_count + sum(1 for s in candidates if s["fame"] >= global_floor)`. Let `max_raw = max(raw_values) or 1`. `richness = round(math.sqrt(raw / max_raw), 4)`.

- [ ] **Step 4: Run pytest to verify pass**

Run: `uv run --project pipeline pytest pipeline/tests/test_select.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```powershell
git -C s:\Projekte\WHSMAP add pipeline/src/whs_pipeline/select.py pipeline/tests/test_select.py
git -C s:\Projekte\WHSMAP commit -m "feat(pipeline): add adaptive site selection and global richness scoring"
```

---

### Task 6: Country "What to Expect" Metrics and Curated Teasers

**Files:**
- Create: `pipeline/src/whs_pipeline/practical.py`
- Create: `pipeline/curated/teasers.yaml`
- Test: `pipeline/tests/test_practical.py`

**Interfaces:**
- Produces:
  - `whs_pipeline.practical.compute_spread(coords: list[tuple[float, float]]) -> dict | None`
  - `whs_pipeline.practical.compute_climate_comfort(temp_c: list[float], precip_mm: list[float]) -> dict`
  - `whs_pipeline.practical.compute_cost_tier(price_level_ratio: float | None, year: int | None) -> dict | None`
  - `whs_pipeline.practical.resolve_teaser(iso3: str, name: str, counts: dict, curated: dict[str, str]) -> str`

- [ ] **Step 1: Write failing tests in `pipeline/tests/test_practical.py`**

```python
from whs_pipeline.practical import (
    compute_climate_comfort,
    compute_cost_tier,
    compute_spread,
    resolve_teaser,
)


def test_compute_spread_classifications():
    assert compute_spread([(12.5, 41.9)]) is None
    compact = compute_spread([(14.4, 35.9), (14.5, 35.85), (14.35, 35.92)])
    assert compact["level"] == "compact"
    spread = compute_spread([(-70.0, -15.0), (-120.0, 45.0), (10.0, 50.0)])
    assert spread["level"] == "spread"


def test_compute_climate_comfort_marks_pleasant_dry_months():
    temps = [5.0, 7.0, 12.0, 16.0, 21.0, 26.0, 31.0, 30.0, 24.0, 18.0, 11.0, 6.0]
    precip = [80, 70, 60, 50, 40, 20, 10, 15, 45, 90, 110, 95]
    c = compute_climate_comfort(temps, precip)
    assert len(c["comfortable"]) == 12
    # May (21C, 40mm) is comfortable; Jan (5C) and Jul (31C) are not
    assert c["comfortable"][4] is True
    assert c["comfortable"][0] is False
    assert c["comfortable"][6] is False


def test_compute_cost_tier_maps_ppp_ratio_to_1_to_5():
    assert compute_cost_tier(None, None) is None
    assert compute_cost_tier(0.30, 2023)["tier"] == 1
    assert compute_cost_tier(0.65, 2023)["tier"] == 3
    assert compute_cost_tier(1.25, 2023)["tier"] == 5


def test_resolve_teaser_uses_curated_then_fallback():
    counts = {"unesco": 3, "notable": 12, "byCategory": {"ancient": 8, "sacred": 7}}
    assert resolve_teaser("ITA", "Italy", counts, {"ITA": "Curated line."}) == "Curated line."
    fallback = resolve_teaser("XYZ", "Xyland", counts, {})
    assert "3 World Heritage Sites" in fallback
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `uv run --project pipeline pytest pipeline/tests/test_practical.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'whs_pipeline.practical'`

- [ ] **Step 3: Implement `practical.py` and `pipeline/curated/teasers.yaml`**

In `practical.py`:
- `compute_spread(coords)`: return `None` if `< 2` coordinates. Otherwise compute pairwise Haversine distances (for `<= 80` sites, or random deterministic sample of 80 sites), take median distance `median_km = round(median)`. Classify `"compact"` if `< 150`, `"moderate"` if `<= 600`, `"spread"` if `> 600`.
- `compute_climate_comfort(temp_c, precip_mm)`: month is comfortable if `13.0 <= t <= 28.0` and `p <= 130.0`. If zero months match (e.g. cold or tropical destination), mark the top 3 months closest to `20°C` and lowest precipitation so every country shows its relatively best months.
- `compute_cost_tier(ratio, year)`: return `None` if `ratio is None`; map `< 0.40 → 1`, `< 0.58 → 2`, `< 0.78 → 3`, `< 1.00 → 4`, `>= 1.00 → 5`.
- `resolve_teaser`: return `curated[iso3]` if present and non-empty; else generate factual 1-sentence summary naming the top 2 categories and total UNESCO/heritage sites.
- Write `pipeline/curated/teasers.yaml` with 65 hand-crafted 1-sentence cultural teasers for the top heritage countries (Italy, China, Germany, France, Spain, India, Mexico, UK, Russia, Iran, Japan, Brazil, Turkey, Greece, Egypt, Peru, Morocco, Jordan, Cambodia, Ethiopia, etc.).

- [ ] **Step 4: Run pytest to verify pass**

Run: `uv run --project pipeline pytest pipeline/tests/test_practical.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```powershell
git -C s:\Projekte\WHSMAP add pipeline/src/whs_pipeline/practical.py pipeline/curated/teasers.yaml pipeline/tests/test_practical.py
git -C s:\Projekte\WHSMAP commit -m "feat(pipeline): add destination practical metrics and 65 country teasers"
```

---

### Task 7: End-to-End Pipeline Builder, Validation Report, and Seeded Dataset Generation

**Files:**
- Create: `pipeline/src/whs_pipeline/build.py`
- Create: `pipeline/fixtures/seed_dataset.json`
- Test: `pipeline/tests/test_build_e2e.py`

**Interfaces:**
- Consumes: Tasks 1–6 modules
- Produces:
  - `whs_pipeline.build.build_dataset(out_dir: Path, cache_dir: Path, offline_seed: Path | None = None) -> dict`
  - CLI entrypoint: `uv run --project pipeline python -m whs_pipeline.build --out web/static/data`
  - Static output files in `web/static/data/` (`countries.json`, `boundaries.geojson`, `sites/{ISO3}.geojson`, `report.md`)

- [ ] **Step 1: Write failing end-to-end test in `pipeline/tests/test_build_e2e.py`**

```python
import json
from pathlib import Path
from whs_pipeline.build import build_dataset
from whs_pipeline.validate import validate_countries_payload, validate_sites_geojson


def test_build_dataset_produces_schema_valid_outputs_and_report(tmp_path: Path):
    seed_path = Path(__file__).parent.parent / "fixtures" / "seed_dataset.json"
    summary = build_dataset(out_dir=tmp_path, cache_dir=tmp_path / "cache", offline_seed=seed_path)

    countries_file = tmp_path / "countries.json"
    boundaries_file = tmp_path / "boundaries.geojson"
    report_file = tmp_path / "report.md"

    assert countries_file.exists() and boundaries_file.exists() and report_file.exists()
    countries_payload = json.loads(countries_file.read_text(encoding="utf-8"))
    validate_countries_payload(countries_payload)

    assert summary["country_count"] >= 30
    for c in countries_payload["countries"]:
        site_file = tmp_path / "sites" / f"{c['iso3']}.geojson"
        assert site_file.exists()
        site_payload = json.loads(site_file.read_text(encoding="utf-8"))
        validate_sites_geojson(site_payload)
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `uv run --project pipeline pytest pipeline/tests/test_build_e2e.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'whs_pipeline.build'`

- [ ] **Step 3: Implement `build.py` and `pipeline/fixtures/seed_dataset.json`**

Create `pipeline/fixtures/seed_dataset.json` containing rich, realistic multi-country fixture data (including major heritage countries across all continents, transboundary sites, a country with overseas territory, an antimeridian country, and a zero-site country) plus live fetch orchestration in `build.py` (with `--seed` fallback when running offline or in CI).
Ensure `build_dataset` validates every emitted JSON/GeoJSON file with `validate_countries_payload` and `validate_sites_geojson` before returning, and writes `report.md` summarizing country counts, category totals, and missing image/coordinate percentages.

- [ ] **Step 4: Run pytest and execute pipeline to populate `web/static/data/`**

Run:
```powershell
uv run --project pipeline pytest -v
uv run --project pipeline python -m whs_pipeline.build --out s:\Projekte\WHSMAP\web\static\data
```
Expected: All tests PASS; `web/static/data/countries.json`, `web/static/data/boundaries.geojson`, `web/static/data/sites/*.geojson`, and `web/static/data/report.md` exist and pass schema validation.

- [ ] **Step 5: Commit**

```powershell
git -C s:\Projekte\WHSMAP add pipeline/ web/static/data/
git -C s:\Projekte\WHSMAP commit -m "feat(pipeline): complete end-to-end dataset builder and generate static data"
```
