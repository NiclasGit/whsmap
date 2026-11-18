"""Per-country adaptive site selection and fixed-floor global richness calculation."""

from __future__ import annotations

import math
from typing import Any


def fame_level(sitelinks: int) -> int:
    """Bucket Wikipedia sitelink count into 1..4 fameLevel."""
    if sitelinks < 10:
        return 1
    if sitelinks < 30:
        return 2
    if sitelinks < 80:
        return 3
    return 4


def select_country_sites(
    unesco_sites: list[dict[str, Any]],
    notable_candidates: list[dict[str, Any]],
    min_floor: int = 3,
    default_floor: int = 5,
    target_min: int = 15,
    target_max: int = 180,
) -> list[dict[str, Any]]:
    """Select all UNESCO sites plus tuned notable sites for a country, sorted UNESCO first then fame desc."""
    sorted_unesco = sorted(
        unesco_sites,
        key=lambda s: (-int(s.get("fame") or 0), str(s.get("siteId") or "")),
    )

    floor = default_floor
    above_default = [s for s in notable_candidates if int(s.get("fame") or 0) >= default_floor]
    if len(above_default) < target_min:
        while floor > min_floor:
            floor -= 1
            cand = [s for s in notable_candidates if int(s.get("fame") or 0) >= floor]
            if len(cand) >= target_min:
                break
        filtered = [s for s in notable_candidates if int(s.get("fame") or 0) >= floor]
    else:
        filtered = above_default

    sorted_notable = sorted(
        filtered,
        key=lambda s: (-int(s.get("fame") or 0), str(s.get("siteId") or "")),
    )[:target_max]

    combined: list[dict[str, Any]] = []
    for s in sorted_unesco + sorted_notable:
        item = dict(s)
        item["fameLevel"] = fame_level(int(item.get("fame") or 0))
        combined.append(item)
    return combined


def compute_global_richness(
    unesco_by_iso3: dict[str, int],
    notable_candidates_by_iso3: dict[str, list[dict[str, Any]]],
    global_floor: int = 5,
) -> dict[str, tuple[int, float]]:
    """Compute (richnessRaw, richness) using a single fixed global fame floor for all countries."""
    all_iso3 = set(unesco_by_iso3.keys()) | set(notable_candidates_by_iso3.keys())
    raw_by_iso3: dict[str, int] = {}

    for iso3 in all_iso3:
        u_count = int(unesco_by_iso3.get(iso3, 0))
        notables = notable_candidates_by_iso3.get(iso3) or []
        n_count = sum(1 for s in notables if int(s.get("fame") or 0) >= global_floor)
        raw_by_iso3[iso3] = 3 * u_count + n_count

    max_raw = max(raw_by_iso3.values(), default=0)
    out: dict[str, tuple[int, float]] = {}
    for iso3, raw in raw_by_iso3.items():
        if max_raw <= 0 or raw <= 0:
            out[iso3] = (0, 0.0)
        else:
            out[iso3] = (raw, round(math.sqrt(raw / max_raw), 4))
    return out
