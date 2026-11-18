import type { CountrySummary } from './types';

export function searchCountries(
	countries: CountrySummary[],
	query: string,
	limit = 8
): CountrySummary[] {
	const q = query.trim().toLowerCase();
	if (!q) return [];

	const scored: Array<{ country: CountrySummary; rank: number }> = [];
	for (const country of countries) {
		const iso = country.iso3.toLowerCase();
		const name = country.name.toLowerCase();
		const aliases = (country.aliases || []).map((a) => a.toLowerCase());

		let rank = 0;
		if (iso === q || name === q) {
			rank = 100;
		} else if (name.startsWith(q)) {
			rank = 80;
		} else if (iso.startsWith(q) || aliases.some((a) => a.startsWith(q))) {
			rank = 65;
		} else if (name.includes(q) || aliases.some((a) => a.includes(q))) {
			rank = 40;
		}

		if (rank > 0) {
			scored.push({ country, rank });
		}
	}

	return scored
		.sort(
			(a, b) =>
				b.rank - a.rank ||
				b.country.richnessRaw - a.country.richnessRaw ||
				a.country.name.localeCompare(b.country.name)
		)
		.slice(0, limit)
		.map((s) => s.country);
}
