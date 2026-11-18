from whs_pipeline.classify import classify_site


def test_override_wins_over_everything():
    assert classify_site("whs-91", ["Q23413"], "Cultural", "Historic Centre of Rome", {"whs-91": "towns"}) == "towns"


def test_wikidata_qid_mapping_resolves_categories():
    assert classify_site("wd-Q1", ["Q23413"], None, "Burg Eltz", {}) == "castles"
    assert classify_site("wd-Q2", ["Q44613"], None, "Monastery", {}) == "sacred"
    assert classify_site("wd-Q3", ["Q839954"], None, "Pompeii", {}) == "ancient"


def test_unesco_natural_and_keyword_fallbacks():
    assert classify_site("whs-2", [], "Natural", "Serengeti National Park", {}) == "natural"
    assert classify_site("whs-3", [], "Cultural", "Cathedral of Chartres", {}) == "sacred"
    assert classify_site("whs-4", [], "Cultural", "Palace and Park of Versailles", {}) == "palaces"
