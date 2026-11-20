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
	let mobileSheetExpanded = $state(false);
	let touchStartY = 0;

	let top5 = $derived(getTopCountries(countries, 5));
	let searchResults = $derived(searchCountries(countries, searchQuery, 6));

	$effect(() => {
		searchResults;
		activeIndex = 0;
	});

	$effect(() => {
		if (!activeCountry) {
			mobileSheetExpanded = false;
		}
	});

	function chooseFromSearch(iso3: string) {
		searchQuery = '';
		searchFocused = false;
		mobileSheetExpanded = false;
		onSelectCountry(iso3);
	}

	function handleSheetTouchStart(e: TouchEvent) {
		touchStartY = e.touches[0]?.clientY ?? 0;
	}

	function handleSheetTouchEnd(e: TouchEvent) {
		const endY = e.changedTouches[0]?.clientY ?? touchStartY;
		const deltaY = endY - touchStartY;
		if (deltaY < -30) {
			mobileSheetExpanded = true;
		} else if (deltaY > 30) {
			if (activeCountry) {
				onHoverCountry(null);
			} else {
				mobileSheetExpanded = false;
			}
		}
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
			onfocus={() => {
				searchFocused = true;
				mobileSheetExpanded = false;
			}}
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

<aside
	class="world-panel glass-panel"
	class:mobile-expanded={mobileSheetExpanded}
	class:has-active-country={Boolean(activeCountry)}
	aria-live="polite"
>
	{#if activeCountry}
		<button
			type="button"
			class="mobile-drag-zone"
			aria-label="Dismiss country preview"
			onclick={() => onHoverCountry(null)}
			ontouchstart={handleSheetTouchStart}
			ontouchend={handleSheetTouchEnd}
		>
			<span class="drag-pill" aria-hidden="true"></span>
		</button>
		<div class="active-head">
			<div>
				<div class="kicker">Country</div>
				<h2>{activeCountry.name}</h2>
			</div>
			<button
				type="button"
				class="mobile-dismiss-btn"
				aria-label="Close country preview"
				onclick={() => onHoverCountry(null)}
			>
				✕
			</button>
		</div>
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
		<button
			type="button"
			class="mobile-sheet-toggle"
			aria-expanded={mobileSheetExpanded}
			aria-controls="world-explore-sheet-body"
			onclick={() => (mobileSheetExpanded = !mobileSheetExpanded)}
			ontouchstart={handleSheetTouchStart}
			ontouchend={handleSheetTouchEnd}
		>
			<span class="drag-pill" aria-hidden="true"></span>
			<span class="toggle-row">
				<span class="toggle-copy">
					<span class="kicker">Start exploring</span>
					<span class="toggle-hint">Tap a country or view top destinations</span>
				</span>
				<span class="toggle-chip">{mobileSheetExpanded ? 'Hide ▼' : 'Explore ▲'}</span>
			</span>
		</button>

		<div id="world-explore-sheet-body" class="sheet-body">
			<div class="kicker desktop-only">Start exploring</div>
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
			<div class="mobile-legend">
				<span class="kicker">Heritage richness</span>
				<div class="legend-bar"></div>
				<div class="mobile-legend-labels">
					<span>fewer sites</span>
					<span>more sites</span>
				</div>
			</div>
		</div>
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
		z-index: 20;
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

	.mobile-sheet-toggle,
	.mobile-drag-zone,
	.mobile-dismiss-btn,
	.mobile-legend {
		display: none;
	}

	.active-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
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
			left: 14px;
			right: 14px;
			top: calc(12px + env(safe-area-inset-top, 0px));
			max-width: none;
		}

		h1 {
			font-size: clamp(24px, 6.8vw, 30px);
		}

		.subtitle {
			margin: 3px 0 10px;
			font-size: 12px;
		}

		.search-wrap {
			width: 100%;
		}

		.search-input {
			font-size: 16px;
			padding: 9px 14px;
		}

		.search-option {
			padding: 10px 12px;
			min-height: 42px;
		}

		.world-panel {
			left: 12px;
			right: 12px;
			bottom: calc(12px + env(safe-area-inset-bottom, 0px));
			top: auto;
			transform: none;
			width: auto;
			padding: 10px 14px 12px;
			border-radius: 18px;
			max-height: 58dvh;
			overflow-y: auto;
			-webkit-overflow-scrolling: touch;
			transition: padding 0.2s ease;
		}

		.world-panel.mobile-expanded,
		.world-panel.has-active-country {
			padding: 10px 16px 16px;
		}

		.mobile-drag-zone {
			display: flex;
			justify-content: center;
			width: 100%;
			padding: 2px 0 8px;
			border: 0;
			background: transparent;
			cursor: pointer;
		}

		.drag-pill {
			display: block;
			width: 36px;
			height: 4px;
			border-radius: 999px;
			background: rgba(243, 211, 139, 0.35);
			margin: 0 auto 8px;
		}

		.mobile-drag-zone .drag-pill {
			margin-bottom: 0;
		}

		.mobile-sheet-toggle {
			display: block;
			width: 100%;
			padding: 0;
			border: 0;
			background: transparent;
			color: var(--text-primary);
			text-align: left;
			cursor: pointer;
		}

		.toggle-row {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 10px;
		}

		.toggle-copy {
			display: flex;
			flex-direction: column;
			gap: 2px;
			min-width: 0;
		}

		.toggle-hint {
			font-size: 12px;
			color: var(--text-secondary);
			white-space: nowrap;
			overflow: hidden;
			text-overflow: ellipsis;
		}

		.toggle-chip {
			flex-shrink: 0;
			padding: 6px 12px;
			border-radius: 999px;
			border: 1px solid var(--gold-soft);
			background: rgba(243, 211, 139, 0.14);
			color: var(--gold-bright);
			font-size: 12px;
			font-weight: 600;
		}

		.desktop-only {
			display: none;
		}

		.sheet-body {
			display: none;
			margin-top: 12px;
			padding-top: 12px;
			border-top: 1px solid rgba(255, 255, 255, 0.08);
		}

		.world-panel.mobile-expanded .sheet-body {
			display: block;
		}

		.mobile-dismiss-btn {
			display: grid;
			place-items: center;
			width: 32px;
			height: 32px;
			border-radius: 50%;
			border: 1px solid rgba(255, 255, 255, 0.18);
			background: rgba(255, 255, 255, 0.06);
			color: var(--text-primary);
			cursor: pointer;
			flex-shrink: 0;
		}

		h2 {
			font-size: 26px;
			margin: 2px 0 4px;
		}

		.stat-row {
			gap: 20px;
			margin: 8px 0 4px;
		}

		.big-num {
			font-size: 30px;
		}

		.big-num.secondary {
			font-size: 24px;
			padding-top: 5px;
		}

		.teaser {
			font-size: 13px;
			line-height: 1.45;
			margin: 8px 0 10px;
		}

		.world-panel.has-active-country .teaser {
			display: -webkit-box;
			-webkit-line-clamp: 2;
			line-clamp: 2;
			-webkit-box-orient: vertical;
			overflow: hidden;
		}

		.explore-btn {
			width: 100%;
			text-align: center;
			padding: 12px 18px;
			margin-top: 2px;
		}

		.top-heading {
			margin-top: 12px;
		}

		.top-item {
			padding: 9px 8px;
			min-height: 40px;
		}

		.mobile-legend {
			display: block;
			margin-top: 14px;
			padding-top: 12px;
			border-top: 1px solid rgba(255, 255, 255, 0.08);
		}

		.mobile-legend .legend-bar {
			width: 100%;
		}

		.mobile-legend-labels {
			display: flex;
			justify-content: space-between;
			font-size: 11px;
			color: var(--text-muted);
		}

		.world-legend {
			display: none;
		}
	}
</style>
