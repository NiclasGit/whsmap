import type { CountrySummary } from './types';

const LOW_RGB = [0x1b, 0x2d, 0x4a] as const;
const HIGH_RGB = [0xf5, 0xc7, 0x6b] as const;

/**
 * Isolated score selector for a country (0..1).
 * In v1 this returns the precomputed global-floor heritage richness;
 * in v2 preference scoring can replace or weight this client-side.
 */
export function getCountryScore(country: CountrySummary): number {
	return Math.max(0, Math.min(1, country.richness));
}

export function scoreToColor(score: number): string {
	const t = Math.max(0, Math.min(1, score));
	const r = Math.round(LOW_RGB[0] + (HIGH_RGB[0] - LOW_RGB[0]) * t);
	const g = Math.round(LOW_RGB[1] + (HIGH_RGB[1] - LOW_RGB[1]) * t);
	const b = Math.round(LOW_RGB[2] + (HIGH_RGB[2] - LOW_RGB[2]) * t);
	return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

export function getTopCountries(countries: CountrySummary[], limit = 5): CountrySummary[] {
	return [...countries]
		.sort((a, b) => b.richnessRaw - a.richnessRaw || a.name.localeCompare(b.name))
		.slice(0, limit);
}
