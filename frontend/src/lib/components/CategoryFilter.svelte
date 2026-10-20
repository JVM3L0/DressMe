<script lang="ts">
	import { CATEGORIES, type GarmentCategory } from '#lib/wardrobe/categories.ts';

	interface Props {
		/** `undefined` mostra tudo */
		selected?: GarmentCategory;
		counts: Record<GarmentCategory, number>;
		total: number;
	}

	let { selected = $bindable(), counts, total }: Props = $props();
</script>

<div class="filter" role="group" aria-label="Filtrar por categoria">
	<button
		type="button"
		aria-pressed={selected === undefined}
		onclick={() => (selected = undefined)}
	>
		Tudo <span class="count">{total}</span>
	</button>
	{#each CATEGORIES as category (category.value)}
		<button
			type="button"
			aria-pressed={selected === category.value}
			onclick={() => (selected = category.value)}
		>
			{category.label} <span class="count">{counts[category.value]}</span>
		</button>
	{/each}
</div>

<style>
	/* No celular, uma fileira que rola para o lado, em vez de ocupar a tela */
	.filter {
		display: flex;
		gap: var(--space-2);
		margin-inline: calc(-1 * var(--page-gutter));
		padding: var(--space-1) var(--page-gutter);
		overflow-x: auto;
		scrollbar-width: thin;
	}

	button {
		flex: none;
		min-height: 2.75rem; /* alvo de toque de 44px */
		padding: var(--space-1) var(--space-4);
		border: 1px solid var(--color-border);
		border-radius: 999px;
		background: transparent;
		color: var(--color-text);
		font: inherit;
		cursor: pointer;
	}

	button[aria-pressed='true'] {
		border-color: var(--color-primary);
		background: var(--color-primary);
		color: var(--color-on-primary);
		font-weight: 600;
	}

	.count {
		margin-left: var(--space-1);
		font-size: var(--text-sm);
		opacity: 0.85;
	}

	@media (min-width: 48rem) {
		.filter {
			flex-wrap: wrap;
			margin-inline: 0;
			padding-inline: 0;
			overflow: visible;
		}
	}
</style>
