import type { Category, FameLevel } from './types';

export const CATEGORY_ORDER: readonly Category[] = [
	'ancient',
	'sacred',
	'castles',
	'towns',
	'palaces',
	'landscapes',
	'modern',
	'natural'
] as const;

export interface CategoryMeta {
	label: string;
	shortLabel: string;
	color: string;
	glyph: string;
	iconSvg: string;
}

export const CATEGORY_META: Record<Category, CategoryMeta> = {
	ancient: {
		label: 'Ancient & Archaeological',
		shortLabel: 'Ancient',
		color: '#e6a15c',
		glyph: '◆',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h16M6 20V9m4 11V9m4 11V9m4 11V9M3 9h18L12 4 3 9Z"/></svg>'
	},
	sacred: {
		label: 'Sacred Places',
		shortLabel: 'Sacred',
		color: '#d988b9',
		glyph: '▲',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3v4m-2-2h4m-7 15V11l5-4 5 4v9M4 20h16"/></svg>'
	},
	castles: {
		label: 'Castles & Forts',
		shortLabel: 'Castles',
		color: '#e06d53',
		glyph: '⛫',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20V7h3v2h2V7h6v2h2V7h3v13M9 20v-5h6v5"/></svg>'
	},
	towns: {
		label: 'Historic Towns',
		shortLabel: 'Old Towns',
		color: '#f2c166',
		glyph: '⬢',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 20v-9l6-5 6 5v9m0 0h6v-7l-3-3-3 3m-6 7v-4h-2v4"/></svg>'
	},
	palaces: {
		label: 'Palaces & Architecture',
		shortLabel: 'Palaces',
		color: '#b892ff',
		glyph: '❖',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 20h18M5 20v-8h14v8M8 12V8a4 4 0 0 1 8 0v4m-4-7V3"/></svg>'
	},
	landscapes: {
		label: 'Cultural Landscapes',
		shortLabel: 'Landscapes',
		color: '#7cc68d',
		glyph: '✦',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 18c3-3 6-3 9 0s6 3 9 0M3 13c4-4 8-4 12 0 2-2 4-2 6 0"/></svg>'
	},
	modern: {
		label: 'Industrial & Modern',
		shortLabel: 'Modern',
		color: '#6bb8d9',
		glyph: '⚙',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 20h18M5 20V9l5 3V9l5 3V6h4v14"/></svg>'
	},
	natural: {
		label: 'Natural Wonders',
		shortLabel: 'Natural',
		color: '#4ecdc4',
		glyph: '●',
		iconSvg:
			'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m3 20 6-11 4 6 3-4 5 9H3Z"/></svg>'
	}
};

export const FAME_LABELS: Record<FameLevel, string> = {
	1: 'Hidden gem',
	2: 'Notable landmark',
	3: 'Renowned site',
	4: 'World-famous'
};
