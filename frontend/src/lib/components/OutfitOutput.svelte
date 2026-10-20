<script lang="ts">
	import {
		canCopyImages,
		canShareFiles,
		copyImage,
		copyText,
		downloadBlob,
		shareFiles
	} from '#lib/outfit/clipboard.ts';
	import { clothesAsPng, photoAsPng } from '#lib/outfit/images.ts';
	import { NOTE_MAX, buildPrompt } from '#lib/outfit/prompt.ts';
	import type { Piece } from '#lib/outfit/slots.ts';

	import TextField from './TextField.svelte';

	interface Props {
		/** Peças do conjunto, na ordem do corpo (a mesma da imagem e do texto) */
		pieces: readonly Piece[];
		photoUid?: string;
	}

	let { pieces, photoUid }: Props = $props();

	let keepBackground = $state(true);
	let note = $state('');
	let message = $state('');
	let failed = $state(false);
	let busy: string | undefined = $state();

	const prompt = $derived(buildPrompt(pieces, { keepBackground, note }));
	const hasPieces = $derived(pieces.length > 0);
	const copyImages = canCopyImages();
	// Testa com um arquivo de mentira: o navegador só diz se sabe compartilhar PNGs
	const shareable = canShareFiles([new File([], 'x.png', { type: 'image/png' })]);

	function failureText(error: unknown): string {
		if (error instanceof DOMException && error.name === 'NotAllowedError') {
			return 'O navegador bloqueou a cópia. Use o botão Baixar.';
		}
		if (error instanceof DOMException && error.name === 'AbortError') return '';
		return error instanceof Error ? error.message : 'Não foi possível concluir. Tente de novo.';
	}

	/**
	 * Roda uma ação e mostra o resultado. A ação começa dentro do clique (sem
	 * `await` antes), o que o Safari exige para liberar a área de transferência.
	 */
	async function run(key: string, success: string, action: () => Promise<void>) {
		busy = key;
		message = '';
		failed = false;
		try {
			await action();
			message = success;
		} catch (error) {
			message = failureText(error);
			failed = message !== '';
		} finally {
			busy = undefined;
		}
	}

	const copyPhoto = () =>
		run('photo', 'Foto copiada. Cole na IA.', () => copyImage(photoAsPng(photoUid!)));

	const downloadPhoto = () =>
		run('photo-download', 'Foto baixada.', async () =>
			downloadBlob(await photoAsPng(photoUid!), 'minha-foto.png')
		);

	const copyClothes = () =>
		run('clothes', 'Roupas copiadas. Cole na IA.', () => copyImage(clothesAsPng(pieces)));

	const downloadClothes = () =>
		run('clothes-download', 'Imagem das roupas baixada.', async () =>
			downloadBlob(await clothesAsPng(pieces), 'roupas.png')
		);

	const copyPrompt = () => run('prompt', 'Texto copiado. Cole na IA.', () => copyText(prompt));

	const share = () =>
		run('share', '', async () => {
			const [photo, clothes] = await Promise.all([photoAsPng(photoUid!), clothesAsPng(pieces)]);
			await shareFiles(
				[
					new File([photo], 'minha-foto.png', { type: 'image/png' }),
					new File([clothes], 'roupas.png', { type: 'image/png' })
				],
				prompt
			);
		});
</script>

<section class="output" aria-labelledby="levar-para-ia">
	<h2 id="levar-para-ia">Levar para uma IA</h2>
	<p class="lead">
		O VirtualFit não envia nada para nenhuma IA. Copie os três itens abaixo e cole, nesta ordem, na
		ferramenta que preferir. Ao colar a sua foto lá, ela passa a seguir as regras de privacidade
		dessa ferramenta.
	</p>

	<ol class="steps">
		<li class="step">
			<h3>1. Sua foto</h3>
			<div class="actions">
				{#if copyImages}
					<button type="button" disabled={!photoUid || busy !== undefined} onclick={copyPhoto}>
						{busy === 'photo' ? 'Copiando…' : 'Copiar foto'}
					</button>
				{/if}
				<button type="button" disabled={!photoUid || busy !== undefined} onclick={downloadPhoto}>
					Baixar foto
				</button>
			</div>
			{#if !photoUid}<p class="hint">Escolha uma foto acima.</p>{/if}
		</li>

		<li class="step">
			<h3>2. As roupas</h3>
			<div class="actions">
				{#if copyImages}
					<button type="button" disabled={!hasPieces || busy !== undefined} onclick={copyClothes}>
						{busy === 'clothes' ? 'Copiando…' : 'Copiar roupas'}
					</button>
				{/if}
				<button type="button" disabled={!hasPieces || busy !== undefined} onclick={downloadClothes}>
					Baixar roupas
				</button>
			</div>
			{#if !hasPieces}<p class="hint">Escolha ao menos uma peça.</p>{/if}
		</li>

		<li class="step">
			<h3>3. O texto</h3>
			<label class="check">
				<input type="checkbox" bind:checked={keepBackground} />
				Manter o fundo da foto
			</label>
			<TextField
				label="Pedido extra (opcional)"
				name="note"
				maxlength={NOTE_MAX}
				autocomplete="off"
				hint="Em inglês funciona melhor, como “in a café” ou “slim fit”."
				bind:value={note}
			/>
			<label class="prompt-label" for="prompt-text">Texto para colar na IA</label>
			<textarea id="prompt-text" readonly rows="11" value={hasPieces ? prompt : ''}></textarea>
			<div class="actions">
				<button type="button" disabled={!hasPieces || busy !== undefined} onclick={copyPrompt}>
					{busy === 'prompt' ? 'Copiando…' : 'Copiar texto'}
				</button>
			</div>
		</li>
	</ol>

	{#if shareable}
		<button
			type="button"
			class="share"
			disabled={!photoUid || !hasPieces || busy !== undefined}
			onclick={share}
		>
			Compartilhar tudo
		</button>
	{/if}

	{#if !copyImages}
		<p class="hint">
			Este endereço não é seguro (HTTPS), então o navegador não deixa copiar imagens. Use Baixar, ou
			abra o VirtualFit por HTTPS.
		</p>
	{/if}

	<p class="status" class:failed role={failed ? 'alert' : 'status'}>{message}</p>
</section>

<style>
	.output {
		display: grid;
		gap: var(--space-4);
	}

	h2 {
		font-size: var(--text-xl);
	}

	h3 {
		font-family: var(--font-body);
		font-size: var(--text-base);
		font-weight: 600;
	}

	.lead,
	.hint {
		margin: 0;
		color: var(--color-text-muted);
	}

	.hint {
		font-size: var(--text-sm);
	}

	.steps {
		display: grid;
		gap: var(--space-4);
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.step {
		display: grid;
		gap: var(--space-3);
		align-content: start;
		min-width: 0;
		padding: var(--space-4);
		border: 1px solid var(--color-border-subtle);
		border-radius: var(--radius-field);
		background: var(--color-surface);
	}

	.actions {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	button {
		min-height: 2.75rem; /* alvo de toque de 44px */
		padding: var(--space-2) var(--space-4);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-field);
		background: var(--color-primary);
		border-color: var(--color-primary);
		color: var(--color-on-primary);
		font: inherit;
		font-weight: 600;
		cursor: pointer;
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.share {
		justify-self: start;
		background: transparent;
		color: var(--color-text);
		border-color: var(--color-border);
	}

	.check {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		min-height: 2.75rem;
	}

	.check input {
		width: 1.25rem;
		height: 1.25rem;
	}

	.prompt-label {
		font-weight: 600;
	}

	textarea {
		width: 100%;
		padding: var(--space-3);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-field);
		background: var(--color-bg);
		color: var(--color-text);
		font: inherit;
		font-size: var(--text-sm);
		resize: vertical;
	}

	.status {
		margin: 0;
		font-weight: 600;
	}

	.status.failed {
		color: var(--color-danger);
	}

	.status:empty {
		position: absolute;
	}

	@media (min-width: 64rem) {
		.steps {
			grid-template-columns: repeat(3, minmax(0, 1fr));
			/* Cada cartão tem a altura do próprio conteúdo: o do texto é bem mais alto */
			align-items: start;
		}
	}
</style>
