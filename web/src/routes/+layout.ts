import type { CountriesPayload } from '$lib/data/types';

export const ssr = false;
export const prerender = false;

export async function load({ fetch }: { fetch: typeof globalThis.fetch }) {
	const resp = await fetch('/data/countries.json');
	const payload = (await resp.json()) as CountriesPayload;
	return {
		countries: payload.countries,
		generatedAt: payload.generatedAt
	};
}
