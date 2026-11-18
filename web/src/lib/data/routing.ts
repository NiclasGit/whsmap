import type { CountrySummary } from './types';

export interface RouteState {
	status: 'world' | 'country' | 'not-found';
	country: CountrySummary | null;
	siteId: string | null;
}

export function resolveRouteState(
	countries: CountrySummary[],
	params: { iso3?: string; siteId?: string }
): RouteState {
	const rawIso = params.iso3?.trim();
	if (!rawIso) {
		return {
			status: 'world',
			country: null,
			siteId: null
		};
	}

	const normIso = rawIso.toUpperCase();
	const country = countries.find((c) => c.iso3 === normIso) ?? null;
	if (!country) {
		return {
			status: 'not-found',
			country: null,
			siteId: null
		};
	}

	return {
		status: 'country',
		country,
		siteId: params.siteId?.trim() || null
	};
}
