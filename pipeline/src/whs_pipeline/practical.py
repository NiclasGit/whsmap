"""Practical destination metrics (spread, climate comfort, cost tier, safety, teasers)."""

from __future__ import annotations

from pathlib import Path
import statistics
from typing import Any

import yaml

from whs_pipeline.wikidata import haversine_km

_CATEGORY_PHRASES: dict[str, str] = {
    "ancient": "ancient ruins and archaeological sites",
    "sacred": "sacred temples, churches and monasteries",
    "castles": "fortresses and castles",
    "towns": "historic old towns",
    "palaces": "palaces and monumental architecture",
    "landscapes": "cultural landscapes",
    "modern": "industrial and modern heritage",
    "natural": "natural wonders",
}


def compute_spread(coords: list[tuple[float, float]]) -> dict[str, Any] | None:
    """Compute pairwise median distance (km) and spread level for a country's sites."""
    if len(coords) < 2:
        return None
    sample = coords[:80]
    dists: list[float] = []
    for i in range(len(sample)):
        lon1, lat1 = sample[i]
        for j in range(i + 1, len(sample)):
            lon2, lat2 = sample[j]
            dists.append(haversine_km(lon1, lat1, lon2, lat2))
    if not dists:
        return None
    median_km = round(statistics.median(dists))
    if median_km < 150:
        level = "compact"
    elif median_km <= 600:
        level = "moderate"
    else:
        level = "spread"
    return {"level": level, "medianKm": median_km}


def compute_climate_comfort(
    temp_c: list[float] | None,
    precip_mm: list[float] | None,
) -> dict[str, Any] | None:
    """Determine monthly comfort booleans from 12 monthly mean temperatures (°C) and precipitation (mm)."""
    if not temp_c or not precip_mm or len(temp_c) != 12 or len(precip_mm) != 12:
        return None
    t_clean = [round(float(x), 1) for x in temp_c]
    p_clean = [max(0.0, round(float(x), 1)) for x in precip_mm]
    comfortable = [13.0 <= t <= 28.0 and p <= 130.0 for t, p in zip(t_clean, p_clean)]
    if not any(comfortable):
        ranked = sorted(
            range(12),
            key=lambda m: (abs(t_clean[m] - 20.0) + p_clean[m] / 40.0),
        )
        for idx in ranked[:3]:
            comfortable[idx] = True
    return {
        "tempC": t_clean,
        "precipMm": p_clean,
        "comfortable": comfortable,
    }


def compute_cost_tier(price_level_ratio: float | None, year: int | None) -> dict[str, Any] | None:
    """Map World Bank PPP price level ratio (USA=1.0) into a 1..5 cost tier."""
    if price_level_ratio is None or year is None or price_level_ratio <= 0:
        return None
    r = round(float(price_level_ratio), 3)
    if r < 0.40:
        tier = 1
    elif r < 0.58:
        tier = 2
    elif r < 0.78:
        tier = 3
    elif r < 1.00:
        tier = 4
    else:
        tier = 5
    return {"tier": tier, "priceLevelRatio": r, "year": int(year)}


def load_teasers(path: Path) -> dict[str, str]:
    """Load ISO3 -> 1-sentence teaser dictionary from YAML."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        str(k).upper(): str(v).strip()
        for k, v in data.items()
        if isinstance(k, str) and isinstance(v, str) and v.strip()
    }


def resolve_teaser(
    iso3: str,
    name: str,
    counts: dict[str, Any],
    curated: dict[str, str],
) -> str:
    """Return curated teaser if available, else generate a factual 1-sentence overview."""
    iso_up = iso3.upper()
    if iso_up in curated and curated[iso_up]:
        return curated[iso_up]

    unesco_n = int(counts.get("unesco") or 0)
    notable_n = int(counts.get("notable") or 0)
    by_cat: dict[str, int] = counts.get("byCategory") or {}
    top_cats = [
        _CATEGORY_PHRASES.get(cat, cat)
        for cat, cnt in sorted(by_cat.items(), key=lambda kv: (-int(kv[1]), kv[0]))
        if int(cnt) > 0
    ][:2]

    if unesco_n > 0 and top_cats:
        joined = " and ".join(top_cats)
        site_word = "World Heritage Site" if unesco_n == 1 else "World Heritage Sites"
        return f"Home to {unesco_n} {site_word} and {notable_n} notable landmarks, highlighted by {joined}."
    if unesco_n > 0:
        site_word = "World Heritage Site" if unesco_n == 1 else "World Heritage Sites"
        return f"Explore {unesco_n} {site_word} across {name}."
    if notable_n > 0 and top_cats:
        return f"Explore {notable_n} notable heritage landmarks in {name}, including {' and '.join(top_cats)}."
    return f"Discover the cultural and historical heritage of {name}."
