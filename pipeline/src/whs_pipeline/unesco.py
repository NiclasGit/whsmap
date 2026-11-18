"""UNESCO World Heritage Sites ingestion and ISO2->ISO3 country mapping."""

from __future__ import annotations

from typing import Any

from whs_pipeline.classify import classify_site
from whs_pipeline.validate import clean_summary

ISO2_TO_ISO3: dict[str, str] = {
    "af": "AFG", "al": "ALB", "dz": "DZA", "ad": "AND", "ao": "AGO", "ag": "ATG", "ar": "ARG",
    "am": "ARM", "au": "AUS", "at": "AUT", "az": "AZE", "bs": "BHS", "bh": "BHR", "bd": "BGD",
    "bb": "BRB", "by": "BLR", "be": "BEL", "bz": "BLZ", "bj": "BEN", "bt": "BTN", "bo": "BOL",
    "ba": "BIH", "bw": "BWA", "br": "BRA", "bn": "BRN", "bg": "BGR", "bf": "BFA", "bi": "BDI",
    "cv": "CPV", "kh": "KHM", "cm": "CMR", "ca": "CAN", "cf": "CAF", "td": "TCD", "cl": "CHL",
    "cn": "CHN", "co": "COL", "km": "COM", "cg": "COG", "cd": "COD", "cr": "CRI", "ci": "CIV",
    "hr": "HRV", "cu": "CUB", "cy": "CYP", "cz": "CZE", "dk": "DNK", "dj": "DJI", "dm": "DMA",
    "do": "DOM", "ec": "ECU", "eg": "EGY", "sv": "SLV", "gq": "GNQ", "er": "ERI", "ee": "EST",
    "sz": "SWZ", "et": "ETH", "fj": "FJI", "fi": "FIN", "fr": "FRA", "ga": "GAB", "gm": "GMB",
    "ge": "GEO", "de": "DEU", "gh": "GHA", "gr": "GRC", "gd": "GRD", "gt": "GTM", "gn": "GIN",
    "gw": "GNB", "gy": "GUY", "ht": "HTI", "va": "VAT", "hn": "HND", "hu": "HUN", "is": "ISL",
    "in": "IND", "id": "IDN", "ir": "IRN", "iq": "IRQ", "ie": "IRL", "il": "ISR", "it": "ITA",
    "jm": "JAM", "jp": "JPN", "jo": "JOR", "kz": "KAZ", "ke": "KEN", "ki": "KIR", "kp": "PRK",
    "kr": "KOR", "kw": "KWT", "kg": "KGZ", "la": "LAO", "lv": "LVA", "lb": "LBN", "ls": "LSO",
    "lr": "LBR", "ly": "LBY", "li": "LIE", "lt": "LTU", "lu": "LUX", "mg": "MDG", "mw": "MWI",
    "my": "MYS", "mv": "MDV", "ml": "MLI", "mt": "MLT", "mh": "MHL", "mr": "MRT", "mu": "MUS",
    "mx": "MEX", "fm": "FSM", "md": "MDA", "mc": "MCO", "mn": "MNG", "me": "MNE", "ma": "MAR",
    "mz": "MOZ", "mm": "MMR", "na": "NAM", "nr": "NRU", "np": "NPL", "nl": "NLD", "nz": "NZL",
    "ni": "NIC", "ne": "NER", "ng": "NGA", "mk": "MKD", "no": "NOR", "om": "OMN", "pk": "PAK",
    "pw": "PLW", "ps": "PSE", "pa": "PAN", "pg": "PNG", "py": "PRY", "pe": "PER", "ph": "PHL",
    "pl": "POL", "pt": "PRT", "qa": "QAT", "ro": "ROU", "ru": "RUS", "rw": "RWA", "kn": "KNA",
    "lc": "LCA", "vc": "VCT", "ws": "WSM", "sm": "SMR", "st": "STP", "sa": "SAU", "sn": "SEN",
    "rs": "SRB", "sc": "SYC", "sl": "SLE", "sg": "SGP", "sk": "SVK", "si": "SVN", "sb": "SLB",
    "so": "SOM", "za": "ZAF", "ss": "SSD", "es": "ESP", "lk": "LKA", "sd": "SDN", "sr": "SUR",
    "se": "SWE", "ch": "CHE", "sy": "SYR", "tj": "TJK", "tz": "TZA", "th": "THA", "tl": "TLS",
    "tg": "TGO", "to": "TON", "tt": "TTO", "tn": "TUN", "tr": "TUR", "tm": "TKM", "tv": "TUV",
    "ug": "UGA", "ua": "UKR", "ae": "ARE", "gb": "GBR", "uk": "GBR", "us": "USA", "uy": "URY",
    "uz": "UZB", "vu": "VUT", "ve": "VEN", "vn": "VNM", "ye": "YEM", "zm": "ZMB", "zw": "ZWE",
}


def resolve_countries(iso_field: str | list[str]) -> list[str]:
    """Resolve comma-separated ISO2 or ISO3 codes into deduplicated uppercase ISO3 codes."""
    tokens = (
        [t.strip() for t in iso_field.split(",") if t.strip()]
        if isinstance(iso_field, str)
        else [str(t).strip() for t in iso_field if str(t).strip()]
    )
    out: list[str] = []
    for tok in tokens:
        low = tok.lower()
        iso3 = ISO2_TO_ISO3.get(low) or (tok.upper() if len(tok) == 3 and tok.isalpha() else None)
        if iso3 and iso3 not in out:
            out.append(iso3)
    return out


def parse_unesco_records(
    raw_records: list[dict[str, Any]],
    wikidata_by_whs_id: dict[str, dict[str, Any]],
    overrides: dict[str, str],
) -> list[dict[str, Any]]:
    """Parse raw UNESCO WHS records and enrich with Wikidata metadata."""
    sites: list[dict[str, Any]] = []
    for rec in raw_records:
        whs_id = str(rec.get("id_no") or "").strip()
        name = str(rec.get("name_en") or rec.get("name") or "").strip()
        if not whs_id or not name:
            continue

        countries = resolve_countries(rec.get("iso_code") or rec.get("countries") or "")
        if not countries:
            continue

        try:
            lon = float(rec["longitude"])
            lat = float(rec["latitude"])
        except (KeyError, TypeError, ValueError):
            continue

        site_id = f"whs-{whs_id}"
        wd = wikidata_by_whs_id.get(whs_id) or {}
        instance_of = list(wd.get("instance_of") or [])
        unesco_type = str(rec.get("category") or "Cultural")
        category = classify_site(site_id, instance_of, unesco_type, name, overrides)

        summary = clean_summary(rec.get("short_description_en") or rec.get("summary"))
        summary_source = "unesco" if summary else (wd.get("summary_source") if wd.get("summary") else None)
        if not summary and wd.get("summary"):
            summary = clean_summary(wd["summary"])

        year_raw = rec.get("date_inscribed") or rec.get("yearInscribed")
        year_inscribed = int(year_raw) if year_raw is not None else None

        sites.append(
            {
                "siteId": site_id,
                "name": name,
                "category": category,
                "unesco": True,
                "inDanger": bool(rec.get("danger")),
                "yearInscribed": year_inscribed,
                "fame": int(wd.get("sitelinks") or rec.get("fame") or 0),
                "summary": summary,
                "summarySource": summary_source,
                "image": wd.get("image") or rec.get("image"),
                "wikipediaUrl": wd.get("wikipedia_url") or rec.get("wikipediaUrl"),
                "unescoUrl": f"https://whc.unesco.org/en/list/{whs_id}",
                "wikidataId": wd.get("qid") or rec.get("wikidataId"),
                "countries": countries,
                "lon": round(lon, 5),
                "lat": round(lat, 5),
            }
        )
    return sites
