# Heritage Atlas — Data Contract

Shared by `2026-11-18-data-pipeline.md` (producer) and `2026-11-18-web-app.md` (consumer).
Spec: `docs/superpowers/specs/2026-11-18-heritage-atlas-design.md`.

The machine-readable source of truth is `contract/countries.schema.json` and `contract/sites.schema.json` (JSON Schema draft 2020-12), created in Pipeline Task 1. The pipeline validates its output against them; the web app's TypeScript types in `web/src/lib/data/types.ts` mirror them field-for-field.

## Output location

Pipeline writes to `web/static/data/` (overridable with `--out`):

```
web/static/data/
  countries.json          # all countries, summary + practical info
  boundaries.geojson      # country polygons, simplified
  sites/{ISO3}.geojson    # one file per country, loaded on demand
  report.md               # validation report (not loaded by the site)
```

## Enums

`Category` (exact strings, this order is the display order):
`ancient`, `sacred`, `castles`, `towns`, `palaces`, `landscapes`, `modern`, `natural`

`FameLevel` (int, from Wikipedia sitelink count `fame`):
`1` hidden gem (< 10) · `2` known (10–29) · `3` famous (30–79) · `4` world-famous (≥ 80)

`SpreadLevel`: `compact` · `moderate` · `spread`

## countries.json

```jsonc
{
  "generatedAt": "2026-11-18",          // ISO date
  "countries": [                         // sorted by name
    {
      "iso3": "ITA",                     // ISO 3166-1 alpha-3, uppercase; primary key everywhere
      "name": "Italy",                   // English short name
      "aliases": ["Italia"],             // extra search terms, may be empty
      "teaser": "Roman forums, …",       // 1 sentence, never empty (fallback text generated)
      "bbox": [6.6, 35.5, 18.5, 47.1],   // [west, south, east, north] of the MAIN territory only
                                         // (largest polygon + polygons within 500 km of it); west > east when crossing 180°
      "counts": {
        "unesco": 60,                    // UNESCO sites shown for this country (incl. transboundary)
        "notable": 214,                  // non-UNESCO sites shown (after per-country tuning)
        "byCategory": { "ancient": 41, "sacred": 77, … }   // over shown sites; all 8 keys always present
      },
      "richness": 0.87,                  // 0..1, sqrt-scaled, see pipeline select.richness()
      "richnessRaw": 412,                // 3*unesco + notable-at-global-floor
      "spread": { "level": "moderate", "medianKm": 240 } ,        // null if < 2 sites
      "climate": {                                                  // null if unavailable
        "tempC":   [8.1, …],             // 12 monthly means, Jan..Dec
        "precipMm":[70, …],              // 12 monthly totals
        "comfortable": [false, …]        // 12 booleans
      },
      "cost": { "tier": 3, "priceLevelRatio": 0.62, "year": 2023 },   // null if unavailable; tier 1..5
      "safety": { "level": 2, "label": "Exercise Increased Caution",
                  "url": "https://travel.state.gov/…", "asOf": "2026-11-10" },  // null if unavailable; level 1..4
      "traditions": { "count": 17, "examples": ["Neapolitan pizza-making", …] }  // examples ≤ 5; count 0 + [] if none
    }
  ]
}
```

## boundaries.geojson

FeatureCollection of (Multi)Polygons, one feature per country in `countries.json`.
`feature.id` = numeric index (MapLibre feature-state needs numeric ids); `properties`: `{ "iso3": "ITA", "name": "Italy" }`.

## sites/{ISO3}.geojson

FeatureCollection of Points, ordered: UNESCO first, then `fame` descending.

```jsonc
{
  "type": "Feature",
  "id": 0,                                   // numeric index within file
  "geometry": { "type": "Point", "coordinates": [12.4922, 41.8902] },
  "properties": {
    "siteId": "whs-91",                      // "whs-{UNESCO id}" or "wd-{QID}"; URL-safe, unique globally
    "name": "Historic Centre of Rome",
    "category": "towns",
    "unesco": true,
    "inDanger": false,                       // always false for non-UNESCO
    "yearInscribed": 1980,                   // null for non-UNESCO
    "fame": 112,                             // Wikipedia sitelinks; 0 if no Wikidata match
    "fameLevel": 4,
    "summary": "Founded, according to legend, …",   // 1–3 sentences, plain text, may be ""
    "summarySource": "unesco",               // "unesco" | "wikipedia" | null
    "image": { "thumbUrl": "https://upload.wikimedia.org/…", "author": "Jane Doe",
               "license": "CC BY-SA 4.0", "sourceUrl": "https://commons.wikimedia.org/wiki/File:…" },  // or null
    "wikipediaUrl": "https://en.wikipedia.org/wiki/…",  // or null
    "unescoUrl": "https://whc.unesco.org/en/list/91",   // or null
    "wikidataId": "Q…",                                  // or null
    "countries": ["ITA", "VAT"]              // all countries this site belongs to (transboundary)
  }
}
```

Countries with zero sites still get a file with an empty FeatureCollection.
