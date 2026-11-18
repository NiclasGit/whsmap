import type { LayerSpecification, SourceSpecification, StyleSpecification } from 'maplibre-gl';
import { CATEGORY_META } from '$lib/data/categories';
import { buildWorldDimFilter } from './camera';

export interface NightAtlasStyleOptions {
	boundariesUrl: string;
	pmtilesUrl?: string;
}

export function generateGraticuleGeoJSON(step = 15): GeoJSON.FeatureCollection {
	const features: GeoJSON.Feature[] = [];
	for (let lon = -180; lon <= 180; lon += step) {
		const coords: [number, number][] = [];
		for (let lat = -80; lat <= 80; lat += 5) {
			coords.push([lon, lat]);
		}
		features.push({
			type: 'Feature',
			properties: {},
			geometry: { type: 'LineString', coordinates: coords }
		});
	}
	for (let lat = -75; lat <= 75; lat += step) {
		const coords: [number, number][] = [];
		for (let lon = -180; lon <= 180; lon += 5) {
			coords.push([lon, lat]);
		}
		features.push({
			type: 'Feature',
			properties: {},
			geometry: { type: 'LineString', coordinates: coords }
		});
	}
	return { type: 'FeatureCollection', features };
}

export function buildNightAtlasStyle(options: NightAtlasStyleOptions): StyleSpecification {
	const categoryColorMatch: any[] = ['match', ['get', 'category']];
	for (const [cat, meta] of Object.entries(CATEGORY_META)) {
		categoryColorMatch.push(cat, meta.color);
	}
	categoryColorMatch.push('#f3d38b');

	const sources: Record<string, SourceSpecification> = {
		graticule: {
			type: 'geojson',
			data: generateGraticuleGeoJSON(15)
		},
		countries: {
			type: 'geojson',
			data: options.boundariesUrl
		},
		sites: {
			type: 'geojson',
			data: {
				type: 'FeatureCollection',
				features: []
			},
			cluster: true,
			clusterMaxZoom: 8,
			clusterRadius: 42
		}
	};

	if (options.pmtilesUrl) {
		sources.basemap = {
			type: 'vector',
			url: options.pmtilesUrl
		};
	}

	const basemapDetailLayers: LayerSpecification[] = options.pmtilesUrl
		? [
				{
					id: 'basemap-roads',
					type: 'line',
					source: 'basemap',
					'source-layer': 'roads',
					minzoom: 5,
					paint: {
						'line-color': 'rgba(243, 211, 139, 0.14)',
						'line-width': 0.8
					}
				},
				{
					id: 'basemap-places',
					type: 'symbol',
					source: 'basemap',
					'source-layer': 'places',
					minzoom: 4,
					layout: {
						'text-field': ['coalesce', ['get', 'name:en'], ['get', 'name']],
						'text-font': ['Noto Sans Regular'],
						'text-size': 11
					},
					paint: {
						'text-color': 'rgba(233, 227, 211, 0.72)',
						'text-halo-color': '#060d1d',
						'text-halo-width': 1.2
					}
				}
			]
		: [];

	return {
		version: 8,
		name: 'Heritage Atlas — Night Atlas',
		glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
		projection: {
			type: 'globe'
		},
		sky: {
			'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 0.85, 5, 0.35, 8, 0]
		},
		sources,
		layers: [
			{
				id: 'space-background',
				type: 'background',
				paint: {
					'background-color': 'rgba(7, 17, 36, 0.92)'
				}
			},
			{
				id: 'graticule-lines',
				type: 'line',
				source: 'graticule',
				paint: {
					'line-color': 'rgba(180, 205, 255, 0.07)',
					'line-width': 0.6
				}
			},
			{
				id: 'countries-fill',
				type: 'fill',
				source: 'countries',
				paint: {
					'fill-color': ['coalesce', ['feature-state', 'richnessColor'], '#1b2d4a'],
					'fill-opacity': [
						'case',
						['boolean', ['feature-state', 'hover'], false],
						0.96,
						0.86
					]
				}
			},
			{
				id: 'countries-dim',
				type: 'fill',
				source: 'countries',
				filter: buildWorldDimFilter(null),
				paint: {
					'fill-color': '#030712',
					'fill-opacity': 0.68
				}
			},
			{
				id: 'countries-border',
				type: 'line',
				source: 'countries',
				paint: {
					'line-color': [
						'case',
						['boolean', ['feature-state', 'selected'], false],
						'#f3d38b',
						['boolean', ['feature-state', 'hover'], false],
						'#fff3cf',
						'rgba(10, 20, 40, 0.9)'
					],
					'line-width': [
						'case',
						['boolean', ['feature-state', 'selected'], false],
						2.2,
						['boolean', ['feature-state', 'hover'], false],
						1.4,
						0.6
					]
				}
			},
			...basemapDetailLayers,
			{
				id: 'sites-clusters',
				type: 'circle',
				source: 'sites',
				filter: ['has', 'point_count'],
				paint: {
					'circle-color': 'rgba(18, 36, 68, 0.92)',
					'circle-radius': ['step', ['get', 'point_count'], 15, 10, 19, 30, 24],
					'circle-stroke-color': '#f3d38b',
					'circle-stroke-width': 1.8
				}
			},
			{
				id: 'sites-cluster-count',
				type: 'symbol',
				source: 'sites',
				filter: ['has', 'point_count'],
				layout: {
					'text-field': '{point_count_abbreviated}',
					'text-font': ['Noto Sans Regular'],
					'text-size': 12
				},
				paint: {
					'text-color': '#f3d38b'
				}
			},
			{
				id: 'sites-notable',
				type: 'circle',
				source: 'sites',
				filter: ['all', ['!', ['has', 'point_count']], ['!=', ['get', 'unesco'], true]],
				paint: {
					'circle-color': categoryColorMatch as any,
					'circle-radius': [
						'case',
						['boolean', ['feature-state', 'hover'], false],
						8,
						['boolean', ['feature-state', 'selected'], false],
						9,
						5.5
					],
					'circle-stroke-color': '#081326',
					'circle-stroke-width': 1.4
				}
			},
			{
				id: 'sites-unesco-glow',
				type: 'circle',
				source: 'sites',
				filter: ['all', ['!', ['has', 'point_count']], ['==', ['get', 'unesco'], true]],
				paint: {
					'circle-color': 'rgba(243, 211, 139, 0.28)',
					'circle-radius': [
						'case',
						['boolean', ['feature-state', 'selected'], false],
						16,
						['boolean', ['feature-state', 'hover'], false],
						14,
						12
					]
				}
			},
			{
				id: 'sites-unesco',
				type: 'circle',
				source: 'sites',
				filter: ['all', ['!', ['has', 'point_count']], ['==', ['get', 'unesco'], true]],
				paint: {
					'circle-color': categoryColorMatch as any,
					'circle-radius': [
						'case',
						['boolean', ['feature-state', 'selected'], false],
						9.5,
						['boolean', ['feature-state', 'hover'], false],
						8.5,
						7.5
					],
					'circle-stroke-color': '#f3d38b',
					'circle-stroke-width': 2.4
				}
			}
		]
	};
}
