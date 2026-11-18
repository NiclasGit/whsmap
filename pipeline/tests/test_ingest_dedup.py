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


def test_unesco_string_danger_false_and_empty_year_and_duplicate_id_merging():
    raw = [
        {
            "id_no": "91",
            "name_en": "Historic Centre of Rome",
            "short_description_en": "Ancient capital.",
            "category": "Cultural",
            "danger": "0",
            "date_inscribed": "",
            "longitude": 12.4922,
            "latitude": 41.8902,
            "iso_code": "it",
        },
        {
            "id_no": "91",
            "name_en": "Historic Centre of Rome",
            "short_description_en": "Ancient capital.",
            "category": "Cultural",
            "danger": "false",
            "date_inscribed": "1980",
            "longitude": 12.4922,
            "latitude": 41.8902,
            "iso_code": "va",
        },
    ]
    sites = parse_unesco_records(raw, {}, {})
    assert len(sites) == 1
    assert sites[0]["inDanger"] is False
    assert sites[0]["yearInscribed"] == 1980
    assert sites[0]["countries"] == ["ITA", "VAT"]


def test_spatial_dedup_folds_unicode_diacritics_and_merges_transboundary_notable():
    unesco = [
        {
            "siteId": "whs-948",
            "name": "Hoi An Ancient Town",
            "wikidataId": "Q36160",
            "lon": 108.3280,
            "lat": 15.8777,
            "countries": ["VNM"],
        }
    ]
    notable_raw = [
        # Diacritic name within 250m of Hoi An Ancient Town -> must be deduplicated
        {
            "qid": "Q888888",
            "name": "Hội An",
            "lon": 108.3285,
            "lat": 15.8780,
            "sitelinks": 40,
            "iso3": "VNM",
            "instance_of": ["Q30198"],
        },
        # Transboundary notable site appearing under two countries -> must merge countries
        {
            "qid": "Q777777",
            "name": "Matterhorn",
            "lon": 7.6586,
            "lat": 45.9764,
            "sitelinks": 95,
            "iso3": "CHE",
            "instance_of": ["Q8502"],
        },
        {
            "qid": "Q777777",
            "name": "Matterhorn",
            "lon": 7.6586,
            "lat": 45.9764,
            "sitelinks": 95,
            "iso3": "ITA",
            "instance_of": ["Q8502"],
        },
    ]
    kept = merge_and_deduplicate_notable(unesco, notable_raw, {})
    assert len(kept) == 1
    assert kept[0]["siteId"] == "wd-Q777777"
    assert kept[0]["countries"] == ["CHE", "ITA"]
