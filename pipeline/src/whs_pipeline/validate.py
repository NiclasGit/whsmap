"""Schema validation and text sanitization utilities."""

from __future__ import annotations

import html
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema

CONTRACT_DIR = Path(__file__).resolve().parents[3] / "contract"

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


@lru_cache(maxsize=4)
def _load_schema(filename: str) -> dict[str, Any]:
    path = CONTRACT_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def validate_countries_payload(payload: dict[str, Any]) -> None:
    """Validate a countries.json payload against contract/countries.schema.json."""
    schema = _load_schema("countries.schema.json")
    jsonschema.validate(instance=payload, schema=schema)


def validate_sites_geojson(payload: dict[str, Any]) -> None:
    """Validate a sites/{ISO3}.geojson payload against contract/sites.schema.json."""
    schema = _load_schema("sites.schema.json")
    jsonschema.validate(instance=payload, schema=schema)


def clean_summary(raw_html: str | None, max_sentences: int = 3) -> str:
    """Strip HTML tags/entities and truncate to at most max_sentences sentences."""
    if not raw_html:
        return ""
    stripped = _TAG_RE.sub(" ", raw_html)
    unescaped = html.unescape(stripped).replace("\xa0", " ")
    collapsed = _WS_RE.sub(" ", unescaped).strip()
    if not collapsed:
        return ""
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(collapsed) if s.strip()]
    return " ".join(sentences[:max_sentences])
