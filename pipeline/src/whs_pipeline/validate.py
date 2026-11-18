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

_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_BLOCK_TAG_RE = re.compile(r"</?(?:p|div|br|li|ul|ol|h[1-6]|tr|blockquote)\b[^>]*>", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>|<[a-zA-Z/][^>]*$")
_WS_RE = re.compile(r"\s+")
_SPACE_BEFORE_PUNCT_RE = re.compile(r"\s+([,.;:!?])")
_ABBREV_RE = re.compile(
    r"\b(sq|st|mr|mrs|ms|dr|prof|no|c|ca|vs|etc|fig|vol|approx|mt|ft|km|e\.g|i\.e)\.",
    re.IGNORECASE,
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_PLACEHOLDER_DOT = "\u2024"


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
    text = raw_html
    for _ in range(2):
        text = html.unescape(text)
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _BLOCK_TAG_RE.sub(" ", text)
    text = _TAG_RE.sub("", text)
    text = text.replace("\xa0", " ")
    text = _WS_RE.sub(" ", text).strip()
    text = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", text)
    if not text:
        return ""

    protected = _ABBREV_RE.sub(lambda m: m.group(1) + _PLACEHOLDER_DOT, text)
    sentences = [
        s.replace(_PLACEHOLDER_DOT, ".").strip()
        for s in _SENTENCE_SPLIT_RE.split(protected)
        if s.strip()
    ]
    return " ".join(sentences[:max_sentences])
