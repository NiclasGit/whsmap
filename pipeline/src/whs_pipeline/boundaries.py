"""Country boundary loading and main-territory bounding box calculation."""

from __future__ import annotations

import math
from typing import Any

import shapely
import numpy as np
from shapely.geometry import MultiPolygon, Polygon, shape


def _shift_lon_0_360(poly: Polygon) -> Polygon:
    return shapely.transform(poly, lambda coords: np.column_stack([np.where(coords[:, 0] < 0, coords[:, 0] + 360.0, coords[:, 0]), coords[:, 1]]))


def _approx_polygon_distance_km(a: Polygon, b: Polygon) -> float:
    """Approximate minimum distance in km between two lon/lat polygons, antimeridian-aware."""
    mid_lat = math.radians((a.centroid.y + b.centroid.y) / 2.0)
    km_per_deg_lat = 111.132
    km_per_deg_lon = max(10.0, 111.320 * math.cos(mid_lat))

    def _scaled(p: Polygon) -> Polygon:
        return shapely.transform(p, lambda coords: np.column_stack([coords[:, 0] * km_per_deg_lon, coords[:, 1] * km_per_deg_lat]))

    dist_std = _scaled(a).distance(_scaled(b))
    dist_wrapped = _scaled(_shift_lon_0_360(a)).distance(_scaled(_shift_lon_0_360(b)))
    return min(dist_std, dist_wrapped)


def compute_main_bbox(geom: dict[str, Any], cluster_km: float = 500.0) -> list[float]:
    """Compute [west, south, east, north] for the largest polygon + polygons within cluster_km."""
    shp = shape(geom)
    if isinstance(shp, Polygon):
        polys = [shp]
    elif isinstance(shp, MultiPolygon):
        polys = list(shp.geoms)
    else:
        polys = [p for p in getattr(shp, "geoms", []) if isinstance(p, Polygon)]

    if not polys:
        return [-180.0, -90.0, 180.0, 90.0]

    main_poly = max(polys, key=lambda p: p.area)
    kept = [
        p
        for p in polys
        if p is main_poly or _approx_polygon_distance_km(main_poly, p) <= cluster_km
    ]

    min_x = min(p.bounds[0] for p in kept)
    min_y = min(p.bounds[1] for p in kept)
    max_x = max(p.bounds[2] for p in kept)
    max_y = max(p.bounds[3] for p in kept)
    span_std = max_x - min_x

    shifted_bounds = [_shift_lon_0_360(p).bounds for p in kept]
    min_wx = min(b[0] for b in shifted_bounds)
    max_wx = max(b[2] for b in shifted_bounds)
    span_wrapped = max_wx - min_wx

    if span_wrapped + 1e-6 < span_std and max_wx > 180.0 >= min_wx:
        west = round(min_wx, 4)
        east = round(max_wx - 360.0 if max_wx > 180.0 else max_wx, 4)
    else:
        west = round(min_x, 4)
        east = round(max_x, 4)

    return [west, round(min_y, 4), east, round(max_y, 4)]


def _extract_iso3(props: dict[str, Any]) -> str | None:
    for key in ("iso3", "ISO_A3", "ADM0_A3", "ISO_A3_EH", "WB_A3"):
        val = props.get(key)
        if isinstance(val, str) and len(val) == 3 and val.isalpha() and val != "-99":
            return val.upper()
    return None


def build_boundaries_feature_collection(
    raw_ne_geojson: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Normalize raw Natural Earth admin-0 GeoJSON into boundaries.geojson and country metadata."""
    features_out: list[dict[str, Any]] = []
    meta_by_iso3: dict[str, dict[str, Any]] = {}

    raw_features = raw_ne_geojson.get("features", [])
    sorted_raw = sorted(
        raw_features,
        key=lambda f: str(
            f.get("properties", {}).get("name")
            or f.get("properties", {}).get("NAME")
            or ""
        ),
    )

    for feat in sorted_raw:
        props = feat.get("properties") or {}
        iso3 = _extract_iso3(props)
        name = str(props.get("name") or props.get("NAME") or props.get("ADMIN") or "").strip()
        geom = feat.get("geometry")
        if not iso3 or not name or not geom or iso3 == "ATA" or name == "Antarctica":
            continue
        if iso3 in meta_by_iso3:
            continue

        aliases: list[str] = []
        for k in ("FORMAL_EN", "NAME_LONG", "BRK_NAME"):
            v = props.get(k)
            if isinstance(v, str) and v.strip() and v.strip() != name and v.strip() not in aliases:
                aliases.append(v.strip())
        if isinstance(props.get("aliases"), list):
            for a in props["aliases"]:
                if isinstance(a, str) and a.strip() and a.strip() not in aliases:
                    aliases.append(a.strip())

        idx = len(features_out)
        features_out.append(
            {
                "type": "Feature",
                "id": idx,
                "properties": {"iso3": iso3, "name": name},
                "geometry": geom,
            }
        )
        meta_by_iso3[iso3] = {
            "iso3": iso3,
            "name": name,
            "aliases": aliases,
            "bbox": compute_main_bbox(geom),
        }

    return {"type": "FeatureCollection", "features": features_out}, meta_by_iso3
