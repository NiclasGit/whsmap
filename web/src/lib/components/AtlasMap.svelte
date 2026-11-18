<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import maplibregl from 'maplibre-gl';
	import 'maplibre-gl/dist/maplibre-gl.css';
	import type {
		Category,
		CountrySummary,
		SitesFeatureCollection
	} from '$lib/data/types';
	import { getCountryScore, scoreToColor } from '$lib/data/richness';
	import {
		bboxToCameraBounds,
		buildWorldDimFilter,
		shouldReduceMotion
	} from '$lib/map/camera';
	import { buildNightAtlasStyle } from '$lib/map/style';

	interface Props {
		countries: CountrySummary[];
		selectedCountry: CountrySummary | null;
		hoveredCountryIso3: string | null;
		sites: SitesFeatureCollection | null;
		activeCategory: Category | null;
		selectedSiteId: string | null;
		hoveredSiteId: string | null;
		onHoverCountry: (iso3: string | null) => void;
		onSelectCountry: (iso3: string) => void;
		onSelectSite: (siteId: string) => void;
		onHoverSite: (siteId: string | null) => void;
	}

	let {
		countries,
		selectedCountry,
		hoveredCountryIso3,
		sites,
		activeCategory,
		selectedSiteId,
		hoveredSiteId,
		onHoverCountry,
		onSelectCountry,
		onSelectSite,
		onHoverSite
	}: Props = $props();

	let mapContainer: HTMLDivElement | undefined = $state();
	let map: maplibregl.Map | null = null;
	let mapReady = $state(false);
	let countryFeatureIdByIso3 = new Map<string, number>();
	let siteFeatureIdBySiteId = new Map<string, number>();
	let prevHoveredCountryId: number | null = null;
	let prevSelectedCountryId: number | null = null;
	let prevHoveredSiteNumId: number | null = null;
	let prevSelectedSiteNumId: number | null = null;
	let lastMovedCountryIso3: string | null = null;

	let animFrame: number | null = null;
	let isUserInteracting = false;
	let lastInteractionTime = 0;

	function syncCountryRichnessColors() {
		if (!map || !mapReady) return;
		const byIso = new Map(countries.map((c) => [c.iso3, c]));
		for (const [iso3, featId] of countryFeatureIdByIso3.entries()) {
			const country = byIso.get(iso3);
			const color = country ? scoreToColor(getCountryScore(country)) : '#1b2d4a';
			map.setFeatureState({ source: 'countries', id: featId }, { richnessColor: color });
		}
	}

	function syncSelectedAndHoveredCountry() {
		if (!map || !mapReady) return;

		if (prevHoveredCountryId !== null) {
			map.setFeatureState({ source: 'countries', id: prevHoveredCountryId }, { hover: false });
			prevHoveredCountryId = null;
		}
		if (hoveredCountryIso3) {
			const fid = countryFeatureIdByIso3.get(hoveredCountryIso3);
			if (fid !== undefined) {
				map.setFeatureState({ source: 'countries', id: fid }, { hover: true });
				prevHoveredCountryId = fid;
			}
		}

		if (prevSelectedCountryId !== null) {
			map.setFeatureState(
				{ source: 'countries', id: prevSelectedCountryId },
				{ selected: false }
			);
			prevSelectedCountryId = null;
		}
		if (selectedCountry) {
			const fid = countryFeatureIdByIso3.get(selectedCountry.iso3);
			if (fid !== undefined) {
				map.setFeatureState({ source: 'countries', id: fid }, { selected: true });
				prevSelectedCountryId = fid;
			}
		}

		map.setFilter('countries-dim', buildWorldDimFilter(selectedCountry?.iso3 ?? null));

		const nextIso = selectedCountry?.iso3 ?? null;
		if (nextIso !== lastMovedCountryIso3) {
			lastMovedCountryIso3 = nextIso;
			const reduced = shouldReduceMotion();
			if (selectedCountry) {
				const bounds = bboxToCameraBounds(selectedCountry.bbox);
				const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
				map.fitBounds(bounds, {
					padding: isMobile
						? { top: 48, bottom: 320, left: 32, right: 32 }
						: { top: 64, bottom: 64, left: 64, right: 440 },
					maxZoom: 8.5,
					duration: reduced ? 0 : 1500
				});
			} else {
				map.easeTo({
					center: [18, 24],
					zoom: 1.75,
					pitch: 0,
					bearing: 0,
					duration: reduced ? 0 : 1100
				});
			}
		}
	}

	function syncSitesSource() {
		if (!map || !mapReady) return;
		const src = map.getSource('sites') as maplibregl.GeoJSONSource | undefined;
		if (!src) return;

		siteFeatureIdBySiteId.clear();
		prevHoveredSiteNumId = null;
		prevSelectedSiteNumId = null;

		if (!sites || !selectedCountry) {
			src.setData({ type: 'FeatureCollection', features: [] });
			return;
		}

		const filteredFeatures = activeCategory
			? sites.features.filter((f) => f.properties.category === activeCategory)
			: sites.features;

		for (const f of filteredFeatures) {
			siteFeatureIdBySiteId.set(f.properties.siteId, f.id);
		}

		src.setData({
			type: 'FeatureCollection',
			features: filteredFeatures as any
		});
	}

	function syncSiteHighlights() {
		if (!map || !mapReady) return;

		if (prevHoveredSiteNumId !== null) {
			map.setFeatureState({ source: 'sites', id: prevHoveredSiteNumId }, { hover: false });
			prevHoveredSiteNumId = null;
		}
		if (hoveredSiteId) {
			const numId = siteFeatureIdBySiteId.get(hoveredSiteId);
			if (numId !== undefined) {
				map.setFeatureState({ source: 'sites', id: numId }, { hover: true });
				prevHoveredSiteNumId = numId;
			}
		}

		if (prevSelectedSiteNumId !== null) {
			map.setFeatureState({ source: 'sites', id: prevSelectedSiteNumId }, { selected: false });
			prevSelectedSiteNumId = null;
		}
		if (selectedSiteId) {
			const numId = siteFeatureIdBySiteId.get(selectedSiteId);
			if (numId !== undefined) {
				map.setFeatureState({ source: 'sites', id: numId }, { selected: true });
				prevSelectedSiteNumId = numId;
			}
		}
	}

	$effect(() => {
		countries;
		mapReady;
		syncCountryRichnessColors();
	});

	$effect(() => {
		selectedCountry;
		hoveredCountryIso3;
		mapReady;
		syncSelectedAndHoveredCountry();
	});

	$effect(() => {
		sites;
		activeCategory;
		selectedCountry;
		mapReady;
		syncSitesSource();
	});

	$effect(() => {
		selectedSiteId;
		hoveredSiteId;
		sites;
		activeCategory;
		mapReady;
		syncSiteHighlights();
	});

	onMount(() => {
		if (!mapContainer) return;

		const instance = new maplibregl.Map({
			container: mapContainer,
			style: buildNightAtlasStyle({ boundariesUrl: '/data/boundaries.geojson' }),
			center: [18, 24],
			zoom: 1.75,
			attributionControl: false
		});
		map = instance;

		instance.addControl(
			new maplibregl.AttributionControl({
				compact: true,
				customAttribution: 'UNESCO · Wikidata · Natural Earth'
			}),
			'bottom-right'
		);

		instance.on('load', async () => {
			try {
				const resp = await fetch('/data/boundaries.geojson');
				if (resp.ok) {
					const fc = await resp.json();
					for (const feat of fc.features ?? []) {
						if (typeof feat.id === 'number' && feat.properties?.iso3) {
							countryFeatureIdByIso3.set(feat.properties.iso3, feat.id);
						}
					}
				}
			} catch {
				// boundaries already loaded by MapLibre source
			}
			mapReady = true;
		});

		const markInteraction = () => {
			lastInteractionTime = performance.now();
		};

		instance.on('mousedown', () => {
			isUserInteracting = true;
			markInteraction();
		});
		instance.on('mouseup', () => {
			isUserInteracting = false;
			markInteraction();
		});
		instance.on('touchstart', () => {
			isUserInteracting = true;
			markInteraction();
		});
		instance.on('touchend', () => {
			isUserInteracting = false;
			markInteraction();
		});
		instance.on('wheel', markInteraction);

		// Country hover and click
		instance.on('mousemove', 'countries-fill', (e) => {
			const feat = e.features?.[0];
			const iso3 = feat?.properties?.iso3 as string | undefined;
			if (!selectedCountry && iso3) {
				instance.getCanvas().style.cursor = 'pointer';
				onHoverCountry(iso3);
			}
		});

		instance.on('mouseleave', 'countries-fill', () => {
			if (!selectedCountry) {
				instance.getCanvas().style.cursor = '';
				onHoverCountry(null);
			}
		});

		instance.on('click', 'countries-fill', (e) => {
			const siteHits = instance.queryRenderedFeatures(e.point, {
				layers: ['sites-unesco', 'sites-notable', 'sites-clusters']
			});
			if (siteHits.length > 0) return;

			const feat = e.features?.[0];
			const iso3 = feat?.properties?.iso3 as string | undefined;
			if (!iso3) return;

			const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
			if (!selectedCountry && isMobile && hoveredCountryIso3 !== iso3) {
				onHoverCountry(iso3);
				return;
			}
			onSelectCountry(iso3);
		});

		// Cluster expansion
		instance.on('click', 'sites-clusters', async (e) => {
			const feat = e.features?.[0];
			if (!feat) return;
			const clusterId = feat.properties?.cluster_id;
			const src = instance.getSource('sites') as maplibregl.GeoJSONSource | undefined;
			if (!src || clusterId === undefined) return;
			const zoom = await src.getClusterExpansionZoom(clusterId);
			const coords = (feat.geometry as any).coordinates as [number, number];
			instance.easeTo({
				center: coords,
				zoom,
				duration: shouldReduceMotion() ? 0 : 550
			});
		});

		// Site marker clicks & hovers
		for (const layerId of ['sites-unesco', 'sites-notable']) {
			instance.on('mousemove', layerId, (e) => {
				instance.getCanvas().style.cursor = 'pointer';
				const siteId = e.features?.[0]?.properties?.siteId as string | undefined;
				if (siteId) onHoverSite(siteId);
			});
			instance.on('mouseleave', layerId, () => {
				instance.getCanvas().style.cursor = '';
				onHoverSite(null);
			});
			instance.on('click', layerId, (e) => {
				const siteId = e.features?.[0]?.properties?.siteId as string | undefined;
				if (siteId) onSelectSite(siteId);
			});
		}

		// Auto-rotation loop in world view
		const tick = (now: number) => {
			if (
				map &&
				mapReady &&
				!selectedCountry &&
				!hoveredCountryIso3 &&
				!isUserInteracting &&
				!shouldReduceMotion() &&
				now - lastInteractionTime > 3500
			) {
				const center = map.getCenter();
				map.setCenter([center.lng + 0.035, center.lat]);
			}
			animFrame = requestAnimationFrame(tick);
		};
		animFrame = requestAnimationFrame(tick);
	});

	onDestroy(() => {
		if (animFrame !== null) cancelAnimationFrame(animFrame);
		map?.remove();
		map = null;
	});
</script>

<div class="map-stage" bind:this={mapContainer} aria-label="Interactive world heritage globe"></div>

<style>
	.map-stage {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
</style>
