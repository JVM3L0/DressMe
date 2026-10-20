<script lang="ts">
	import type { Piece } from '#lib/outfit/slots.ts';
	import { categoryLabel, type GarmentCategory } from '#lib/wardrobe/categories.ts';
	import { garmentThumbnailUrl } from '#lib/wardrobe/garments.ts';

	interface Props {
		category: GarmentCategory;
		piece?: Piece;
		/** Ocupa a largura toda (a peça única, que fica no lugar de cima e de baixo) */
		wide?: boolean;
		onpick: () => void;
		onclear: () => void;
	}

	let { category, piece, wide = false, onpick, onclear }: Props = $props();

	const label = $derived(categoryLabel(category));
	const title = $derived(piece?.name || label);
</script>

<div class="slot" class:wide class:filled={piece}>
	<button
		type="button"
		class="face"
		aria-label={piece ? `Trocar ${label}: ${title}` : `Escolher ${label}`}
		onclick={onpick}
	>
		{#if piece}
			<img src={garmentThumbnailUrl(piece.uid)} alt="" loading="lazy" decoding="async" />
			<span class="caption">
				<span class="category">{label}</span>
				<span class="name">{title}</span>
			</span>
		{:else}
			<span class="plus" aria-hidden="true">+</span>
			<span class="category">{label}</span>
		{/if}
	</button>
	{#if piece}
		<button type="button" class="clear" aria-label={`Tirar ${title} do conjunto`} onclick={onclear}>
			<span aria-hidden="true">✕</span>
		</button>
	{/if}
</div>

<style>
	.slot {
		position: relative;
		min-width: 0;
	}

	.face {
		display: grid;
		place-items: center;
		align-content: center;
		gap: var(--space-1);
		width: 100%;
		aspect-ratio: 1;
		padding: var(--space-2);
		border: 2px dashed var(--color-border);
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--color-text-muted);
		font: inherit;
		text-align: center;
		cursor: pointer;
		overflow: hidden;
	}

	.wide .face {
		aspect-ratio: 2 / 1;
	}

	.face:hover {
		border-color: var(--color-primary);
		color: var(--color-text);
	}

	.filled .face {
		position: relative;
		border-style: solid;
		border-color: var(--color-border-subtle);
		background: var(--color-surface);
		color: var(--color-text);
		padding: 0;
	}

	.plus {
		font-size: var(--text-2xl);
		line-height: 1;
	}

	.category {
		font-size: var(--text-sm);
	}

	img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: contain;
		padding: var(--space-2) var(--space-2) 2.6rem;
	}

	.caption {
		position: absolute;
		inset: auto 0 0;
		display: grid;
		padding: var(--space-1) var(--space-2);
		background: var(--color-surface);
		text-align: left;
	}

	.caption .category {
		color: var(--color-text-muted);
	}

	.name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 600;
	}

	/* O alvo de toque tem 44px, mesmo com o ícone pequeno */
	.clear {
		position: absolute;
		top: var(--space-1, 0.25rem);
		right: var(--space-1, 0.25rem);
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		border: 0;
		border-radius: 50%;
		background: transparent;
		color: var(--color-text);
		font: inherit;
		cursor: pointer;
	}

	.clear span {
		display: grid;
		place-items: center;
		width: 1.75rem;
		height: 1.75rem;
		border-radius: 50%;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		font-size: var(--text-sm);
	}
</style>
