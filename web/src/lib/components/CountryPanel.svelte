<script lang="ts">
	import type {
		Category,
		CountrySummary,
		SiteFeature,
		SitesFeatureCollection
	} from '$lib/data/types';
	import { CATEGORY_META, CATEGORY_ORDER, FAME_LABELS } from '$lib/data/categories';
	import {
		filterSitesByCategory,
		formatCostTier,
		MONTH_LABELS,
		MONTH_NAMES,
		SPREAD_DESCRIPTIONS
	} from './panel-helpers';

	interface Props {
		country: CountrySummary;
		sites: SitesFeatureCollection | null;
		loadingSites: boolean;
		activeCategory: Category | null;
		selectedSiteId: string | null;
		hoveredSiteId: string | null;
		onBackToWorld: () => void;
		onToggleCategory: (cat: Category | null) => void;
		onSelectSite: (siteId: string) => void;
		onHoverSite: (siteId: string | null) => void;
	}

	let {
		country,
		sites,
		loadingSites,
		activeCategory,
		selectedSiteId,
		hoveredSiteId,
		onBackToWorld,
		onToggleCategory,
		onSelectSite,
		onHoverSite
	}: Props = $props();

	let visibleSites: SiteFeature[] = $derived(
		filterSitesByCategory(sites?.features ?? [], activeCategory)
	);

	let mobileCollapsed = $state(false);
	let touchStartY = 0;

	$effect(() => {
		country.iso3;
		mobileCollapsed = false;
	});

	function handleTouchStart(e: TouchEvent) {
		touchStartY = e.touches[0]?.clientY ?? 0;
	}

	function handleTouchEnd(e: TouchEvent) {
		const endY = e.changedTouches[0]?.clientY ?? touchStartY;
		const deltaY = endY - touchStartY;
		if (deltaY > 30) {
			mobileCollapsed = true;
		} else if (deltaY < -30) {
			mobileCollapsed = false;
		}
	}
</script>

<aside
	class="country-panel glass-panel"
	class:mobile-collapsed={mobileCollapsed}
	aria-label="{country.name} heritage overview"
>
	<div class="panel-top">
		<button
			type="button"
			class="mobile-drag-handle"
			aria-label={mobileCollapsed ? 'Expand country details' : 'Collapse country details'}
			aria-expanded={!mobileCollapsed}
			onclick={() => (mobileCollapsed = !mobileCollapsed)}
			ontouchstart={handleTouchStart}
			ontouchend={handleTouchEnd}
		>
			<span class="mobile-drag-pill" aria-hidden="true"></span>
		</button>
		<div class="top-controls">
			<button type="button" class="back-btn" onclick={onBackToWorld}>← Back to globe</button>
			<button
				type="button"
				class="mobile-collapse-btn"
				aria-expanded={!mobileCollapsed}
				onclick={() => (mobileCollapsed = !mobileCollapsed)}
			>
				{mobileCollapsed ? 'Details ▲' : 'Map ▼'}
			</button>
		</div>
		<div class="title-block">
			<h2>{country.name}</h2>
			<div class="badge-row">
				<span class="pill unesco-pill">★ {country.counts.unesco} World Heritage</span>
				<span class="pill notable-pill">◆ {country.counts.notable} Notable Sites</span>
			</div>
			<p class="teaser">{country.teaser}</p>
		</div>
	</div>

	<div class="country-panel-details">

	<section class="panel-section">
		<div class="sec-head">
			<span class="kicker">Heritage by category</span>
			{#if activeCategory}
				<button type="button" class="clear-btn" onclick={() => onToggleCategory(null)}>
					Show all
				</button>
			{/if}
		</div>
		<div class="cat-grid">
			{#each CATEGORY_ORDER as cat (cat)}
				{@const meta = CATEGORY_META[cat]}
				{@const count = country.counts.byCategory[cat] ?? 0}
				<button
					type="button"
					class="cat-chip"
					class:active={activeCategory === cat}
					disabled={count === 0}
					onclick={() => onToggleCategory(activeCategory === cat ? null : cat)}
				>
					<span class="cat-dot" style="background:{meta.color}">{meta.glyph}</span>
					<span class="cat-name">{meta.shortLabel}</span>
					<span class="cat-count">{count}</span>
				</button>
			{/each}
		</div>
	</section>

	<section class="panel-section practical-box">
		<div class="kicker">What to expect</div>

		<div class="prac-grid">
			{#if country.spread}
				<div class="prac-item">
					<span class="prac-label">Site layout</span>
					<span class="prac-val">
						{SPREAD_DESCRIPTIONS[country.spread.level]} (~{country.spread.medianKm} km median)
					</span>
				</div>
			{/if}

			{#if country.cost}
				<div class="prac-item">
					<span class="prac-label">Cost level</span>
					<span class="prac-val cost-tier" title="World Bank price level index">
						{formatCostTier(country.cost.tier)}
					</span>
				</div>
			{/if}

			{#if country.safety}
				<div class="prac-item">
					<span class="prac-label">Travel advisory</span>
					<span class="prac-val">
						<a href={country.safety.url} target="_blank" rel="noopener noreferrer">
							Level {country.safety.level}: {country.safety.label}
						</a>
						<small class="as-of">(as of {country.safety.asOf})</small>
					</span>
				</div>
			{/if}
		</div>

		{#if country.climate}
			<div class="climate-block">
				<span class="prac-label">Best months to visit</span>
				<div class="month-strip" role="list" aria-label="Monthly weather comfort">
					{#each MONTH_LABELS as mLabel, idx}
						{@const isGood = country.climate.comfortable[idx]}
						<div
							role="listitem"
							class="month-cell"
							class:comfortable={isGood}
							title="{MONTH_NAMES[idx]}: {country.climate.tempC[idx]}°C, {country.climate.precipMm[idx]} mm"
						>
							{mLabel}
						</div>
					{/each}
				</div>
			</div>
		{/if}

		{#if country.traditions.count > 0}
			<div class="traditions-block">
				<span class="prac-label"
					>Living traditions ({country.traditions.count} UNESCO Intangible Heritage)</span
				>
				<div class="trad-tags">
					{#each country.traditions.examples as ex}
						<span class="trad-tag">{ex}</span>
					{/each}
				</div>
			</div>
		{/if}
	</section>

	<section class="panel-section sites-section">
		<div class="sec-head">
			<span class="kicker">
				Sites to explore ({visibleSites.length})
			</span>
		</div>

		{#if loadingSites}
			<p class="muted-note">Loading heritage sites…</p>
		{:else if visibleSites.length === 0}
			<p class="muted-note">No sites listed for this filter.</p>
		{:else}
			<ul class="site-list">
				{#each visibleSites as feat (feat.properties.siteId)}
					{@const p = feat.properties}
					{@const meta = CATEGORY_META[p.category]}
					<li>
						<button
							type="button"
							class="site-row"
							class:selected={selectedSiteId === p.siteId}
							class:hovered={hoveredSiteId === p.siteId}
							onmouseenter={() => onHoverSite(p.siteId)}
							onmouseleave={() => onHoverSite(null)}
							onclick={() => onSelectSite(p.siteId)}
						>
							<span class="site-marker" style="background:{meta.color}">
								{p.unesco ? '★' : meta.glyph}
							</span>
							<span class="site-main">
								<span class="site-title">{p.name}</span>
								<span class="site-sub">
									{meta.shortLabel} · {FAME_LABELS[p.fameLevel]}
									{#if p.unesco}
										· <strong class="unesco-tag">UNESCO</strong>
									{/if}
								</span>
							</span>
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</section>
	</div>
</aside>

<style>
	.country-panel {
		position: absolute;
		top: 18px;
		right: 18px;
		bottom: 18px;
		width: 410px;
		z-index: 12;
		display: flex;
		flex-direction: column;
		padding: 20px;
		overflow-y: auto;
	}

	.mobile-drag-handle,
	.mobile-collapse-btn {
		display: none;
	}

	.top-controls {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
	}

	.back-btn {
		background: transparent;
		border: 1px solid var(--gold-soft);
		color: var(--gold-bright);
		padding: 6px 12px;
		border-radius: 999px;
		font-size: 12px;
		cursor: pointer;
	}

	.back-btn:hover {
		background: rgba(243, 211, 139, 0.14);
	}

	h2 {
		font-family: var(--font-serif);
		font-size: 36px;
		margin: 10px 0 6px;
		color: #fff;
		line-height: 1.05;
	}

	.badge-row {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.pill {
		font-size: 12px;
		padding: 4px 10px;
		border-radius: 999px;
		font-weight: 600;
	}

	.unesco-pill {
		background: rgba(243, 211, 139, 0.2);
		color: var(--gold-bright);
		border: 1px solid rgba(243, 211, 139, 0.45);
	}

	.notable-pill {
		background: rgba(255, 255, 255, 0.08);
		color: var(--text-secondary);
	}

	.teaser {
		font-size: 13px;
		line-height: 1.5;
		color: var(--text-secondary);
		margin: 10px 0 0;
	}

	.panel-section {
		margin-top: 16px;
		padding-top: 14px;
		border-top: 1px solid rgba(255, 255, 255, 0.08);
	}

	.sec-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 10px;
	}

	.clear-btn {
		background: none;
		border: 0;
		color: var(--gold-bright);
		font-size: 12px;
		cursor: pointer;
		text-decoration: underline;
	}

	.cat-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 7px;
	}

	.cat-chip {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 7px 10px;
		border-radius: 10px;
		border: 1px solid rgba(255, 255, 255, 0.09);
		background: rgba(255, 255, 255, 0.04);
		color: var(--text-primary);
		font-size: 12px;
		cursor: pointer;
		text-align: left;
	}

	.cat-chip:disabled {
		opacity: 0.38;
		cursor: default;
	}

	.cat-chip.active {
		border-color: var(--gold-bright);
		background: rgba(243, 211, 139, 0.18);
	}

	.cat-dot {
		width: 20px;
		height: 20px;
		border-radius: 50%;
		display: inline-grid;
		place-items: center;
		color: #091326;
		font-size: 11px;
		font-weight: 700;
		flex-shrink: 0;
	}

	.cat-name {
		flex: 1;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.cat-count {
		font-weight: 600;
		color: var(--gold-bright);
	}

	.prac-grid {
		display: grid;
		gap: 8px;
		margin-top: 8px;
	}

	.prac-item {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 10px;
		font-size: 12px;
	}

	.prac-label {
		color: var(--text-muted);
		font-size: 11px;
		display: block;
	}

	.prac-val {
		color: var(--text-primary);
		text-align: right;
	}

	.prac-val a {
		color: var(--gold-bright);
		text-decoration: none;
	}

	.prac-val a:hover {
		text-decoration: underline;
	}

	.as-of {
		color: var(--text-muted);
		margin-left: 4px;
	}

	.cost-tier {
		color: var(--gold-bright);
		font-weight: 700;
		letter-spacing: 1px;
	}

	.climate-block {
		margin-top: 10px;
	}

	.month-strip {
		display: grid;
		grid-template-columns: repeat(12, 1fr);
		gap: 4px;
		margin-top: 6px;
	}

	.month-cell {
		text-align: center;
		padding: 5px 0;
		font-size: 11px;
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.05);
		color: var(--text-muted);
	}

	.month-cell.comfortable {
		background: rgba(243, 211, 139, 0.26);
		color: var(--gold-bright);
		border: 1px solid rgba(243, 211, 139, 0.5);
		font-weight: 700;
	}

	.traditions-block {
		margin-top: 10px;
	}

	.trad-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 5px;
		margin-top: 6px;
	}

	.trad-tag {
		font-size: 11px;
		padding: 3px 8px;
		border-radius: 999px;
		background: rgba(255, 255, 255, 0.07);
		color: var(--text-secondary);
	}

	.site-list {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.site-row {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 9px 10px;
		border-radius: 10px;
		border: 1px solid rgba(255, 255, 255, 0.06);
		background: rgba(255, 255, 255, 0.03);
		color: var(--text-primary);
		cursor: pointer;
		text-align: left;
	}

	.site-row:hover,
	.site-row.hovered,
	.site-row.selected {
		border-color: var(--gold-bright);
		background: rgba(243, 211, 139, 0.14);
	}

	.site-marker {
		width: 24px;
		height: 24px;
		border-radius: 50%;
		display: grid;
		place-items: center;
		color: #081326;
		font-size: 12px;
		font-weight: 700;
		flex-shrink: 0;
	}

	.site-main {
		display: flex;
		flex-direction: column;
		min-width: 0;
	}

	.site-title {
		font-size: 13px;
		font-weight: 600;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.site-sub {
		font-size: 11px;
		color: var(--text-muted);
		margin-top: 2px;
	}

	.unesco-tag {
		color: var(--gold-bright);
	}

	.muted-note {
		font-size: 13px;
		color: var(--text-muted);
	}

	@media (max-width: 767px) {
		.country-panel {
			left: 10px;
			right: 10px;
			bottom: calc(10px + env(safe-area-inset-bottom, 0px));
			top: auto;
			width: auto;
			padding: 10px 14px 14px;
			max-height: 50dvh;
			-webkit-overflow-scrolling: touch;
		}

		.mobile-drag-handle {
			display: flex;
			justify-content: center;
			width: 100%;
			padding: 2px 0 8px;
			border: 0;
			background: transparent;
			cursor: pointer;
		}

		.mobile-drag-pill {
			display: block;
			width: 36px;
			height: 4px;
			border-radius: 999px;
			background: rgba(243, 211, 139, 0.35);
		}

		.mobile-collapse-btn {
			display: inline-flex;
			align-items: center;
			background: rgba(243, 211, 139, 0.14);
			border: 1px solid var(--gold-soft);
			color: var(--gold-bright);
			padding: 6px 12px;
			border-radius: 999px;
			font-size: 12px;
			font-weight: 600;
			cursor: pointer;
		}

		h2 {
			font-size: 26px;
			margin: 8px 0 6px;
		}

		.country-panel.mobile-collapsed {
			max-height: none;
			overflow: hidden;
			padding-bottom: 12px;
		}

		.country-panel.mobile-collapsed .teaser,
		.country-panel.mobile-collapsed .country-panel-details {
			display: none;
		}

		.cat-chip,
		.site-row {
			min-height: 40px;
		}
	}
</style>
