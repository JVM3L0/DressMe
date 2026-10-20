<script lang="ts">
	interface Props {
		src: string;
		width: number;
		height: number;
		alt: string;
		title: string;
		detail?: string;
		/** O que a exclusão apaga, para o rótulo do botão ("a foto", "a peça") */
		subject: string;
		busy?: boolean;
		ondelete: () => void;
	}

	let { src, width, height, alt, title, detail, subject, busy = false, ondelete }: Props = $props();

	// Excluir é definitivo: pede uma segunda confirmação, na própria carta
	let confirming = $state(false);
</script>

<div class="card" aria-busy={busy}>
	<figure>
		<div class="frame">
			<img {src} {width} {height} {alt} loading="lazy" decoding="async" />
		</div>
		<figcaption>
			<span class="title">{title}</span>
			{#if detail}<span class="detail">{detail}</span>{/if}
		</figcaption>
	</figure>

	<div class="actions">
		{#if confirming}
			<button
				type="button"
				class="danger"
				disabled={busy}
				onclick={() => {
					confirming = false;
					ondelete();
				}}
			>
				Excluir mesmo
			</button>
			<button type="button" class="plain" onclick={() => (confirming = false)}>Cancelar</button>
		{:else}
			<button type="button" class="plain" disabled={busy} onclick={() => (confirming = true)}>
				Excluir <span class="visually-hidden">{subject}</span>
			</button>
		{/if}
	</div>
</div>

<style>
	.card {
		display: grid;
		gap: var(--space-2);
	}

	figure {
		display: grid;
		gap: var(--space-2);
		margin: 0;
	}

	/* Todas as imagens no mesmo quadro, para a grade ficar alinhada, sem cortar
	   a peça ou a pessoa */
	.frame {
		aspect-ratio: 4 / 5;
		border: 1px solid var(--color-border-subtle);
		border-radius: var(--radius-field);
		background: var(--color-surface);
		overflow: hidden;
	}

	img {
		display: block;
		width: 100%;
		height: 100%;
		object-fit: contain;
	}

	/* Espaço para o título e o detalhe, tenha a carta os dois ou não: os
	   botões de todas as cartas ficam alinhados */
	figcaption {
		display: grid;
		align-content: start;
		min-height: 3rem;
	}

	.title {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 600;
	}

	.detail {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.actions {
		display: flex;
		gap: var(--space-2);
	}

	button {
		min-height: 2.75rem; /* alvo de toque de 44px */
		padding: var(--space-1) var(--space-3);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--color-text);
		font: inherit;
		font-size: var(--text-sm);
		font-weight: 600;
		cursor: pointer;
	}

	button:disabled {
		cursor: progress;
		opacity: 0.6;
	}

	.danger {
		border-color: var(--color-danger);
		background: var(--color-danger);
		color: var(--color-bg);
	}

	[aria-busy='true'] img {
		opacity: 0.5;
	}
</style>
