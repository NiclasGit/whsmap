import json
from pathlib import Path
from whs_pipeline.build import build_dataset
from whs_pipeline.validate import validate_countries_payload, validate_sites_geojson


def test_build_dataset_produces_schema_valid_outputs_and_report(tmp_path: Path):
    seed_path = Path(__file__).parent.parent / "fixtures" / "seed_dataset.json"
    summary = build_dataset(out_dir=tmp_path, cache_dir=tmp_path / "cache", offline_seed=seed_path)

    countries_file = tmp_path / "countries.json"
    boundaries_file = tmp_path / "boundaries.geojson"
    report_file = tmp_path / "report.md"

    assert countries_file.exists() and boundaries_file.exists() and report_file.exists()
    countries_payload = json.loads(countries_file.read_text(encoding="utf-8"))
    validate_countries_payload(countries_payload)

    assert summary["country_count"] >= 150
    for c in countries_payload["countries"]:
        site_file = tmp_path / "sites" / f"{c['iso3']}.geojson"
        assert site_file.exists()
        site_payload = json.loads(site_file.read_text(encoding="utf-8"))
        validate_sites_geojson(site_payload)
        for feat in site_payload["features"]:
            # Ensure no synthetic numbered placeholder names exist
            assert not feat["properties"]["name"].endswith((" 1", " 2", " 3", " 4", " 5"))
