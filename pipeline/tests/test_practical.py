from whs_pipeline.practical import (
    compute_climate_comfort,
    compute_cost_tier,
    compute_spread,
    resolve_teaser,
)


def test_compute_spread_classifications():
    assert compute_spread([(12.5, 41.9)]) is None
    compact = compute_spread([(14.4, 35.9), (14.5, 35.85), (14.35, 35.92)])
    assert compact["level"] == "compact"
    spread = compute_spread([(-70.0, -15.0), (-120.0, 45.0), (10.0, 50.0)])
    assert spread["level"] == "spread"


def test_compute_climate_comfort_marks_pleasant_dry_months():
    temps = [5.0, 7.0, 12.0, 16.0, 21.0, 26.0, 31.0, 30.0, 24.0, 18.0, 11.0, 6.0]
    precip = [80, 70, 60, 50, 40, 20, 10, 15, 45, 90, 110, 95]
    c = compute_climate_comfort(temps, precip)
    assert len(c["comfortable"]) == 12
    # May (21C, 40mm) is comfortable; Jan (5C) and Jul (31C) are not
    assert c["comfortable"][4] is True
    assert c["comfortable"][0] is False
    assert c["comfortable"][6] is False


def test_compute_cost_tier_maps_ppp_ratio_to_1_to_5():
    assert compute_cost_tier(None, None) is None
    assert compute_cost_tier(0.30, 2023)["tier"] == 1
    assert compute_cost_tier(0.65, 2023)["tier"] == 3
    assert compute_cost_tier(1.25, 2023)["tier"] == 5


def test_resolve_teaser_uses_curated_then_fallback():
    counts = {"unesco": 3, "notable": 12, "byCategory": {"ancient": 8, "sacred": 7}}
    assert resolve_teaser("ITA", "Italy", counts, {"ITA": "Curated line."}) == "Curated line."
    fallback = resolve_teaser("XYZ", "Xyland", counts, {})
    assert "3 World Heritage Sites" in fallback
