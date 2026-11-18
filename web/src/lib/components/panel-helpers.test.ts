import { describe, expect, it } from 'vitest';
import {
	filterSitesByCategory,
	formatCostTier,
	reconciledSelectedSiteId
} from './panel-helpers';
import type { SiteFeature } from '$lib/data/types';

const sampleSites = [
	{
		id: 0,
		type: 'Feature',
		geometry: { type: 'Point', coordinates: [12, 41] },
		properties: { siteId: 'whs-1', category: 'ancient', name: 'Forum' }
	},
	{
		id: 1,
		type: 'Feature',
		geometry: { type: 'Point', coordinates: [12, 42] },
		properties: { siteId: 'wd-2', category: 'castles', name: 'Castle' }
	}
] as SiteFeature[];

describe('panel helpers', () => {
	it('filters sites by category and reconciles active site selection when filtered out', () => {
		const filtered = filterSitesByCategory(sampleSites, 'castles');
		expect(filtered.map((s) => s.properties.siteId)).toEqual(['wd-2']);
		expect(reconciledSelectedSiteId(sampleSites, 'castles', 'whs-1')).toBeNull();
		expect(reconciledSelectedSiteId(sampleSites, 'castles', 'wd-2')).toBe('wd-2');
	});

	it('formats cost tier 1..5 as euro symbols', () => {
		expect(formatCostTier(1)).toBe('€');
		expect(formatCostTier(3)).toBe('€€€');
		expect(formatCostTier(5)).toBe('€€€€€');
	});
});
