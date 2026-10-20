<script lang="ts">
	import { MAX_ACCESSORIES, type Piece } from '#lib/outfit/slots.ts';
	import { garmentThumbnailUrl } from '#lib/wardrobe/garments.ts';

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
					<span aria-hidden="true">+</span>
				</button>
			</li>
		{/if}
	</ul>
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
		width: 100%;
		aspect-ratio: 1;
		min-height: 2.75rem; /* alvo de toque de 44px */
		padding: 0;
		border: 2px dashed var(--color-border);
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--color-text-muted);
		font: inherit;
		font-size: var(--text-lg);
		line-height: 1;
		cursor: pointer;
		overflow: hidden;
	}

	.mini:hover {
		border-color: var(--color-primary);
		color: var(--color-text);
	}

	.mini.filled {
		border: 1px solid var(--color-border-subtle);
		background: var(--color-surface);
	}

	img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		padding: 2px;
	}
</style>
