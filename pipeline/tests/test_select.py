from whs_pipeline.select import compute_global_richness, fame_level, select_country_sites


def test_fame_level_buckets():
    assert fame_level(0) == 1
    assert fame_level(9) == 1
    assert fame_level(10) == 2
    assert fame_level(29) == 2
    assert fame_level(30) == 3
    assert fame_level(80) == 4


def test_select_country_sites_tunes_threshold_and_sorts_unesco_first():
    unesco = [{"siteId": "whs-1", "unesco": True, "fame": 12}]
    # Sparse country: only 4 notable sites with fame 3..4; threshold lowers to min_floor=3
    sparse_notable = [{"siteId": f"wd-{i}", "unesco": False, "fame": 3 + (i % 2)} for i in range(4)]
    selected = select_country_sites(
        unesco, sparse_notable, min_floor=3, default_floor=5, target_min=10, target_max=50
    )
    assert selected[0]["siteId"] == "whs-1"
    assert len(selected) == 5

    # Dense country: 100 notable sites with varying fame; threshold raises so <= target_max are kept
    dense_notable = [{"siteId": f"wd-{i}", "unesco": False, "fame": i} for i in range(1, 101)]
    dense_selected = select_country_sites(
        [], dense_notable, min_floor=3, default_floor=5, target_min=10, target_max=25
    )
    assert len(dense_selected) <= 25
    assert dense_selected[0]["fame"] >= dense_selected[-1]["fame"] >= 5


def test_global_richness_uses_fixed_global_floor_not_tuned_counts():
    unesco_counts = {"ITA": 60, "IRL": 2, "NRU": 0}
    notable_by_iso3 = {
        "ITA": [{"fame": 10}] * 200 + [{"fame": 3}] * 500,
        "IRL": [{"fame": 10}] * 15 + [{"fame": 3}] * 40,
        "NRU": [],
    }
    res = compute_global_richness(unesco_counts, notable_by_iso3, global_floor=5)
    assert res["ITA"][0] == 3 * 60 + 200
    assert res["ITA"][1] == 1.0
    assert res["IRL"][0] == 3 * 2 + 15
    assert 0.0 < res["IRL"][1] < 1.0
    assert res["NRU"] == (0, 0.0)
