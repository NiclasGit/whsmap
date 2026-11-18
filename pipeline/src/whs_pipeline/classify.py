"""Site category classification from overrides, Wikidata QIDs, UNESCO type, and keywords."""

from __future__ import annotations

from pathlib import Path

import yaml

from whs_pipeline.types import CATEGORIES

_QID_TO_CATEGORY: dict[str, str] = {
    # castles & forts
    "Q23413": "castles",
    "Q57821": "castles",
    "Q1785071": "castles",
    "Q744913": "castles",
    # sacred
    "Q16970": "sacred",
    "Q2977": "sacred",
    "Q32815": "sacred",
    "Q44613": "sacred",
    "Q24398318": "sacred",
    "Q44539": "sacred",
    "Q108325": "sacred",
    "Q697295": "sacred",
    # ancient / archaeological
    "Q839954": "ancient",
    "Q109607": "ancient",
    "Q15661340": "ancient",
    "Q381885": "ancient",
    "Q14560": "ancient",
    # palaces & architecture
    "Q16560": "palaces",
    "Q1802963": "palaces",
    "Q3950": "palaces",
    "Q41176": "palaces",
    # historic towns
    "Q30198": "towns",
    "Q15284": "towns",
    "Q515": "towns",
    "Q676050": "towns",
    # modern / industrial
    "Q16695773": "modern",
    "Q4989906": "modern",
    "Q12280": "modern",
    "Q820477": "modern",
    # landscapes
    "Q1129474": "landscapes",
    "Q1107656": "landscapes",
    "Q22746": "landscapes",
    # natural
    "Q46169": "natural",
    "Q8502": "natural",
    "Q179049": "natural",
}

_KEYWORD_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("castles", ("castle", "fortress", "citadel", "fort ", "fortifications", "alcázar", "kremlin", "kasbah")),
    (
        "sacred",
        (
            "cathedral",
            "abbey",
            "monastery",
            "church",
            "mosque",
            "temple",
            "shrine",
            "basilica",
            "synagogue",
            "pagoda",
            "stupa",
            "sanctuary",
        ),
    ),
    (
        "towns",
        (
            "historic centre",
            "historic center",
            "old town",
            "old city",
            "historic city",
            "historic town",
            "medina of",
            "historic quarter",
        ),
    ),
    ("palaces", ("palace", "residence", "villa ", "château", "royal site", "opera house", "palladian")),
    (
        "modern",
        (
            "industrial",
            "mining",
            "mine ",
            "ironbridge",
            "railway",
            "canal",
            "factory",
            "bauhaus",
            "modernist",
            "ironworks",
        ),
    ),
    ("landscapes", ("cultural landscape", "garden", "vineyard", "rice terraces", "agave", "coffee cultural")),
    (
        "ancient",
        (
            "archaeological",
            "ruins",
            "ancient",
            "necropolis",
            "megalithic",
            "prehistoric",
            "rock art",
            "petroglyph",
            "pyramid",
            "tumuli",
            "acropolis",
        ),
    ),
    ("natural", ("national park", "nature reserve", "biosphere", "glacier", "volcano", "islands", "reef", "canyon")),
]


def load_overrides(path: Path) -> dict[str, str]:
    """Load and validate siteId -> category overrides from YAML."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    valid = set(CATEGORIES)
    out: dict[str, str] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str) and v in valid:
            out[k] = v
    return out


def classify_site(
    site_id: str,
    instance_of_qids: list[str],
    unesco_type: str | None,
    name: str,
    overrides: dict[str, str],
) -> str:
    """Return one of the 8 contract categories for a site."""
    if site_id in overrides and overrides[site_id] in CATEGORIES:
        return overrides[site_id]

    if unesco_type and unesco_type.lower() == "natural":
        return "natural"

    for qid in instance_of_qids:
        mapped = _QID_TO_CATEGORY.get(qid)
        if mapped:
            return mapped

    lower_name = name.lower()
    for category, keywords in _KEYWORD_RULES:
        if any(kw in lower_name for kw in keywords):
            return category

    if unesco_type and unesco_type.lower() == "mixed":
        return "natural"

    return "ancient"
