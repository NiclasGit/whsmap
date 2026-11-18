import { describe, expect, it } from 'vitest';
import { resolveRouteState } from './routing';
import type { CountrySummary } from './types';

const countries = [{ iso3: 'ITA', name: 'Italy' }] as CountrySummary[];

describe('resolveRouteState', () => {
	it('resolves root route to world view', () => {
		expect(resolveRouteState(countries, {})).toEqual({
			status: 'world',
			country: null,
			siteId: null
		});
	});

	it('resolves case-insensitive ISO3 and optional siteId', () => {
		const res = resolveRouteState(countries, { iso3: 'ita', siteId: 'whs-91' });
		expect(res.status).toBe('country');
		expect(res.country?.iso3).toBe('ITA');
		expect(res.siteId).toBe('whs-91');
	});

	it('returns not-found for unknown ISO3 without throwing', () => {
		const res = resolveRouteState(countries, { iso3: 'ZZZ' });
		expect(res.status).toBe('not-found');
		expect(res.country).toBeNull();
	});
});
