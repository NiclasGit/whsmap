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


def test_clean_summary_handles_encoded_tags_punctuation_spacing_and_abbreviations():
    raw = "&lt;p&gt;Stretching over 400 sq. km near St. Peter, &lt;b&gt;Angkor&lt;/b&gt; is famous. Built c. 1150 AD, it has No. 1 temples. Third sentence here. Fourth dropped.&lt;/p&gt;"
    cleaned = clean_summary(raw, max_sentences=3)
    assert cleaned == (
        "Stretching over 400 sq. km near St. Peter, Angkor is famous. "
        "Built c. 1150 AD, it has No. 1 temples. "
        "Third sentence here."
    )


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
                    "byCategory": {
                        c: 0
                        for c in (
                            "ancient",
                            "sacred",
                            "castles",
                            "towns",
                            "palaces",
                            "landscapes",
                            "modern",
                            "natural",
                        )
                    },
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
