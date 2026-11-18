from whs_pipeline.unesco import parse_unesco_records
from whs_pipeline.wikidata import merge_and_deduplicate_notable


def test_transboundary_unesco_site_preserves_all_iso3_codes():
    raw = [
        {
            "id_no": "91",
            "name_en": "Historic Centre of Rome, the Properties of the Holy See",
            "short_description_en": "<p>Founded by Romulus and Remus.</p>",
            "category": "Cultural",
            "danger": 0,
            "date_inscribed": 1980,
            "longitude": 12.4922,
            "latitude": 41.8902,
            "iso_code": "it,va",
        }
    ]
    wd = {
        "91": {
            "qid": "Q152874",
            "sitelinks": 112,
            "instance_of": ["Q30198"],
            "image": None,
            "wikipedia_url": "https://en.wikipedia.org/wiki/Historic_Centre_of_Rome",
        }
    }
    sites = parse_unesco_records(raw, wd, {"whs-91": "towns"})
    assert len(sites) == 1
    assert sites[0]["siteId"] == "whs-91"
    assert sites[0]["countries"] == ["ITA", "VAT"]
    assert sites[0]["summary"] == "Founded by Romulus and Remus."


def test_deduplicate_drops_notable_matching_unesco_by_qid_or_proximity():
    unesco = [
        {
            "siteId": "whs-91",
            "name": "Colosseum",
            "wikidataId": "Q10285",
            "lon": 12.4922,
            "lat": 41.8902,
            "countries": ["ITA"],
        }
    ]
    notable_raw = [
        # Duplicate by Wikidata QID
        {
            "qid": "Q10285",
            "name": "Colosseum",
            "lon": 12.4922,
            "lat": 41.8902,
            "sitelinks": 150,
            "iso3": "ITA",
            "instance_of": ["Q839954"],
        },
        # Duplicate by <250m proximity + matching normalized name
        {
            "qid": "Q99999",
            "name": "The Colosseum",
            "lon": 12.4925,
            "lat": 41.8904,
            "sitelinks": 45,
            "iso3": "ITA",
            "instance_of": ["Q839954"],
        },
        # Distinct site
        {
            "qid": "Q47891",
            "name": "Pantheon",
            "lon": 12.4769,
            "lat": 41.8986,
            "sitelinks": 120,
            "iso3": "ITA",
            "instance_of": ["Q44539"],
        },
    ]
    kept = merge_and_deduplicate_notable(unesco, notable_raw, {})
    assert [s["siteId"] for s in kept] == ["wd-Q47891"]
