import type { Category, SiteFeature, SpreadLevel } from '$lib/data/types';

export const MONTH_LABELS: readonly string[] = [
	'J',
	'F',
	'M',
	'A',
	'M',
	'J',
	'J',
	'A',
	'S',
	'O',
	'N',
	'D'
] as const;

export const MONTH_NAMES: readonly string[] = [
	'Jan',
	'Feb',
	'Mar',
	'Apr',
	'May',
	'Jun',
	'Jul',
	'Aug',
	'Sep',
	'Oct',
	'Nov',
	'Dec'
] as const;

export const SPREAD_DESCRIPTIONS: Record<SpreadLevel, string> = {
	compact: 'Compact · easy to combine in one base',
	moderate: 'Moderate · regional hops by train or car',
	spread: 'Spread out · best explored region by region'
};

export function filterSitesByCategory(
	sites: SiteFeature[],
	category: Category | null
): SiteFeature[] {
	if (!category) return sites;
	return sites.filter((s) => s.properties.category === category);
}

export function reconciledSelectedSiteId(
	sites: SiteFeature[],
	category: Category | null,
	selectedSiteId: string | null
): string | null {
	if (!selectedSiteId) return null;
	const visible = filterSitesByCategory(sites, category);
	return visible.some((s) => s.properties.siteId === selectedSiteId) ? selectedSiteId : null;
}

export function formatCostTier(tier: number): string {
	const clamped = Math.max(1, Math.min(5, Math.round(tier)));
	return '€'.repeat(clamped);
}
