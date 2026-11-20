import { base } from '$app/paths';
import type { SitesFeatureCollection } from './types';

export function createSitesLoader(fetchFn: typeof fetch = fetch) {
	const cache = new Map<string, SitesFeatureCollection>();
	let currentToken = 0;
	let currentAbort: AbortController | null = null;

	return {
		async loadCountrySites(iso3: string): Promise<SitesFeatureCollection | null> {
			const norm = iso3.trim().toUpperCase();
			const token = ++currentToken;
			if (currentAbort) {
				currentAbort.abort();
				currentAbort = null;
			}

			if (cache.has(norm)) {
				return cache.get(norm)!;
			}

			const controller = new AbortController();
			currentAbort = controller;

			try {
				const resp = await fetchFn(`${base}/data/sites/${norm}.geojson`, {
					signal: controller.signal
				});
				if (token !== currentToken) {
					return null;
				}
				if (!resp.ok) {
					return { type: 'FeatureCollection', features: [] };
				}
				const data = (await resp.json()) as SitesFeatureCollection;
				if (token !== currentToken) {
					return null;
				}
				cache.set(norm, data);
				return data;
			} catch {
				if (token !== currentToken || controller.signal.aborted) {
					return null;
				}
				return { type: 'FeatureCollection', features: [] };
			}
		}
	};
}
