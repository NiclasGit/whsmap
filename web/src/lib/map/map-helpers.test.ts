import { describe, expect, it } from 'vitest';
import { bboxToCameraBounds, buildWorldDimFilter } from './camera';
import { buildNightAtlasStyle } from './style';

describe('camera and Night Atlas style helpers', () => {
	it('pads tiny country bboxes so camera does not over-zoom', () => {
		const [[w, s], [e, n]] = bboxToCameraBounds([12.44, 41.9, 12.46, 41.91], 0.5);
		expect(e - w).toBeGreaterThanOrEqual(0.5);
		expect(n - s).toBeGreaterThanOrEqual(0.5);
	});

	it('normalizes antimeridian bboxes where west > east', () => {
		const [[w, s], [e, n]] = bboxToCameraBounds([178.0, -19.0, -178.0, -16.0]);
		expect(e).toBeGreaterThan(w);
		expect(e - w).toBeCloseTo(4.0, 1);
	});

	it('builds a globe style with richness fill and dim overlay filter', () => {
		const style = buildNightAtlasStyle({ boundariesUrl: '/data/boundaries.geojson' });
		expect(style.projection?.type).toBe('globe');
		expect(style.layers.some((l) => l.id === 'countries-fill')).toBe(true);
		expect(style.layers.some((l) => l.id === 'countries-dim')).toBe(true);
		expect(buildWorldDimFilter('ITA')).toEqual(['!=', ['get', 'iso3'], 'ITA']);
	});
});
