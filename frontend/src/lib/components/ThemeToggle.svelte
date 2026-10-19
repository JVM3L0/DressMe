<script lang="ts">
	import { onMount } from 'svelte';

	import { currentTheme, toggleTheme, type Theme } from '#lib/theme.ts';

	// Só é conhecido no navegador (a página é pré-renderizada no build); até lá
	// o botão fica oculto, para não mostrar o ícone errado
	let theme: Theme | undefined = $state();

	onMount(() => {
		theme = currentTheme();
	});

	const label = $derived(theme === 'dark' ? 'Usar tema claro' : 'Usar tema escuro');
</script>

<button
	type="button"
	class="toggle"
	aria-label={label}
	title={label}
	hidden={!theme}
	onclick={() => (theme = toggleTheme())}
>
	{#if theme === 'dark'}
		<!-- Sol: a ação é voltar ao tema claro -->
		<svg viewBox="0 0 24 24" aria-hidden="true">
			<circle cx="12" cy="12" r="4.5" />
			<path
				d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"
			/>
		</svg>
	{:else}
		<!-- Lua: a ação é ir para o tema escuro -->
		<svg viewBox="0 0 24 24" aria-hidden="true">
			<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" />
		</svg>
	{/if}
</button>

<style>
	.toggle {
		display: inline-grid;
		place-items: center;
		width: 2.75rem; /* alvo de toque de 44px */
		height: 2.75rem;
		padding: 0;
		border: 1px solid var(--color-border-subtle);
		border-radius: 50%;
		background: transparent;
		color: var(--color-text);
		cursor: pointer;
		transition: border-color var(--duration-quick) ease-out;
	}

	.toggle:hover {
		border-color: var(--color-border);
	}

	.toggle[hidden] {
		display: none;
	}

	svg {
		width: 1.25rem;
		height: 1.25rem;
		fill: none;
		stroke: currentColor;
		stroke-width: 1.75;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
</style>
