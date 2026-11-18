export type Category =
	| 'ancient'
	| 'sacred'
	| 'castles'
	| 'towns'
	| 'palaces'
	| 'landscapes'
	| 'modern'
	| 'natural';

export type FameLevel = 1 | 2 | 3 | 4;

export type SpreadLevel = 'compact' | 'moderate' | 'spread';

export interface CountryCounts {
	unesco: number;
	notable: number;
	byCategory: Record<Category, number>;
}

export interface CountrySpread {
	level: SpreadLevel;
	medianKm: number;
}

export interface CountryClimate {
	tempC: number[];
	precipMm: number[];
	comfortable: boolean[];
}

export interface CountryCost {
	tier: 1 | 2 | 3 | 4 | 5;
	priceLevelRatio: number;
	year: number;
}

export interface CountrySafety {
	level: 1 | 2 | 3 | 4;
	label: string;
	url: string;
	asOf: string;
}

export interface CountryTraditions {
	count: number;
	examples: string[];
}

export interface CountrySummary {
	iso3: string;
	name: string;
	aliases: string[];
	teaser: string;
	bbox: [number, number, number, number];
	counts: CountryCounts;
	richness: number;
	richnessRaw: number;
	spread: CountrySpread | null;
	climate: CountryClimate | null;
	cost: CountryCost | null;
	safety: CountrySafety | null;
	traditions: CountryTraditions;
}

export interface CountriesPayload {
	generatedAt: string;
	countries: CountrySummary[];
}

export interface SiteImage {
	thumbUrl: string;
	author: string;
	license: string;
	sourceUrl: string;
}

export interface SiteProperties {
	siteId: string;
	name: string;
	category: Category;
	unesco: boolean;
	inDanger: boolean;
	yearInscribed: number | null;
	fame: number;
	fameLevel: FameLevel;
	summary: string;
	summarySource: 'unesco' | 'wikipedia' | null;
	image: SiteImage | null;
	wikipediaUrl: string | null;
	unescoUrl: string | null;
	wikidataId: string | null;
	countries: string[];
}

export interface SiteFeature {
	type: 'Feature';
	id: number;
	geometry: {
		type: 'Point';
		coordinates: [number, number];
	};
	properties: SiteProperties;
}

export interface SitesFeatureCollection {
	type: 'FeatureCollection';
	features: SiteFeature[];
}
