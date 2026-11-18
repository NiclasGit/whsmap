import { describe, expect, it } from 'vitest';
import { CATEGORY_META, CATEGORY_ORDER, FAME_LABELS } from './categories';

describe('categories and fame constants', () => {
	it('defines the exact 8 categories in contract display order', () => {
		expect(CATEGORY_ORDER).toEqual([
			'ancient',
			'sacred',
			'castles',
			'towns',
			'palaces',
			'landscapes',
			'modern',
			'natural'
		]);
		for (const cat of CATEGORY_ORDER) {
			expect(CATEGORY_META[cat].label.length).toBeGreaterThan(0);
			expect(CATEGORY_META[cat].color).toMatch(/^#[0-9a-fA-F]{6}$/);
		}
	});

	it('maps all 4 fame levels from hidden gem to world-famous', () => {
		expect(FAME_LABELS[1]).toBe('Hidden gem');
		expect(FAME_LABELS[4]).toBe('World-famous');
	});
});
