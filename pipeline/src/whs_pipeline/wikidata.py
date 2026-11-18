"""Wikidata notable heritage site ingestion and deduplication against UNESCO sites."""

from __future__ import annotations

import json
import math
from pathlib import Path
import re
from typing import Any
import unicodedata
from urllib.parse import quote

import httpx

from whs_pipeline.classify import classify_site
from whs_pipeline.validate import clean_summary

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

_STOPWORDS = {"the", "of", "and", "in", "at", "de", "la", "le", "el", "di", "von", "der"}
_WORD_RE = re.compile(r"[a-z0-9]+")


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Great-circle distance in kilometers between two (lon, lat) points."""
    r = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def _fold_ascii(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower()


def _name_tokens(name: str) -> set[str]:
    folded = _fold_ascii(name)
    tokens: set[str] = set()
    for w in _WORD_RE.findall(folded):
        if w in _STOPWORDS or len(w) <= 2:
            continue
        stem = w[:-1] if len(w) > 4 and w.endswith("s") else w
        tokens.add(stem)
    return tokens


def build_commons_image(
    filename: str | None,
    author: str = "Wikimedia Commons",
    license_name: str = "CC BY-SA",
) -> dict[str, str] | None:
    """Build contract image metadata from a Wikimedia Commons file name."""
    if not filename:
        return None
    clean_file = filename.strip().replace(" ", "_")
    encoded = quote(clean_file)
    return {
        "thumbUrl": f"https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/{encoded}&width=640",
        "author": author,
        "license": license_name,
        "sourceUrl": f"https://commons.wikimedia.org/wiki/File:{encoded}",
    }


def fetch_wikidata_sites(cache_dir: Path) -> list[dict[str, Any]]:
    """Fetch and cache notable heritage landmarks from Wikidata SPARQL."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "wikidata_notable_raw.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    query = """
    SELECT ?item ?itemLabel ?coord ?iso3 ?sitelinks ?instance ?image ?article WHERE {
      VALUES ?instance { wd:Q23413 wd:Q57821 wd:Q839954 wd:Q16560 wd:Q2977 wd:Q44613 wd:Q32815 wd:Q24398318 wd:Q30198 }
      ?item wdt:P31 ?instance ;
            wdt:P625 ?coord ;
            wdt:P17 ?country ;
            wikibase:sitelinks ?sitelinks .
      ?country wdt:P298 ?iso3 .
      FILTER(?sitelinks >= 15)
      OPTIONAL { ?item wdt:P18 ?image . }
      OPTIONAL {
        ?article schema:about ?item ;
                 schema:isPartOf <https://en.wikipedia.org/> .
      }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 5000
    """
    with httpx.Client(timeout=60.0, headers={"Accept": "application/sparql-results+json"}) as client:
        resp = client.get(WIKIDATA_SPARQL_URL, params={"query": query})
        resp.raise_for_status()
        data = resp.json()
        cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data.get("results", {}).get("bindings", [])


def merge_and_deduplicate_notable(
    unesco_sites: list[dict[str, Any]],
    raw_notable: list[dict[str, Any]],
    overrides: dict[str, str],
) -> list[dict[str, Any]]:
    """Filter out notable site candidates that duplicate a UNESCO site by QID or <250m proximity."""
    unesco_qids = {s["wikidataId"] for s in unesco_sites if s.get("wikidataId")}
    by_qid: dict[str, dict[str, Any]] = {}

    for rec in raw_notable:
        qid = str(rec.get("qid") or "").strip()
        name = str(rec.get("name") or "").strip()
        iso3 = str(rec.get("iso3") or "").strip().upper()
        if not qid or not name or not iso3 or qid in unesco_qids:
            continue
        if rec.get("whs_id"):
            continue

        try:
            lon = float(rec["lon"])
            lat = float(rec["lat"])
        except (KeyError, TypeError, ValueError):
            continue

        if qid in by_qid:
            if iso3 not in by_qid[qid]["countries"]:
                by_qid[qid]["countries"].append(iso3)
            continue

        cand_tokens = _name_tokens(name)
        is_spatial_dup = False
        for u in unesco_sites:
            if iso3 not in u["countries"]:
                continue
            dist_km = haversine_km(lon, lat, u["lon"], u["lat"])
            if dist_km <= 0.25:
                u_tokens = _name_tokens(u["name"])
                if not cand_tokens or not u_tokens or (cand_tokens & u_tokens):
                    is_spatial_dup = True
                    break
        if is_spatial_dup:
            continue

        site_id = f"wd-{qid}"
        instance_of = list(rec.get("instance_of") or [])
        category = rec.get("category") or classify_site(site_id, instance_of, None, name, overrides)
        summary = clean_summary(rec.get("summary"))
        image = rec.get("image")
        if isinstance(image, str):
            image = build_commons_image(image)

        by_qid[qid] = {
            "siteId": site_id,
            "name": name,
            "category": category,
            "unesco": False,
            "inDanger": False,
            "yearInscribed": None,
            "fame": int(rec.get("sitelinks") or rec.get("fame") or 0),
            "summary": summary,
            "summarySource": "wikipedia" if summary else None,
            "image": image,
            "wikipediaUrl": rec.get("wikipedia_url") or rec.get("wikipediaUrl"),
            "unescoUrl": None,
            "wikidataId": qid,
            "countries": [iso3],
            "lon": round(lon, 5),
            "lat": round(lat, 5),
        }

    return list(by_qid.values())
