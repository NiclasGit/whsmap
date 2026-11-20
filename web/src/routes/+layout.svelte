<script lang="ts">
	import '../app.css';
	import { goto } from '$app/navigation';
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import type {
		Category,
		CountrySummary,
		SiteFeature,
		SitesFeatureCollection
	} from '$lib/data/types';
	import { createSitesLoader } from '$lib/data/loader';
	import { resolveRouteState } from '$lib/data/routing';
	import { reconciledSelectedSiteId } from '$lib/components/panel-helpers';
	import AtlasMap from '$lib/components/AtlasMap.svelte';
	import WorldPanel from '$lib/components/WorldPanel.svelte';
	import CountryPanel from '$lib/components/CountryPanel.svelte';
	import SiteCard from '$lib/components/SiteCard.svelte';

	let { data, children } = $props();

	const sitesLoader = createSitesLoader();

	let hoveredCountryIso3 = $state<string | null>(null);
	let hoveredSiteId = $state<string | null>(null);
	let activeCategory = $state<Category | null>(null);
	let currentSites = $state<SitesFeatureCollection | null>(null);
	let loadingSites = $state(false);
	let loadedCountryIso3 = $state<string | null>(null);

	let routeState = $derived(
		resolveRouteState(data.countries, {
			iso3: page.params.iso3,
			siteId: page.params.siteId
		})
	);

	let activeWorldCountry: CountrySummary | null = $derived(
		hoveredCountryIso3
			? (data.countries.find((c: CountrySummary) => c.iso3 === hoveredCountryIso3) ?? null)
			: null
	);

	let selectedSite: SiteFeature | null = $derived(
		routeState.siteId &&
			currentSites &&
			loadedCountryIso3 === routeState.country?.iso3
			? (currentSites.features.find((f) => f.properties.siteId === routeState.siteId) ?? null)
			: null
	);

	$effect(() => {
		const targetIso = routeState.country?.iso3 ?? null;
		if (!targetIso) {
			currentSites = null;
			loadedCountryIso3 = null;
			loadingSites = false;
			activeCategory = null;
			return;
		}
		if (targetIso === loadedCountryIso3) {
			return;
		}

		loadedCountryIso3 = targetIso;
		currentSites = null;
		activeCategory = null;
		loadingSites = true;
		sitesLoader.loadCountrySites(targetIso).then((fc) => {
			if (fc !== null && loadedCountryIso3 === targetIso) {
				currentSites = fc;
				loadingSites = false;
			}
		});
	});

	function navigateToWorld() {
		hoveredCountryIso3 = null;
		hoveredSiteId = null;
		goto(`${base}/`);
	}

	function navigateToCountry(iso3: string) {
		hoveredCountryIso3 = null;
		hoveredSiteId = null;
		goto(`${base}/country/${iso3.toUpperCase()}`);
	}

	function navigateToSite(siteId: string) {
		const iso3 = routeState.country?.iso3;
		if (!iso3) return;
		goto(`${base}/country/${iso3}/site/${encodeURIComponent(siteId)}`);
	}

	function handleToggleCategory(cat: Category | null) {
		activeCategory = cat;
		if (routeState.country && routeState.siteId && currentSites) {
			const kept = reconciledSelectedSiteId(
				currentSites.features,
				cat,
				routeState.siteId
			);
			if (!kept) {
				goto(`${base}/country/${routeState.country.iso3}`);
			}
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key !== 'Escape') return;
		if (routeState.siteId && routeState.country) {
			goto(`${base}/country/${routeState.country.iso3}`);
		} else if (routeState.status !== 'world') {
			navigateToWorld();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<main class="atlas-shell" class:has-site-card={Boolean(selectedSite)}>
	<AtlasMap
		countries={data.countries}
		selectedCountry={routeState.country}
		{hoveredCountryIso3}
		sites={currentSites}
		{activeCategory}
		selectedSiteId={routeState.siteId}
		{hoveredSiteId}
		onHoverCountry={(iso) => (hoveredCountryIso3 = iso)}
		onSelectCountry={navigateToCountry}
		onSelectSite={navigateToSite}
		onHoverSite={(id) => (hoveredSiteId = id)}
	/>

	{#if routeState.status === 'world'}
		<WorldPanel
			countries={data.countries}
			activeCountry={activeWorldCountry}
			onSelectCountry={navigateToCountry}
			onHoverCountry={(iso) => (hoveredCountryIso3 = iso)}
		/>
	{:else if routeState.status === 'country' && routeState.country}
		<div class="country-panel-holder">
			<CountryPanel
				country={routeState.country}
				sites={currentSites}
				{loadingSites}
				{activeCategory}
				selectedSiteId={routeState.siteId}
				{hoveredSiteId}
				onBackToWorld={navigateToWorld}
				onToggleCategory={handleToggleCategory}
				onSelectSite={navigateToSite}
				onHoverSite={(id) => (hoveredSiteId = id)}
			/>
		</div>
		{#if selectedSite}
			<SiteCard
				site={selectedSite}
				onClose={() => goto(`${base}/country/${routeState.country!.iso3}`)}
			/>
		{:else if routeState.siteId && !loadingSites && currentSites !== null && loadedCountryIso3 === routeState.country.iso3}
			<div class="not-found-toast glass-panel" role="status">
				<span>Site "{routeState.siteId}" not found in {routeState.country.name}.</span>
				<button
					type="button"
					class="toast-btn"
					onclick={() => goto(`${base}/country/${routeState.country!.iso3}`)}
				>
					Dismiss
				</button>
			</div>
		{/if}
	{:else if routeState.status === 'not-found'}
		<div class="not-found-modal glass-panel" role="alert">
			<div class="kicker">Destination unavailable</div>
			<h2>Country not found</h2>
			<p>We couldn't find a country matching "{page.params.iso3}" in the atlas.</p>
			<button type="button" class="back-world-btn" onclick={navigateToWorld}>
				← Back to world globe
			</button>
		</div>
	{/if}

	{@render children()}
</main>

<style>
	.atlas-shell {
		position: relative;
		width: 100vw;
		height: 100vh;
		overflow: hidden;
	}

	.not-found-modal {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		padding: 28px;
		width: 360px;
		z-index: 20;
		text-align: center;
	}

	.not-found-modal h2 {
		font-family: var(--font-serif);
		font-size: 34px;
		margin: 8px 0;
	}

	.not-found-modal p {
		font-size: 14px;
		color: var(--text-secondary);
		margin-bottom: 18px;
	}

	.back-world-btn {
		padding: 10px 18px;
		border-radius: 999px;
		border: 0;
		background: var(--gold-bright);
		color: #091326;
		font-weight: 600;
		cursor: pointer;
	}

	.not-found-toast {
		position: absolute;
		left: 24px;
		bottom: 24px;
		padding: 12px 16px;
		z-index: 16;
		display: flex;
		align-items: center;
		gap: 12px;
		font-size: 13px;
	}

	.toast-btn {
		padding: 5px 10px;
		border-radius: 999px;
		border: 1px solid var(--gold-soft);
		background: transparent;
		color: var(--gold-bright);
		cursor: pointer;
		font-size: 12px;
	}

	@media (max-width: 767px) {
		.atlas-shell.has-site-card .country-panel-holder {
			display: none;
		}
	}
</style>
