from whs_pipeline.boundaries import build_boundaries_feature_collection, compute_main_bbox


def test_compute_main_bbox_ignores_distant_overseas_polygon():
    # Metropolitan France polygon near (2E, 46N) + small French Guiana polygon near (-53W, 4N)
    geom = {
        "type": "MultiPolygon",
        "coordinates": [
            [[[-5.0, 42.0], [8.0, 42.0], [8.0, 51.0], [-5.0, 51.0], [-5.0, 42.0]]],
            [[[-54.0, 2.0], [-51.0, 2.0], [-51.0, 6.0], [-54.0, 6.0], [-54.0, 2.0]]],
        ],
    }
    bbox = compute_main_bbox(geom, cluster_km=500.0)
    assert bbox == [-5.0, 42.0, 8.0, 51.0]


def test_compute_main_bbox_handles_antimeridian_crossing():
    # Two islands straddling 180°: one at 178..179.9E, one at -179.9..-178W
    geom = {
        "type": "MultiPolygon",
        "coordinates": [
            [[[178.0, -18.0], [179.9, -18.0], [179.9, -16.0], [178.0, -16.0], [178.0, -18.0]]],
            [[[-179.9, -18.0], [-178.0, -18.0], [-178.0, -16.0], [-179.9, -16.0], [-179.9, -18.0]]],
        ],
    }
    west, south, east, north = compute_main_bbox(geom, cluster_km=500.0)
    assert west == 178.0 and east == -178.0
    assert west > east


def test_build_boundaries_assigns_sequential_ids_and_extracts_meta():
    raw = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ISO_A3": "ITA", "NAME": "Italy", "FORMAL_EN": "Italian Republic"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.6, 35.5], [18.5, 35.5], [18.5, 47.1], [6.6, 47.1], [6.6, 35.5]]],
                },
            }
        ],
    }
    fc, meta = build_boundaries_feature_collection(raw)
    assert len(fc["features"]) == 1
    assert fc["features"][0]["id"] == 0
    assert fc["features"][0]["properties"] == {"iso3": "ITA", "name": "Italy"}
    assert meta["ITA"]["bbox"] == [6.6, 35.5, 18.5, 47.1]
