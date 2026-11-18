import { describe, expect, it, vi } from 'vitest';
import { getCountryScore, getTopCountries, scoreToColor } from './richness';
import { searchCountries } from './search';
import { createSitesLoader } from './loader';
import type { CountrySummary } from './types';

const sampleCountries = [
	{
		iso3: 'ITA',
		name: 'Italy',
		aliases: ['Italia'],
		richness: 1.0,
		richnessRaw: 380,
		counts: { unesco: 60, notable: 200, byCategory: {} as any }
	},
	{
		iso3: 'DEU',
		name: 'Germany',
		aliases: ['Deutschland'],
		richness: 0.85,
		richnessRaw: 270,
		counts: { unesco: 54, notable: 150, byCategory: {} as any }
	},
	{
		iso3: 'IRL',
		name: 'Ireland',
		aliases: ['Éire'],
		richness: 0.35,
		richnessRaw: 45,
		counts: { unesco: 2, notable: 39, byCategory: {} as any }
	}
] as CountrySummary[];

describe('richness, search, and race-safe loader', () => {
	it('ranks top countries by richnessRaw and maps 0..1 score to dark-blue..gold hex', () => {
		const top = getTopCountries(sampleCountries, 2);
		expect(top.map((c) => c.iso3)).toEqual(['ITA', 'DEU']);
		expect(getCountryScore(sampleCountries[0])).toBe(1.0);
		expect(scoreToColor(0)).toBe('#1b2d4a');
		expect(scoreToColor(1)).toBe('#f5c76b');
	});

	it('searches countries by prefix, substring, ISO3, and alias', () => {
		expect(searchCountries(sampleCountries, 'deu')[0].iso3).toBe('DEU');
		expect(searchCountries(sampleCountries, 'deutsch')[0].iso3).toBe('DEU');
		expect(searchCountries(sampleCountries, 'ital')[0].iso3).toBe('ITA');
	});

	it('aborts and ignores stale country site responses when switching rapidly', async () => {
		let resolveFra!: (v: any) => void;
		const fetchMock = vi.fn((url: string) => {
			if (url.includes('FRA')) {
				return new Promise((r) => {
					resolveFra = r;
				});
			}
			return Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ type: 'FeatureCollection', features: [{ id: 1 }] })
			});
		}) as any;

		const loader = createSitesLoader(fetchMock);
		const pFra = loader.loadCountrySites('FRA');
		const pJpn = loader.loadCountrySites('JPN');

		const jpnResult = await pJpn;
		resolveFra({
			ok: true,
			json: () => Promise.resolve({ type: 'FeatureCollection', features: [] })
		});
		const fraResult = await pFra;

		expect(jpnResult?.features).toHaveLength(1);
		expect(fraResult).toBeNull();
	});
});
