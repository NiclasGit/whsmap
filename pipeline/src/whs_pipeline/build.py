"""End-to-end dataset builder and CLI for Heritage Atlas."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
from typing import Any

import httpx

from whs_pipeline.boundaries import build_boundaries_feature_collection
from whs_pipeline.classify import load_overrides
from whs_pipeline.practical import (
    compute_climate_comfort,
    compute_cost_tier,
    compute_spread,
    load_teasers,
    resolve_teaser,
)
from whs_pipeline.select import compute_global_richness, select_country_sites
from whs_pipeline.types import CATEGORIES
from whs_pipeline.unesco import parse_unesco_records
from whs_pipeline.validate import validate_countries_payload, validate_sites_geojson
from whs_pipeline.wikidata import build_commons_image, merge_and_deduplicate_notable

PIPELINE_ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = PIPELINE_ROOT / "curated"
DEFAULT_SEED = PIPELINE_ROOT / "fixtures" / "seed_dataset.json"

NE_COUNTRIES_GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
)


def _site_to_geojson_feature(idx: int, site: dict[str, Any]) -> dict[str, Any]:
    image = site.get("image")
    if isinstance(image, str):
        image = build_commons_image(image)
    return {
        "type": "Feature",
        "id": idx,
        "geometry": {
            "type": "Point",
            "coordinates": [float(site["lon"]), float(site["lat"])],
        },
        "properties": {
            "siteId": site["siteId"],
            "name": site["name"],
            "category": site["category"],
            "unesco": bool(site["unesco"]),
            "inDanger": bool(site.get("inDanger", False)),
            "yearInscribed": site.get("yearInscribed"),
            "fame": int(site.get("fame", 0)),
            "fameLevel": int(site["fameLevel"]),
            "summary": str(site.get("summary") or ""),
            "summarySource": site.get("summarySource"),
            "image": image,
            "wikipediaUrl": site.get("wikipediaUrl"),
            "unescoUrl": site.get("unescoUrl"),
            "wikidataId": site.get("wikidataId"),
            "countries": list(site["countries"]),
        },
    }


def _load_or_fetch_raw(cache_dir: Path, offline_seed: Path | None) -> dict[str, Any]:
    seed_file = offline_seed or DEFAULT_SEED
    data = json.loads(seed_file.read_text(encoding="utf-8"))
    ne_cache = cache_dir / "ne_110m_admin_0_countries.geojson"
    if ne_cache.exists():
        ne_geo = json.loads(ne_cache.read_text(encoding="utf-8"))
        if ne_geo.get("features"):
            data["boundaries_raw"] = ne_geo
    return data


def fetch_natural_earth_to_cache(cache_dir: Path) -> Path:
    """Download Natural Earth 110m admin-0 boundaries to cache_dir if missing."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / "ne_110m_admin_0_countries.geojson"
    if not target.exists():
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            resp = client.get(NE_COUNTRIES_GEOJSON_URL)
            resp.raise_for_status()
            target.write_text(resp.text, encoding="utf-8")
    return target


def build_dataset(
    out_dir: Path,
    cache_dir: Path,
    offline_seed: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build countries.json, boundaries.geojson, sites/{ISO3}.geojson, and report.md."""
    out_dir.mkdir(parents=True, exist_ok=True)
    sites_dir = out_dir / "sites"
    sites_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    raw = _load_or_fetch_raw(cache_dir, offline_seed)
    overrides = load_overrides(CURATED_DIR / "category_overrides.yaml")
    teasers = load_teasers(CURATED_DIR / "teasers.yaml")

    boundaries_fc, country_meta = build_boundaries_feature_collection(raw["boundaries_raw"])
    unesco_sites = parse_unesco_records(
        raw.get("unesco_raw", []),
        raw.get("wikidata_by_whs_id", {}),
        overrides,
    )
    notable_sites = merge_and_deduplicate_notable(
        unesco_sites,
        raw.get("notable_raw", []),
        overrides,
    )
    practical_by_iso3: dict[str, dict[str, Any]] = raw.get("practical_by_iso3", {})

    unesco_by_iso3: dict[str, list[dict[str, Any]]] = {iso3: [] for iso3 in country_meta}
    notable_by_iso3: dict[str, list[dict[str, Any]]] = {iso3: [] for iso3 in country_meta}

    for s in unesco_sites:
        for iso3 in s["countries"]:
            if iso3 in unesco_by_iso3:
                unesco_by_iso3[iso3].append(s)

    for s in notable_sites:
        for iso3 in s["countries"]:
            if iso3 in notable_by_iso3:
                notable_by_iso3[iso3].append(s)

    unesco_counts_global = {iso3: len(sites) for iso3, sites in unesco_by_iso3.items()}
    richness_map = compute_global_richness(
        unesco_counts_global,
        notable_by_iso3,
        global_floor=5,
    )

    countries_out: list[dict[str, Any]] = []
    total_shown_sites = 0
    total_with_image = 0
    category_totals = {c: 0 for c in CATEGORIES}

    for iso3 in sorted(country_meta.keys(), key=lambda k: country_meta[k]["name"]):
        meta = country_meta[iso3]
        u_list = unesco_by_iso3.get(iso3, [])
        n_list = notable_by_iso3.get(iso3, [])
        selected = select_country_sites(u_list, n_list)

        features = [_site_to_geojson_feature(idx, s) for idx, s in enumerate(selected)]
        site_fc = {"type": "FeatureCollection", "features": features}
        validate_sites_geojson(site_fc)
        (sites_dir / f"{iso3}.geojson").write_text(
            json.dumps(site_fc, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        by_cat = {c: 0 for c in CATEGORIES}
        coords: list[tuple[float, float]] = []
        for s in selected:
            cat = s["category"]
            by_cat[cat] = by_cat.get(cat, 0) + 1
            category_totals[cat] += 1
            coords.append((float(s["lon"]), float(s["lat"])))
            total_shown_sites += 1
            if s.get("image"):
                total_with_image += 1

        counts_obj = {
            "unesco": sum(1 for s in selected if s["unesco"]),
            "notable": sum(1 for s in selected if not s["unesco"]),
            "byCategory": by_cat,
        }
        raw_score, norm_score = richness_map.get(iso3, (0, 0.0))
        prac = practical_by_iso3.get(iso3) or {}

        climate_raw = prac.get("climate")
        climate_obj = (
            compute_climate_comfort(climate_raw.get("tempC"), climate_raw.get("precipMm"))
            if isinstance(climate_raw, dict)
            else None
        )
        cost_raw = prac.get("cost")
        cost_obj = (
            compute_cost_tier(cost_raw.get("priceLevelRatio"), cost_raw.get("year"))
            if isinstance(cost_raw, dict)
            else None
        )
        safety_raw = prac.get("safety")
        safety_obj = (
            {
                "level": int(safety_raw["level"]),
                "label": str(safety_raw["label"]),
                "url": str(safety_raw["url"]),
                "asOf": str(safety_raw["asOf"]),
            }
            if isinstance(safety_raw, dict) and "level" in safety_raw
            else None
        )
        trad_raw = prac.get("traditions")
        trad_obj = (
            {
                "count": int(trad_raw.get("count") or len(trad_raw.get("examples") or [])),
                "examples": [str(x) for x in (trad_raw.get("examples") or [])[:5]],
            }
            if isinstance(trad_raw, dict)
            else {"count": 0, "examples": []}
        )

        countries_out.append(
            {
                "iso3": iso3,
                "name": meta["name"],
                "aliases": meta["aliases"],
                "teaser": resolve_teaser(iso3, meta["name"], counts_obj, teasers),
                "bbox": meta["bbox"],
                "counts": counts_obj,
                "richness": norm_score,
                "richnessRaw": raw_score,
                "spread": compute_spread(coords),
                "climate": climate_obj,
                "cost": cost_obj,
                "safety": safety_obj,
                "traditions": trad_obj,
            }
        )

    countries_payload = {
        "generatedAt": generated_at or date.today().isoformat(),
        "countries": countries_out,
    }
    validate_countries_payload(countries_payload)

    (out_dir / "countries.json").write_text(
        json.dumps(countries_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "boundaries.geojson").write_text(
        json.dumps(boundaries_fc, ensure_ascii=False),
        encoding="utf-8",
    )

    img_pct = round(100.0 * total_with_image / max(1, total_shown_sites), 1)
    report_lines = [
        "# Heritage Atlas Dataset Validation Report",
        "",
        f"- Generated at: `{countries_payload['generatedAt']}`",
        f"- Total countries: **{len(countries_out)}**",
        f"- Total site placements across countries: **{total_shown_sites}**",
        f"- Sites with Wikimedia Commons images: **{total_with_image}** ({img_pct}%)",
        "",
        "## Category Breakdown",
        "",
    ]
    for cat in CATEGORIES:
        report_lines.append(f"- `{cat}`: {category_totals[cat]}")
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "country_count": len(countries_out),
        "total_sites": total_shown_sites,
        "category_totals": category_totals,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Heritage Atlas static data files.")
    parser.add_argument("--out", type=Path, required=True, help="Output directory (e.g. web/static/data)")
    parser.add_argument(
        "--cache",
        type=Path,
        default=PIPELINE_ROOT / ".cache",
        help="Cache directory for downloaded raw files",
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=DEFAULT_SEED,
        help="Seed dataset JSON path",
    )
    parser.add_argument(
        "--fetch-ne",
        action="store_true",
        help="Download Natural Earth 110m boundaries into cache before building",
    )
    args = parser.parse_args()
    if args.fetch_ne:
        fetch_natural_earth_to_cache(args.cache)
    summary = build_dataset(out_dir=args.out, cache_dir=args.cache, offline_seed=args.seed)
    print(
        f"Built {summary['country_count']} countries and {summary['total_sites']} site placements into {args.out}"
    )


if __name__ == "__main__":
    main()
