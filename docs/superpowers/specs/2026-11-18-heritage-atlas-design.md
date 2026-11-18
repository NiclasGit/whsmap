# Heritage Atlas — Design (v1: Globe, Country View, Data)

*Working title "Heritage Atlas"; project folder `WHSMAP`. Status: awaiting owner approval (builder check done).*

Legend: **[decided]** = chosen by the project owner · **[call]** = proposed by the designer, open to correction · **[builder]** = left to the builder.

---

## 1. Intent

A public website that makes the world explorable through its cultural and historical heritage. It is for **cultural travelers looking for inspiration** — people who don't yet know where to go and want to see what each country offers and what they can expect there. **[decided]**

Priority order **[decided]**:
1. A polished, visually pleasing, intuitive map experience — **this document**.
2. Preference-based scoring of countries — *separate design round later*.
3. Trip planning — *out of scope for now*.

**Definition of done for v1** **[decided]**: a working build the owner can try (locally or on a private link) — not a public launch. Launch work (domain, legal/attribution pages, confirming UNESCO reuse terms, SEO prerendering polish) follows in a later step; v1 should not paint itself into a corner for it but need not do it.

**Content work** **[decided]**: the builder produces all curated content — UNESCO category review and country teasers — via an automated + AI-assisted first pass. The owner spot-checks at will; nothing in v1 blocks on owner review.

## 2. Goals, non-goals, anti-goals

**Goals (v1)**
- A cinematic world globe that invites exploration ("Night Atlas" direction). **[decided]**
- Selecting a country flies the map into it, shows it large, and places heritage sites as markers styled by category. **[decided]**
- Per-country stats by category (castles, ancient sites, sacred sites, …) plus practical "what to expect" info. **[decided]** (exact set **[call]**, §6.3)
- Coverage beyond UNESCO: UNESCO World Heritage Sites as highlighted "stars" plus notable non-UNESCO sites from Wikidata/OSM, filtered by a fame threshold. **[decided]**
- Works on desktop and mobile (touch to spin/zoom). **[call]**

**Non-goals (v1)**
- Preference input / scoring / ranking of countries (next design round; v1 must leave room for it — see §9).
- Trip planning, itineraries, routing. **[decided]**
- Accounts, saved lists, reviews, booking, live data (opening hours, prices, crowds).
- Visa, language, transport info (later).
- Languages other than English. **[call]**

**Anti-goals** — it fails even if it "works" if:
- It feels like a database or spreadsheet rather than an inviting atlas.
- The globe stutters, or loading feels slow.
- The map is cluttered with markers, or obscure sites drown out the meaningful ones.
- It implies a misleading "more UNESCO sites = better country" leaderboard, or under-represents regions where UNESCO/Wikipedia coverage is thin (e.g. Ireland or much of Africa looking empty purely due to data bias).

## 3. Constraints

- No per-request map fees or API keys for the basemap; hosting should fit a free or near-free tier. **[call]**
- All data is prebuilt by an offline pipeline and shipped as static files; the site does no live third-party data fetching at runtime (except optional image loading from Wikimedia). **[call]**
- Licensing/attribution must be honoured: OSM (ODbL), Wikipedia text (CC BY-SA), Wikimedia Commons images (per-file licences), UNESCO data (verify reuse terms — **[builder]** must confirm before launch), Natural Earth (public domain).
- Node.js is not yet installed on the dev machine; setup is part of the plan.

## 4. Approaches considered

| | Approach | Trade-off |
|---|---|---|
| 1 | D3/SVG globe (as in the mockup) | Matches mockup exactly, light; but weak country view: sluggish with thousands of markers, no real geography when zooming. |
| **2** | **MapLibre GL JS (v5, globe projection) + self-hosted Protomaps vector tiles** | **Smooth fly-to, clustering, real geography down to site level, no fees; costs custom styling effort to achieve the Night Atlas look.** |
| 3 | globe.gl/three.js or CesiumJS | Most cinematic world view; poor for zoomed country exploration; Cesium heavy and nudges toward paid services. |

**Chosen: 2** **[decided]** — the country view is central, and only MapLibre serves both the globe and the close-up well. The Night Atlas look is recreated via a custom style.

## 5. Experience

### 5.1 World view (landing) — "Night Atlas" **[decided]**
Reference mockup: `.superpowers/brainstorm/landing-directions.html`, direction A.
- Dark navy space background, globe slowly auto-rotating; drag/touch to spin; auto-rotate pauses on interaction and resumes after idle.
- Countries filled on a dark-blue → gold scale by **heritage richness**. Until scoring exists, richness = sqrt-scaled weighted count (UNESCO site = 3, notable site = 1) **[call]**, where notable sites are counted against **one global fame floor for all countries** — *not* the per-country tuned set used for markers (§6.1), which would flatten notable counts and collapse richness into a UNESCO leaderboard. Richness is an explicit placeholder; it must be easy to swap for the later score.
- Faint graticule and an atmosphere glow around the globe.
- Hover (desktop) / tap (mobile) a country → glass side panel: country name, headline number (UNESCO count + notable count), one-line teaser, "Explore {country} →".
- Idle panel: invitation text + top-5 list labelled factually ("most heritage sites"), not as "best". **[call]**
- Title and legend overlays as in the mockup. Serif display font (Cormorant Garamond) + Inter for UI. **[call]**
- Country search box (type-ahead) for people who already have a name in mind. **[call]**

### 5.2 Country view **[decided: fly-in, large frame, category markers, stats]**
- "Explore" → camera flies to fit the country; the rest of the world dims; the selected country is outlined/lit. **[decided]** The globe transitions naturally to flat mercator at higher zoom (MapLibre default).
- Basemap at country zoom shows restrained geography (coastlines, terrain shading, major cities, few roads) in the same dark/gold palette. **[call]**
- Markers: one icon/colour per category (§6.2). UNESCO sites larger, gold-ringed "stars"; notable sites smaller. Markers cluster when dense and expand on zoom. **[call]**
- Side panel (desktop right; mobile bottom sheet) **[call]**:
  - Country name, teaser, UNESCO count, notable count.
  - **Category stats** with icon and count; clicking a category filters markers. **[decided: stats; call: filter]**
  - "What to expect" block (§6.3).
  - Scrollable site list (UNESCO first, then by fame); hovering a list item highlights its marker and vice-versa.
- Back/escape returns to the globe.

### 5.3 Site card **[call]**
Clicking a marker or list item opens a card: photo, 2–3 sentence "why it matters", category, UNESCO badge (+ "in danger" flag, year inscribed), fame indicator ("world-famous" ↔ "hidden gem"), link to Wikipedia (and UNESCO page if applicable), attribution line.

### 5.4 URLs and sharing **[call]**
Deep links: `/` , `/country/{ISO3}`, `/country/{ISO3}/site/{siteId}`. Country pages are prerendered with basic text content for search engines and link previews.

### 5.5 Accessibility & mobile **[call]**
Keyboard: search, tab through site list, Esc to go back. The site list is the accessible alternative to the map. Respect `prefers-reduced-motion` (no auto-rotate, instant transitions). Touch: tap = select, button = enter.

## 6. Data

### 6.1 Sites
**UNESCO World Heritage Sites (~1,200)** **[decided]** — from UNESCO's published list: id, name, country/countries, coordinates, cultural/natural/mixed, criteria, year inscribed, in-danger status, short description. Transboundary sites appear under each country they belong to. Linked to Wikidata via property P757 (World Heritage Site ID) to obtain image, Wikipedia links and fame.

**Notable non-UNESCO sites** **[decided]** — from Wikidata (primary) with OSM as a secondary source for category hints/coordinates **[call]**. Candidate types: castles, fortifications, palaces, archaeological sites, ruins, temples/churches/mosques/monasteries and other places of worship, historic town centres, notable monuments/architecture, cultural landscapes.

**Fame threshold** **[call]**: fame = number of Wikipedia language editions with an article (Wikidata sitelinks). Include a non-UNESCO site if sitelinks ≥ threshold; default ~5, **tuned per country** so sparse countries still have meaningful content and dense countries aren't swamped (e.g. a target band of sites per country, with a hard floor so true obscurities never appear). Exact algorithm and target band **[builder]**.

Fame indicator on site cards derives from sitelinks (bucketed into ~3–4 levels). **[call]**

### 6.2 Categories **[call]**
Exactly one primary category per site:
`ancient` (archaeological, ruins, prehistoric) · `sacred` (temples, churches, mosques, monasteries) · `castles` (castles & forts) · `towns` (historic towns & old centres) · `palaces` (palaces & architecture) · `landscapes` (cultural landscapes, gardens) · `modern` (industrial & modern heritage) · `natural` (natural sites).

UNESCO does not tag sites this way: classification is automated from Wikidata "instance of" mappings, then **UNESCO sites get a reviewed pass** (by the builder, AI-assisted; owner spot-checks optionally) recorded in an overrides file kept in the repo (CSV/YAML: siteId → category). Non-UNESCO sites rely on automated mapping. The review tooling **[builder]**.

### 6.3 Country "what to expect" block (v1) **[call]**
| Item | Source (proposed) | Shown as |
|---|---|---|
| Category stats | derived | counts per category |
| How spread out sites are | derived from site coordinates | "compact / moderate / spread out" + short phrase; formula **[builder]** |
| Best months to visit | monthly climate normals sampled at the country's site locations (e.g. Open-Meteo climate data or WorldClim) | 12-month strip highlighting comfortable months; comfort rule **[builder]** |
| Cost level | World Bank price level ratio (PPP) | 5-tier "€ – €€€€€" |
| Safety | US State Dept travel advisory levels 1–4 (public domain) — German Foreign Office open data as alternative | level + label + link to the official source, with "as of" date |
| Living traditions | UNESCO Intangible Cultural Heritage lists | 3–5 named elements + count |

### 6.4 Text and images
- Site descriptions: Wikipedia summary extracts (CC BY-SA, attributed) or UNESCO short descriptions for WHS. Country teasers: short, drafted by the builder (AI-assisted, fact-checked against the site data) for at least the ~60 heritage-richest countries; generic fallback for others. Stored as an editable file in the repo so the owner can tweak them.
- Images: Wikidata P18 → Wikimedia Commons thumbnails, with licence/author attribution; placeholder art per category when missing.

### 6.5 Countries and boundaries **[call]**
Natural Earth admin-0 boundaries. Set of countries = UNESCO States Parties that have territory on the map. Disputed areas follow Natural Earth's default view. Treatment of overseas territories (e.g. sites in French Guiana) **[builder]**, but must be consistent.

## 7. Architecture **[call]**

```
pipeline/ (Python)  ──►  data/ (static JSON/GeoJSON)  ──►  web/ (SvelteKit, static build)
  fetch UNESCO, Wikidata,      countries.json (summary,         MapLibre GL JS v5 globe
  OSM, climate, cost, safety,  stats, richness, practical)      custom "Night Atlas" style
  ICH; classify; apply         sites/{ISO3}.geojson             Protomaps PMTiles basemap
  overrides; compute metrics   (loaded on demand)               prerendered country pages
```

- **Pipeline:** Python, rerunnable end-to-end, cached raw downloads, deterministic output, validation report (counts per country/category, missing images/coords). Run manually; refresh at least yearly after the World Heritage Committee session (July).
- **Web:** SvelteKit with static adapter; MapLibre GL JS v5 globe projection; country fills from a lightweight boundaries layer with feature-state for hover/selection; per-country site GeoJSON loaded on demand with MapLibre clustering.
- **Basemap:** self-hosted Protomaps PMTiles, zoom-limited so it fits free/cheap object storage; exact max zoom and storage **[builder]**.
- **Hosting:** static host (Cloudflare Pages or Netlify) + object storage for PMTiles.
- **Performance targets:** interactive globe in < ~3 s on average broadband; smooth (~60 fps) rotation and fly-to on a mid-range laptop and recent phone; initial payload excludes all per-country site data.

## 8. Left to the builder
Repo layout and tooling details; exact Wikidata queries and type mappings; fame-threshold algorithm and target band; spread and best-month formulas; review tooling for category overrides; icon set and exact marker styling within the Night Atlas palette; max basemap zoom; test strategy; how the try-out build is shared (local or private preview link). Confirming UNESCO data reuse terms is required before the later public launch, not for v1.

## 9. Looking ahead (not v1, but don't block it)
- **Scoring (next round):** user preferences (e.g. interest in categories) will produce a per-country score that replaces "heritage richness" as the globe colouring and drives a ranking. Keep richness computation isolated and country data structured per category so a weighted score can be computed client-side.
- **Trip planning (later):** site coordinates, time-needed estimates and spread metrics will feed it.
