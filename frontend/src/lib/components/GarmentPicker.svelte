<script lang="ts">
	import { resolve } from '$app/paths';

	import type { Piece } from '#lib/outfit/slots.ts';
	import { categoryLabel, type GarmentCategory } from '#lib/wardrobe/categories.ts';
	import { garmentThumbnailUrl, type Garment } from '#lib/wardrobe/garments.ts';

	interface Props {
		/** Categoria sendo escolhida; `undefined` fecha a janela */
		category?: GarmentCategory;
		garments: readonly Garment[];
		/** Peça já escolhida nesta categoria */
		current?: Piece;
		/** Peças que sairiam do conjunto se uma dessa categoria entrar */
		replaced?: readonly Piece[];
		/** Ids que não podem ser escolhidos de novo (acessórios que já estão no conjunto) */
		exclude?: readonly string[];
		/** Quando há uma peça sendo trocada, oferece tirá-la do conjunto */
		onremove?: () => void;
		onselect: (garment: Garment) => void;
		onclose: () => void;
	}

	let {
		category,
		garments,
		current,
		replaced = [],
		exclude = [],
		onremove,
		onselect,
		onclose
	}: Props = $props();

	let dialog: HTMLDialogElement | undefined = $state();

	const options = $derived(
		garments.filter((garment) => garment.category === category && !exclude.includes(garment.uid))
	);
	const allUsed = $derived(
		options.length === 0 &&
			garments.some((garment) => garment.category === category && exclude.includes(garment.uid))
	);
	const label = $derived(category ? categoryLabel(category) : '');
	const titleId = $props.id();

	// A janela nativa já prende o foco, fecha com Esc e restaura o foco ao fechar
	$effect(() => {
		if (!dialog) return;
		if (category && !dialog.open) dialog.showModal();
		if (!category && dialog.open) dialog.close();
	});

	/** Clique fora do conteúdo (no fundo escurecido) fecha a janela */
	function handleBackdropClick(event: MouseEvent) {
		if (event.target === dialog) dialog?.close();
	}
</script>

<dialog bind:this={dialog} aria-labelledby={titleId} {onclose} onclick={handleBackdropClick}>
	<div class="content">
		<h2 id={titleId}>Escolher: {label}</h2>

		{#if replaced.length}
			{@const names = replaced.map((p) => p.name || categoryLabel(p.category)).join(' e ')}
			<p class="warning">Isso tira {names} do conjunto.</p>
		{/if}

		{#if allUsed}
			<p class="muted">Todas as suas peças dessa categoria já estão no conjunto.</p>
		{:else if options.length === 0}
			<p class="muted">Você ainda não tem peças nessa categoria.</p>
			<a class="button" href={resolve('/guarda-roupa')}>Adicionar peça</a>
		{:else}
			<ul class="options">
				{#each options as garment (garment.uid)}
					<li>
						<button
							type="button"
							class="option"
							aria-pressed={current?.uid === garment.uid}
							onclick={() => onselect(garment)}
						>
							<img src={garmentThumbnailUrl(garment.uid)} alt="" loading="lazy" decoding="async" />
							<span class="name">{garment.name || label}</span>
						</button>
					</li>
				{/each}
			</ul>
		{/if}

		<form method="dialog" class="footer">
			{#if onremove}
				<button
					class="close remove"
					type="submit"
					onclick={() => {
						onremove?.();
					}}
				>
					Tirar do conjunto
				</button>
			{/if}
			<button class="close" type="submit">Cancelar</button>
		</form>
	</div>
</dialog>

<style>
	dialog {
		width: min(100% - 2 * var(--page-gutter), 34rem);
		max-height: 85dvh;
		padding: 0;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-tag);
		background: var(--color-bg);
		color: var(--color-text);
	}

	dialog::backdrop {
		background: rgb(29 32 33 / 0.6);
	}

	.content {
		display: grid;
		gap: var(--space-4);
		padding: var(--space-6);
	}

	h2 {
		font-size: var(--text-xl);
	}

	.warning {
		margin: 0;
		padding: var(--space-2) var(--space-3);
		border-left: 4px solid var(--color-focus);
		background: var(--color-surface);
	}

	.muted {
		margin: 0;
		color: var(--color-text-muted);
	}

	.options {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(7rem, 1fr));
		gap: var(--space-3);
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.option {
		display: grid;
		gap: var(--space-1);
		width: 100%;
		padding: var(--space-1);
		border: 2px solid var(--color-border-subtle);
		border-radius: var(--radius-field);
		background: var(--color-surface);
		color: inherit;
		font: inherit;
		text-align: left;
		cursor: pointer;
	}

	.option:hover {
		border-color: var(--color-primary);
	}

	.option[aria-pressed='true'] {
		border-color: var(--color-primary);
		background: var(--color-primary);
		color: var(--color-on-primary);
	}

	img {
		width: 100%;
		aspect-ratio: 1;
		object-fit: contain;
		background: var(--color-surface);
		border-radius: var(--radius-field);
	}

	.name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-size: var(--text-sm);
		font-weight: 600;
	}

	.footer {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	.remove {
		border-color: var(--color-danger);
		color: var(--color-danger);
	}

	.close {
		min-height: 2.75rem;
		padding: var(--space-2) var(--space-6);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--color-text);
		font: inherit;
		font-weight: 600;
		cursor: pointer;
	}
</style>
