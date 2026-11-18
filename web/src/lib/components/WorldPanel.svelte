<script lang="ts">
	import type { CountrySummary } from '$lib/data/types';
	import { getTopCountries } from '$lib/data/richness';
	import { searchCountries } from '$lib/data/search';

	interface Props {
		countries: CountrySummary[];
		activeCountry: CountrySummary | null;
		onSelectCountry: (iso3: string) => void;
		onHoverCountry: (iso3: string | null) => void;
	}

	let {
		countries,
		activeCountry,
		onSelectCountry,
		onHoverCountry
	}: Props = $props();

	let searchQuery = $state('');
	let searchFocused = $state(false);
	let activeIndex = $state(0);

	let top5 = $derived(getTopCountries(countries, 5));
	let searchResults = $derived(searchCountries(countries, searchQuery, 6));

	$effect(() => {
		searchResults;
		activeIndex = 0;
	});

	function chooseFromSearch(iso3: string) {
		searchQuery = '';
		searchFocused = false;
		onSelectCountry(iso3);
	}

	function handleSearchKeydown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown' && searchResults.length > 0) {
			e.preventDefault();
			activeIndex = (activeIndex + 1) % searchResults.length;
		} else if (e.key === 'ArrowUp' && searchResults.length > 0) {
			e.preventDefault();
			activeIndex = (activeIndex - 1 + searchResults.length) % searchResults.length;
		} else if (e.key === 'Enter' && searchResults.length > 0) {
			e.preventDefault();
			const pick = searchResults[activeIndex] ?? searchResults[0];
			chooseFromSearch(pick.iso3);
		} else if (e.key === 'Escape') {
			searchFocused = false;
		}
	}
</script>

<header class="world-header">
	<h1>The World's Heritage</h1>
	<p class="subtitle">Drag to spin · brighter countries hold more heritage</p>

	<div class="search-wrap">
		<input
			type="search"
			class="search-input"
			placeholder="Search a country (e.g. Italy, Japan, Peru)…"
			aria-label="Search a country"
			role="combobox"
			aria-expanded={searchFocused && searchResults.length > 0}
			aria-controls="country-search-listbox"
			bind:value={searchQuery}
			onfocus={() => (searchFocused = true)}
			onblur={() => setTimeout(() => (searchFocused = false), 150)}
			onkeydown={handleSearchKeydown}
		/>
		{#if searchFocused && searchResults.length > 0}
			<ul id="country-search-listbox" class="search-dropdown glass-panel" role="listbox">
				{#each searchResults as item, idx (item.iso3)}
					<li role="option" aria-selected={idx === activeIndex}>
						<button
							type="button"
							class="search-option"
							class:highlighted={idx === activeIndex}
							onmousedown={(e) => e.preventDefault()}
							onclick={() => chooseFromSearch(item.iso3)}
						>
							<span class="opt-name">{item.name}</span>
							<span class="opt-meta"
								>{item.counts.unesco} UNESCO · {item.counts.notable} notable</span
							>
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</header>

<aside class="world-panel glass-panel" aria-live="polite">
	{#if activeCountry}
		<div class="kicker">Country</div>
		<h2>{activeCountry.name}</h2>
		<div class="stat-row">
			<div>
				<div class="big-num">{activeCountry.counts.unesco}</div>
				<div class="kicker">World Heritage Sites</div>
			</div>
			<div>
				<div class="big-num secondary">{activeCountry.counts.notable}</div>
				<div class="kicker">Notable Landmarks</div>
			</div>
		</div>
		<p class="teaser">{activeCountry.teaser}</p>
		<button
			type="button"
			class="explore-btn"
			onclick={() => onSelectCountry(activeCountry.iso3)}
		>
			Explore {activeCountry.name} →
		</button>
	{:else}
		<div class="kicker">Start exploring</div>
		<h2>Where to next?</h2>
		<p class="teaser">
			Every glowing country is a story. Hover or tap one to see what it holds for a cultural
			traveler.
		</p>
		<div class="kicker top-heading">Most heritage sites</div>
		<ol class="top-list">
			{#each top5 as c (c.iso3)}
				<li>
					<button
						type="button"
						class="top-item"
						onmouseenter={() => onHoverCountry(c.iso3)}
						onclick={() => onSelectCountry(c.iso3)}
					>
						<span class="top-name">{c.name}</span>
						<span class="top-count"
							>{c.counts.unesco} UNESCO · {c.counts.notable} notable</span
						>
					</button>
				</li>
			{/each}
		</ol>
	{/if}
</aside>

<div class="world-legend">
	<span>Heritage richness</span>
	<div class="legend-bar"></div>
	<span>fewer sites ⟶ more sites</span>
</div>

<style>
	.world-header {
		position: absolute;
		left: 42px;
		top: 28px;
		z-index: 10;
		max-width: 420px;
		pointer-events: none;
	}

	h1 {
		margin: 0;
		font-family: var(--font-serif);
		font-weight: 600;
		font-size: 46px;
		color: var(--gold-bright);
		letter-spacing: 0.5px;
		line-height: 1.05;
	}

	.subtitle {
		margin: 6px 0 14px;
		color: var(--text-muted);
		font-size: 14px;
	}

	.search-wrap {
		position: relative;
		pointer-events: auto;
		width: 320px;
	}

	.search-input {
		width: 100%;
		padding: 10px 14px;
		border-radius: 999px;
		border: 1px solid var(--gold-soft);
		background: rgba(10, 20, 42, 0.78);
		backdrop-filter: blur(10px);
		color: var(--text-primary);
		font-size: 13px;
		outline: none;
	}

	.search-input:focus {
		border-color: var(--gold-bright);
	}

	.search-dropdown {
		position: absolute;
		top: calc(100% + 6px);
		left: 0;
		right: 0;
		margin: 0;
		padding: 6px;
		list-style: none;
		border-radius: 14px;
	}

	.search-option {
		width: 100%;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 10px;
		background: transparent;
		border: 0;
		color: var(--text-primary);
		cursor: pointer;
		border-radius: 8px;
		text-align: left;
		font-size: 13px;
	}

	.search-option:hover,
	.search-option.highlighted {
		background: rgba(243, 211, 139, 0.16);
	}

	.opt-meta {
		font-size: 11px;
		color: var(--text-muted);
	}

	.world-panel {
		position: absolute;
		right: 36px;
		top: 50%;
		transform: translateY(-50%);
		width: 350px;
		padding: 26px;
		z-index: 10;
	}

	h2 {
		font-family: var(--font-serif);
		font-size: 38px;
		margin: 6px 0 4px;
		color: #fff;
		font-weight: 600;
		line-height: 1.1;
	}

	.stat-row {
		display: flex;
		gap: 24px;
		margin: 12px 0 6px;
	}

	.big-num {
		font-size: 46px;
		font-weight: 700;
		color: var(--gold-bright);
		line-height: 1;
		margin-bottom: 4px;
	}

	.big-num.secondary {
		color: var(--text-secondary);
		font-size: 36px;
		padding-top: 8px;
	}

	.teaser {
		color: var(--text-secondary);
		line-height: 1.55;
		font-size: 14px;
		margin: 12px 0;
	}

	.explore-btn {
		display: inline-block;
		margin-top: 6px;
		padding: 11px 20px;
		border-radius: 999px;
		border: 0;
		background: var(--gold-bright);
		color: #0b1730;
		font-weight: 600;
		font-size: 14px;
		cursor: pointer;
	}

	.explore-btn:hover {
		filter: brightness(1.08);
	}

	.top-heading {
		margin-top: 18px;
	}

	.top-list {
		margin: 10px 0 0;
		padding-left: 18px;
		color: var(--text-secondary);
		font-size: 14px;
	}

	.top-item {
		width: 100%;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 6px 8px;
		background: transparent;
		border: 0;
		color: var(--text-primary);
		cursor: pointer;
		border-radius: 8px;
		font-size: 13px;
	}

	.top-item:hover {
		background: rgba(243, 211, 139, 0.12);
	}

	.top-count {
		color: var(--text-muted);
		font-size: 12px;
	}

	.world-legend {
		position: absolute;
		left: 42px;
		bottom: 30px;
		font-size: 12px;
		color: var(--text-muted);
		z-index: 10;
		pointer-events: none;
	}

	.legend-bar {
		width: 220px;
		height: 8px;
		border-radius: 4px;
		background: linear-gradient(90deg, var(--country-low), var(--country-high));
		margin: 6px 0;
	}

	@media (max-width: 767px) {
		.world-header {
			left: 18px;
			right: 18px;
			top: 16px;
		}
		h1 {
			font-size: 32px;
		}
		.search-wrap {
			width: 100%;
		}
		.world-panel {
			left: 14px;
			right: 14px;
			bottom: 16px;
			top: auto;
			transform: none;
			width: auto;
			padding: 18px;
		}
		.world-legend {
			display: none;
		}
	}
</style>
