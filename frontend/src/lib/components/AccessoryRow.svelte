<script lang="ts">
	import { MAX_ACCESSORIES, type Piece } from '#lib/outfit/slots.ts';
	import { garmentThumbnailUrl } from '#lib/wardrobe/garments.ts';

	import Icon from './Icon.svelte';

	interface Props {
		pieces: readonly Piece[];
		onadd: () => void;
		/** Abre a escolha para trocar (ou tirar) um acessório */
		onedit: (piece: Piece) => void;
	}

	let { pieces, onadd, onedit }: Props = $props();

	const full = $derived(pieces.length >= MAX_ACCESSORIES);
</script>

<!-- Até 4 acessórios (boné, óculos, relógio, bolsa…), em quadradinhos pequenos:
     o nome fica no rótulo e na dica, e a lista completa aparece ao tocar -->
<div class="accessories" role="group" aria-label="Acessórios">
	<p class="caption">
		Acessórios <span class="count">{pieces.length} de {MAX_ACCESSORIES}</span>
	</p>
	<ul class="row">
		{#each pieces as piece (piece.uid)}
			{@const name = piece.name || 'Acessório'}
			<li>
				<button
					type="button"
					class="mini filled"
					aria-label={`Trocar acessório: ${name}`}
					title={name}
					onclick={() => onedit(piece)}
				>
					<img src={garmentThumbnailUrl(piece.uid)} alt="" loading="lazy" decoding="async" />
				</button>
			</li>
		{/each}
		{#if !full}
			<li>
				<button type="button" class="mini add" aria-label="Adicionar acessório" onclick={onadd}>
					<Icon name="plus" size="sm" />
					<span class="add-label" aria-hidden="true">Adicionar</span>
				</button>
			</li>
		{/if}
	</ul>
	{#if pieces.length > 0}
		<p class="hint">Toque num acessório para trocar ou tirar.</p>
	{/if}
</div>

<style>
	.accessories {
		display: grid;
		gap: var(--space-1);
	}

	.caption {
		margin: 0;
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		text-align: center;
	}

	.count {
		margin-left: var(--space-1);
		font-weight: 600;
	}

	.hint {
		margin: 0;
		font-size: 0.75rem;
		color: var(--color-text-muted);
		text-align: center;
	}

	.row {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: var(--space-2, 0.5rem);
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.mini {
		display: grid;
		place-items: center;
		align-content: center;
		width: 100%;
		aspect-ratio: 1;
		min-height: 2.75rem; /* alvo de toque de 44px */
		padding: 0;
		border: 2px dashed var(--color-primary);
		border-radius: var(--radius-field);
		background: var(--color-surface);
		color: var(--color-primary);
		font: inherit;
		cursor: pointer;
		overflow: hidden;
		transition: transform var(--duration-quick, 150ms) ease-out;
	}

	.mini:hover {
		background: var(--color-bg);
	}

	.mini:active {
		transform: scale(0.95);
	}

	.add-label {
		font-size: 0.625rem;
		font-weight: 600;
		line-height: 1;
	}

	.mini.filled {
		border: 1px solid var(--color-border-subtle);
	}

	.mini.filled:hover {
		border-color: var(--color-primary);
	}

	@media (prefers-reduced-motion: reduce) {
		.mini {
			transition: none;
		}

		.mini:active {
			transform: none;
		}
	}

	img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		padding: 2px;
	}
</style>
