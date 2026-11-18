<script lang="ts">
	import { page } from '$app/state';
</script>

<svelte:head>
	<title
		>{page.params.siteId} · {page.params.iso3?.toUpperCase()} — Heritage Atlas</title
	>
</svelte:head>
