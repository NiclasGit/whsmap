<script lang="ts">
	import type { SiteFeature } from '$lib/data/types';
	import { CATEGORY_META, FAME_LABELS } from '$lib/data/categories';

	interface Props {
		site: SiteFeature;
		onClose: () => void;
	}

	let { site, onClose }: Props = $props();
	let p = $derived(site.properties);
	let meta = $derived(CATEGORY_META[p.category]);
	let imageFailed = $state(false);

	$effect(() => {
		site;
		imageFailed = false;
	});
</script>

<article class="site-card glass-panel" aria-label="{p.name} details">
	<button type="button" class="close-btn" aria-label="Close site card" onclick={onClose}>
		✕
	</button>

	<div class="media-wrap" style="--cat-color: {meta.color}">
		{#if p.image && !imageFailed}
			<img
				src={p.image.thumbUrl}
				alt={p.name}
				loading="lazy"
				onerror={() => (imageFailed = true)}
			/>
		{:else}
			<div class="fallback-art">
				<div class="art-icon">{@html meta.iconSvg}</div>
				<span>{meta.label}</span>
			</div>
		{/if}
	</div>

	<div class="card-body">
		<div class="badges">
			<span class="cat-badge" style="background:{meta.color}">
				{meta.glyph}
				{meta.label}
			</span>
			{#if p.unesco}
				<span class="unesco-badge">
					★ UNESCO World Heritage{p.yearInscribed ? ` · ${p.yearInscribed}` : ''}
				</span>
			{/if}
			{#if p.inDanger}
				<span class="danger-badge">In Danger</span>
			{/if}
			<span class="fame-badge">{FAME_LABELS[p.fameLevel]}</span>
		</div>

		<h3>{p.name}</h3>

		{#if p.summary}
			<p class="summary">{p.summary}</p>
		{:else}
			<p class="summary">
				A notable {meta.label.toLowerCase()} landmark recognized across {p.fame} Wikipedia language
				editions.
			</p>
		{/if}

		<div class="links">
			{#if p.wikipediaUrl}
				<a href={p.wikipediaUrl} target="_blank" rel="noopener noreferrer" class="ext-link">
					Read on Wikipedia ↗
				</a>
			{/if}
			{#if p.unescoUrl}
				<a href={p.unescoUrl} target="_blank" rel="noopener noreferrer" class="ext-link">
					UNESCO dossier ↗
				</a>
			{/if}
		</div>

		<footer class="attribution">
			{#if p.summarySource === 'unesco'}
				<span>Text: UNESCO World Heritage Centre</span>
			{:else if p.summarySource === 'wikipedia'}
				<span>Text: Wikipedia (CC BY-SA 4.0)</span>
			{/if}
			{#if p.image}
				<span>
					· Photo: <a href={p.image.sourceUrl} target="_blank" rel="noopener noreferrer"
						>{p.image.author}</a
					>
					({p.image.license})
				</span>
			{/if}
		</footer>
	</div>
</article>

<style>
	.site-card {
		position: absolute;
		left: 24px;
		bottom: 24px;
		width: 370px;
		z-index: 15;
		overflow: hidden;
		background: var(--glass-bg-strong);
	}

	.close-btn {
		position: absolute;
		top: 10px;
		right: 10px;
		width: 30px;
		height: 30px;
		border-radius: 50%;
		border: 1px solid rgba(255, 255, 255, 0.25);
		background: rgba(6, 12, 26, 0.75);
		color: #fff;
		cursor: pointer;
		z-index: 2;
	}

	.media-wrap {
		height: 175px;
		background: radial-gradient(circle at 50% 40%, rgba(243, 211, 139, 0.22), #071126);
		position: relative;
		overflow: hidden;
	}

	.media-wrap img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.fallback-art {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 8px;
		color: var(--cat-color);
		font-size: 12px;
		letter-spacing: 1px;
		text-transform: uppercase;
	}

	.art-icon {
		width: 48px;
		height: 48px;
	}

	.card-body {
		padding: 16px 18px 18px;
	}

	.badges {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 8px;
	}

	.cat-badge,
	.unesco-badge,
	.danger-badge,
	.fame-badge {
		font-size: 11px;
		padding: 3px 8px;
		border-radius: 999px;
		font-weight: 600;
	}

	.cat-badge {
		color: #081326;
	}

	.unesco-badge {
		background: rgba(243, 211, 139, 0.2);
		color: var(--gold-bright);
		border: 1px solid rgba(243, 211, 139, 0.5);
	}

	.danger-badge {
		background: rgba(232, 107, 90, 0.22);
		color: var(--danger);
		border: 1px solid var(--danger);
	}

	.fame-badge {
		background: rgba(255, 255, 255, 0.08);
		color: var(--text-secondary);
	}

	h3 {
		font-family: var(--font-serif);
		font-size: 26px;
		margin: 4px 0 8px;
		color: #fff;
		line-height: 1.15;
	}

	.summary {
		font-size: 13px;
		line-height: 1.55;
		color: var(--text-secondary);
		margin: 0 0 12px;
	}

	.links {
		display: flex;
		gap: 12px;
		margin-bottom: 10px;
	}

	.ext-link {
		font-size: 12px;
		font-weight: 600;
		color: var(--gold-bright);
		text-decoration: none;
	}

	.ext-link:hover {
		text-decoration: underline;
	}

	.attribution {
		font-size: 10px;
		color: var(--text-muted);
		border-top: 1px solid rgba(255, 255, 255, 0.08);
		padding-top: 8px;
	}

	.attribution a {
		color: var(--text-secondary);
	}

	@media (max-width: 767px) {
		.site-card {
			left: 10px;
			right: 10px;
			top: 12px;
			bottom: auto;
			width: auto;
		}
	}
</style>
