<script lang="ts">
	import { resolve } from '$app/paths';
	import '@fontsource-variable/bodoni-moda';
	import '@fontsource-variable/figtree';
	import '../app.css';

	import favicon from '#lib/assets/favicon.svg';
	import ApiStatus from '#lib/components/ApiStatus.svelte';

	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta
		name="description"
		content="Experimente roupas sobre a sua foto antes de decidir o que vestir."
	/>
</svelte:head>

<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>

<header class="site-header">
	<a class="wordmark" href={resolve('/')}>VirtualFit</a>
</header>

<main id="conteudo" class="page">
	{@render children()}
</main>

<footer class="site-footer">
	<ApiStatus />
</footer>

<style>
	.site-header,
	.page,
	.site-footer {
		width: 100%;
		max-width: var(--page-max);
		margin-inline: auto;
		padding-inline: var(--page-gutter);
	}

	.site-header {
		padding-block: var(--space-6);
	}

	.wordmark {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: 600;
		color: var(--color-text);
		text-decoration: none;
	}

	.page {
		padding-block: var(--space-8) var(--space-16);
	}

	.site-footer {
		padding-block: var(--space-6);
		border-top: 1px solid var(--color-border-subtle);
	}

	.skip-link {
		position: absolute;
		left: var(--space-4);
		top: calc(-1 * var(--space-16));
		padding: var(--space-2) var(--space-4);
		background: var(--color-surface);
		z-index: 1;
	}

	.skip-link:focus-visible {
		top: var(--space-4);
	}
</style>
