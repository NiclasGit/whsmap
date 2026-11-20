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

export interface CameraPadding {
	top: number;
	bottom: number;
	left: number;
	right: number;
}

export interface WorldCameraSpec {
	center: [number, number];
	zoom: number;
	padding: CameraPadding;
}

const MOBILE_BREAKPOINT = 768;
const GLOBE_BASE_DIAMETER_PX = 512 / Math.PI;

export function getWorldCamera(viewportWidth: number, viewportHeight: number): WorldCameraSpec {
	if (viewportWidth >= MOBILE_BREAKPOINT) {
		return {
			center: [18, 24],
			zoom: 1.75,
			padding: { top: 0, bottom: 0, left: 0, right: 0 }
		};
	}

	const topPad = viewportHeight < 500 ? 96 : 124;
	const bottomPad = viewportHeight < 500 ? 56 : 78;
	const usableWidth = Math.max(180, viewportWidth - 24);
	const usableHeight = Math.max(160, viewportHeight - topPad - bottomPad);
	const limitingDim = Math.min(usableWidth, usableHeight);
	const targetDiameter = limitingDim * 0.82;
	const rawZoom = Math.log2(targetDiameter / GLOBE_BASE_DIAMETER_PX);
	const zoom = Math.max(0.25, Math.min(1.5, Number(rawZoom.toFixed(2))));

	return {
		center: [18, 20],
		zoom,
		padding: { top: topPad, bottom: bottomPad, left: 0, right: 0 }
	};
}

export function getCountryFitPadding(viewportWidth: number, viewportHeight: number): CameraPadding {
	if (viewportWidth >= MOBILE_BREAKPOINT) {
		return { top: 64, bottom: 64, left: 64, right: 440 };
	}
	const bottom = Math.min(280, Math.max(140, Math.round(viewportHeight * 0.4)));
	return { top: 36, bottom, left: 24, right: 24 };
}

export function shouldReduceMotion(): boolean {
	if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
		return false;
	}
	return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}
