import type { StyleSpecification } from 'maplibre-gl';
import { CATEGORY_META } from '$lib/data/categories';
import { buildWorldDimFilter } from './camera';

export interface NightAtlasStyleOptions {
	boundariesUrl: string;
	pmtilesUrl?: string;
}

export function buildNightAtlasStyle(options: NightAtlasStyleOptions): StyleSpecification {
	const categoryColorMatch: any[] = ['match', ['get', 'category']];
	for (const [cat, meta] of Object.entries(CATEGORY_META)) {
		categoryColorMatch.push(cat, meta.color);
	}
	categoryColorMatch.push('#f3d38b');

	return {
		version: 8,
		name: 'Heritage Atlas — Night Atlas',
		projection: {
			type: 'globe'
		},
		sources: {
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
		},
		layers: [
			{
				id: 'space-background',
				type: 'background',
				paint: {
					'background-color': '#071124'
				}
			},
			{
				id: 'countries-fill',
				type: 'fill',
				source: 'countries',
				paint: {
					'fill-color': [
						'coalesce',
						['feature-state', 'richnessColor'],
						'#1b2d4a'
					],
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
			{
				id: 'sites-clusters',
				type: 'circle',
				source: 'sites',
				filter: ['has', 'point_count'],
				paint: {
					'circle-color': 'rgba(18, 36, 68, 0.92)',
					'circle-radius': [
						'step',
						['get', 'point_count'],
						15,
						10,
						19,
						30,
						24
					],
					'circle-stroke-color': '#f3d38b',
					'circle-stroke-width': 1.8
				}
			},
			{
				id: 'sites-notable',
				type: 'circle',
				source: 'sites',
				filter: [
					'all',
					['!', ['has', 'point_count']],
					['!=', ['get', 'unesco'], true]
				],
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
				filter: [
					'all',
					['!', ['has', 'point_count']],
					['==', ['get', 'unesco'], true]
				],
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
				filter: [
					'all',
					['!', ['has', 'point_count']],
					['==', ['get', 'unesco'], true]
				],
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
