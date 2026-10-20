<script lang="ts">
	import type { Piece } from '#lib/outfit/slots.ts';
	import { categoryLabel, type GarmentCategory } from '#lib/wardrobe/categories.ts';
	import { garmentThumbnailUrl } from '#lib/wardrobe/garments.ts';

	import Icon from './Icon.svelte';

	interface Props {
		category: GarmentCategory;
		piece?: Piece;
		/** Vertical: ocupa a altura de dois quadradinhos (a peça única, no lugar do tronco e das pernas) */
		tall?: boolean;
		onpick: () => void;
		onclear: () => void;
	}

	let { category, piece, tall = false, onpick, onclear }: Props = $props();

	const label = $derived(categoryLabel(category));
	const title = $derived(piece?.name || label);
</script>

<div class="slot" class:tall class:filled={piece}>
	<button
		type="button"
		class="face"
		aria-label={piece ? `Trocar ${label}: ${title}` : `Escolher ${label}`}
		onclick={onpick}
	>
		{#if piece}
			<img src={garmentThumbnailUrl(piece.uid)} alt="" loading="lazy" decoding="async" />
			<!-- A categoria é dada pela posição no mapa (e pelo rótulo do botão): a legenda
			     fica numa linha só, o nome, para a imagem ocupar o quadradinho -->
			<span class="caption">
				<span class="name">{title}</span>
				<!-- Dica de que o quadradinho é um botão: toque para trocar a peça -->
				<span class="swap" aria-hidden="true"><Icon name="swap" size="sm" /></span>
			</span>
		{:else}
			<span class="plus" aria-hidden="true"><Icon name="plus" size="sm" /></span>
			<Icon name={category} size="lg" />
			<span class="category">{label}</span>
			<span class="cta">Toque para escolher</span>
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
		position: relative;
		display: grid;
		place-items: center;
		align-content: center;
		gap: var(--space-1);
		width: 100%;
		aspect-ratio: 1;
		padding: var(--space-2);
		border: 2px dashed var(--color-primary);
		border-radius: var(--radius-field);
		background: var(--color-surface);
		color: var(--color-text);
		font: inherit;
		text-align: center;
		cursor: pointer;
		overflow: hidden;
		transition:
			background var(--duration-quick, 150ms) ease-out,
			transform var(--duration-quick, 150ms) ease-out,
			box-shadow var(--duration-quick, 150ms) ease-out;
	}

	/* Tall: preenche a altura que a grade der (dois quadradinhos, com o espaço entre eles) */
	.tall {
		height: 100%;
	}

	.tall .face {
		aspect-ratio: auto;
		height: 100%;
	}

	/* Resposta ao passar o mouse e ao tocar: o quadradinho sobe e afunda */
	.face:hover {
		background: var(--color-bg);
		box-shadow: 0 0.25rem 0.75rem -0.5rem rgb(60 56 54 / 0.5);
	}

	.face:active {
		transform: scale(0.97);
		box-shadow: none;
	}

	@media (prefers-reduced-motion: reduce) {
		.face {
			transition: none;
		}

		.face:active {
			transform: none;
		}
	}

	.filled .face {
		border-style: solid;
		border-color: var(--color-border-subtle);
		padding: 0;
	}

	.filled .face:hover {
		border-color: var(--color-primary);
	}

	/* O "+" do canto diz que há o que adicionar */
	.plus {
		position: absolute;
		top: var(--space-1, 0.25rem);
		right: var(--space-1, 0.25rem);
		display: grid;
		place-items: center;
		width: 1.5rem;
		height: 1.5rem;
		border-radius: 50%;
		background: var(--color-primary);
		color: var(--color-on-primary);
	}

	.cta {
		font-size: 0.75rem;
		color: var(--color-primary);
		font-weight: 600;
	}

	.face :global(.icon.lg) {
		color: var(--color-primary);
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
		padding: var(--space-2, 0.5rem) var(--space-2, 0.5rem) 2.25rem;
	}

	.caption {
		position: absolute;
		inset: auto 0 0;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-1);
		padding: var(--space-1) var(--space-2);
		background: var(--color-surface);
		text-align: left;
	}

	.swap {
		display: grid;
		place-items: center;
		flex: none;
		width: 1.5rem;
		height: 1.5rem;
		border-radius: 50%;
		background: var(--color-primary);
		color: var(--color-on-primary);
	}

	.name {
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-size: var(--text-sm);
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
