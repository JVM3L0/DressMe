<script lang="ts">
	import type { Outfit } from '#lib/outfit/outfits.ts';
	import { garmentThumbnailUrl, type Garment } from '#lib/wardrobe/garments.ts';

	interface Props {
		outfits: readonly Outfit[];
		/** Para mostrar as miniaturas: peças que já não existem simplesmente não aparecem */
		garments: readonly Garment[];
		/** Conjunto em edição (o último usado ou salvo) */
		activeUid?: string;
		deletingUid?: string;
		onuse: (outfit: Outfit) => void;
		ondelete: (outfit: Outfit) => void;
	}

	let { outfits, garments, activeUid, deletingUid, onuse, ondelete }: Props = $props();

	const byUid = $derived(new Map(garments.map((garment) => [garment.uid, garment])));

	/** Excluir é definitivo: pede uma segunda confirmação, no próprio item */
	let confirmingUid: string | undefined = $state();

	const piecesOf = (outfit: Outfit) =>
		outfit.garment_ids.flatMap((uid) => byUid.get(uid) ?? []).slice(0, 8);
</script>

<section class="saved" aria-labelledby="conjuntos-salvos">
	<h2 id="conjuntos-salvos">Conjuntos salvos</h2>

	{#if outfits.length === 0}
		<p class="muted">Nenhum conjunto salvo ainda. Monte um acima e dê um nome a ele.</p>
	{:else}
		<ul class="list">
			{#each outfits as outfit (outfit.uid)}
				{@const pieces = piecesOf(outfit)}
				<li class="item" class:active={outfit.uid === activeUid}>
					<div class="thumbs" aria-hidden="true">
						{#each pieces as piece (piece.uid)}
							<img src={garmentThumbnailUrl(piece.uid)} alt="" loading="lazy" decoding="async" />
						{/each}
					</div>
					<div class="info">
						<span class="name">{outfit.name}</span>
						<span class="meta">
							{#if pieces.length === 0}
								Conjunto vazio
							{:else}
								{pieces.length} {pieces.length === 1 ? 'peça' : 'peças'}
							{/if}
						</span>
					</div>
					<div class="button-group">
						<button
							type="button"
							class="button"
							aria-label={`Usar o conjunto ${outfit.name}`}
							onclick={() => onuse(outfit)}
						>
							Usar
						</button>
						{#if confirmingUid === outfit.uid}
							<button
								type="button"
								class="button danger"
								disabled={deletingUid === outfit.uid}
								onclick={() => {
									confirmingUid = undefined;
									ondelete(outfit);
								}}
							>
								Excluir mesmo
							</button>
							<button
								type="button"
								class="button secondary"
								onclick={() => (confirmingUid = undefined)}
							>
								Cancelar
							</button>
						{:else}
							<button
								type="button"
								class="button secondary"
								aria-label={`Excluir o conjunto ${outfit.name}`}
								disabled={deletingUid === outfit.uid}
								onclick={() => (confirmingUid = outfit.uid)}
							>
								Excluir
							</button>
						{/if}
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</section>

<style>
	.saved {
		display: grid;
		gap: var(--space-4);
	}

	h2 {
		font-size: var(--text-xl);
	}

	.muted {
		margin: 0;
		color: var(--color-text-muted);
	}

	.list {
		display: grid;
		gap: var(--space-3);
		margin: 0;
		padding: 0;
		list-style: none;
	}

	/* Celular: miniaturas, nome e botões empilhados (8 miniaturas não cabem ao lado do nome) */
	.item {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: var(--space-2) var(--space-4);
		align-items: center;
		padding: var(--space-3);
		border: 1px solid var(--color-border-subtle);
		border-radius: var(--radius-field);
		background: var(--color-surface);
	}

	.item.active {
		border-color: var(--color-primary);
		border-width: 2px;
	}

	.thumbs {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-1);
	}

	img {
		width: 2.75rem;
		height: 2.75rem;
		object-fit: contain;
		border-radius: var(--radius-field);
		background: var(--color-bg);
	}

	.info {
		display: grid;
		min-width: 0;
	}

	.name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 600;
	}

	.meta {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	@media (min-width: 48rem) {
		.item {
			grid-template-columns: auto minmax(0, 1fr);
		}

		.button-group {
			grid-column: 1 / -1;
		}
	}
</style>
