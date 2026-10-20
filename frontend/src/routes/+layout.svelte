<script lang="ts">
	import { resolve } from '$app/paths';
	import { onMount } from 'svelte';
	import '@fontsource-variable/bodoni-moda';
	import '@fontsource-variable/figtree';
	import '../app.css';

	import favicon from '#lib/assets/favicon.svg';
	import ApiStatus from '#lib/components/ApiStatus.svelte';
	import SiteNav from '#lib/components/SiteNav.svelte';
	import ThemeToggle from '#lib/components/ThemeToggle.svelte';
	import { loadSession, session } from '#lib/session.svelte.ts';

	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	// Uma vez por visita: as páginas são estáticas e a sessão só existe no navegador
	onMount(() => {
		loadSession();
	});
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
	<SiteNav />
	<div class="toggle-slot"><ThemeToggle /></div>
</header>

<main id="conteudo" class="page">
	{@render children()}
</main>

<footer class="site-footer" class:tabbar-space={session.current.status !== 'anonymous'}>
	<ApiStatus />
	<a class="repository" href="https://github.com/JVM3L0/DressMe">
		<!-- Marca do GitHub (Octicons, licença MIT) -->
		<svg viewBox="0 0 16 16" aria-hidden="true">
			<path
				d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"
			/>
		</svg>
		Código no GitHub
	</a>
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
		display: flex;
		align-items: center;
		gap: var(--space-4);
		padding-block: var(--space-2);
	}

	.wordmark {
		margin-right: auto;
	}

	.toggle-slot {
		order: 2;
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
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-2) var(--space-6);
		padding-block: var(--space-6);
		border-top: 1px solid var(--color-border-subtle);
	}

	.repository {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		min-height: 2.75rem;
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.repository:hover {
		color: var(--color-text);
	}

	.repository svg {
		width: 1rem;
		height: 1rem;
		fill: currentColor;
	}

	/* A barra de navegação fixa do celular não pode cobrir o rodapé. O espaço é
	   reservado até a sessão ser conhecida (sem salto para quem está logado) e
	   some para quem não tem sessão, que não vê a barra. */
	@media (max-width: 47.99rem) {
		.site-footer.tabbar-space {
			padding-bottom: calc(
				var(--space-6) + var(--tabbar-height, 3.5rem) + env(safe-area-inset-bottom, 0px)
			);
		}
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
