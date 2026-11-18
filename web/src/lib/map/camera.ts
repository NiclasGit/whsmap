import type { FilterSpecification } from 'maplibre-gl';

export function bboxToCameraBounds(
	bbox: [number, number, number, number],
	minSpanDeg = 0.6
): [[number, number], [number, number]] {
	let [west, south, east, north] = bbox;
	if (west > east) {
		east += 360;
	}

	const width = east - west;
	if (width < minSpanDeg) {
		const midX = (west + east) / 2;
		west = midX - minSpanDeg / 2;
		east = midX + minSpanDeg / 2;
	}

	const height = north - south;
	if (height < minSpanDeg) {
		const midY = (south + north) / 2;
		south = Math.max(-85, midY - minSpanDeg / 2);
		north = Math.min(85, midY + minSpanDeg / 2);
	}

	return [
		[west, south],
		[east, north]
	];
}

export function buildWorldDimFilter(selectedIso3: string | null): FilterSpecification {
	if (!selectedIso3) {
		return ['==', ['get', 'iso3'], '__NONE__'];
	}
	return ['!=', ['get', 'iso3'], selectedIso3.toUpperCase()];
}

export function shouldReduceMotion(): boolean {
	if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
		return false;
	}
	return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}
