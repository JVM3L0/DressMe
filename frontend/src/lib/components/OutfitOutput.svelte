<script lang="ts">
	import { onDestroy, untrack } from 'svelte';

	import {
		canCopyImages,
		canShareFiles,
		copyImage,
		copyText,
		downloadBlob,
		shareFiles
	} from '#lib/outfit/clipboard.ts';
	import { composeCollage } from '#lib/outfit/collage.ts';
	import { clothesAsPng, fetchImage, photoAsPng } from '#lib/outfit/images.ts';
	import { NOTE_MAX, buildPrompt } from '#lib/outfit/prompt.ts';
	import type { Piece } from '#lib/outfit/slots.ts';
	import { garmentThumbnailUrl } from '#lib/wardrobe/garments.ts';

	import Icon from './Icon.svelte';
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

	// Pré-visualização do que será colado: a mesma montagem, só que com as miniaturas
	// (leves), refeita quando o conjunto muda. O endereço é liberado ao trocar.
	let previewUrl: string | undefined = $state();

	$effect(() => {
		const items = pieces;
		if (items.length === 0) {
			previewUrl = undefined;
			return;
		}
		let cancelled = false;
		let url: string | undefined;
		(async () => {
			try {
				const images = await Promise.all(
					items.map((piece) => fetchImage(garmentThumbnailUrl(piece.uid)))
				);
				const collage = await composeCollage(images);
				if (cancelled) return;
				url = URL.createObjectURL(collage);
				previewUrl = url;
			} catch {
				// Sem pré-visualização, as cópias continuam funcionando
				if (!cancelled) previewUrl = undefined;
			}
		})();
		return () => {
			cancelled = true;
			if (url) URL.revokeObjectURL(url);
		};
	});

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

	// Sem a cópia por botão (em HTTP, o navegador bloqueia), a imagem aparece na tela e
	// a pessoa a copia segurando o dedo sobre ela: "Copiar imagem" é do próprio navegador
	// e não depende de HTTPS. O endereço da imagem é liberado ao trocar ou ao sair.
	let shown: 'photo' | 'clothes' | undefined = $state();
	let shownUrl: string | undefined = $state();

	function setShown(kind: 'photo' | 'clothes' | undefined, url?: string) {
		if (shownUrl) URL.revokeObjectURL(shownUrl);
		shown = kind;
		shownUrl = url;
	}

	// Uma imagem de um conjunto ou de uma foto antiga não deve ficar na tela
	$effect(() => {
		void pieces;
		void photoUid;
		untrack(() => setShown(undefined));
	});

	onDestroy(() => {
		if (shownUrl) URL.revokeObjectURL(shownUrl);
	});

	const HOLD_HINT = 'Segure a imagem e toque em “Copiar imagem”.';

	function reveal(kind: 'photo' | 'clothes') {
		if (shown === kind) return setShown(undefined);
		return run(`reveal-${kind}`, HOLD_HINT, async () => {
			const blob = kind === 'photo' ? await photoAsPng(photoUid!) : await clothesAsPng(pieces);
			setShown(kind, URL.createObjectURL(blob));
		});
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
		Copie os três itens e cole, nesta ordem, na IA que preferir. O VirtualFit não envia nada, e a
		sua foto passa a seguir as regras de privacidade da ferramenta onde você a colar.
	</p>

	<ol class="steps">
		<li class="step">
			<h3>1. Sua foto</h3>
			<div class="button-group">
				{#if copyImages}
					<button
						type="button"
						class="button"
						disabled={!photoUid || busy !== undefined}
						onclick={copyPhoto}
					>
						<Icon name="copy" />
						{busy === 'photo' ? 'Copiando…' : 'Copiar foto'}
					</button>
				{:else}
					<button
						type="button"
						class="button secondary"
						aria-pressed={shown === 'photo'}
						disabled={!photoUid || busy !== undefined}
						onclick={() => reveal('photo')}
					>
						<Icon name="eye" />
						{shown === 'photo' ? 'Esconder foto' : 'Mostrar foto para copiar'}
					</button>
				{/if}
				<button
					type="button"
					class="button secondary"
					disabled={!photoUid || busy !== undefined}
					onclick={downloadPhoto}
				>
					<Icon name="download" />
					Baixar foto
				</button>
			</div>
			{#if shown === 'photo' && shownUrl}
				<img class="reveal" src={shownUrl} alt="Sua foto: segure a imagem para copiar" />
				<p class="hint">{HOLD_HINT}</p>
			{/if}
			{#if !photoUid}<p class="hint">Escolha uma foto acima.</p>{/if}
		</li>

		<li class="step">
			<h3>2. As roupas</h3>
			<div class="button-group">
				{#if copyImages}
					<button
						type="button"
						class="button"
						disabled={!hasPieces || busy !== undefined}
						onclick={copyClothes}
					>
						<Icon name="copy" />
						{busy === 'clothes' ? 'Copiando…' : 'Copiar roupas'}
					</button>
				{:else}
					<button
						type="button"
						class="button secondary"
						aria-pressed={shown === 'clothes'}
						disabled={!hasPieces || busy !== undefined}
						onclick={() => reveal('clothes')}
					>
						<Icon name="eye" />
						{shown === 'clothes' ? 'Esconder roupas' : 'Mostrar roupas para copiar'}
					</button>
				{/if}
				<button
					type="button"
					class="button secondary"
					disabled={!hasPieces || busy !== undefined}
					onclick={downloadClothes}
				>
					<Icon name="download" />
					Baixar roupas
				</button>
			</div>
			{#if shown === 'clothes' && shownUrl}
				<img class="reveal" src={shownUrl} alt="Imagem das roupas: segure a imagem para copiar" />
				<p class="hint">{HOLD_HINT}</p>
			{:else if previewUrl && hasPieces}
				<img class="preview" src={previewUrl} alt="Pré-visualização da imagem das roupas" />
			{/if}
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
			<textarea id="prompt-text" readonly rows="6" value={hasPieces ? prompt : ''}></textarea>
			<div class="button-group">
				<button
					type="button"
					class="button"
					disabled={!hasPieces || busy !== undefined}
					onclick={copyPrompt}
				>
					<Icon name="copy" />
					{busy === 'prompt' ? 'Copiando…' : 'Copiar texto'}
				</button>
			</div>
		</li>
	</ol>

	{#if shareable}
		<button
			type="button"
			class="button secondary"
			disabled={!photoUid || !hasPieces || busy !== undefined}
			onclick={share}
		>
			<Icon name="share" />
			Compartilhar tudo
		</button>
	{/if}

	{#if !copyImages}
		<p class="hint">
			Este endereço não é seguro (HTTPS), então o navegador não deixa copiar imagens com um toque.
			Use “Mostrar para copiar” (segure a imagem) ou Baixar. Por HTTPS, aparece o botão Copiar.
		</p>
	{/if}

	<p class="status" class:failed role={failed ? 'alert' : 'status'}>{message}</p>
</section>

<style>
	.output {
		display: grid;
		gap: var(--space-3);
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
		gap: var(--space-3);
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.step {
		display: grid;
		gap: var(--space-2);
		align-content: start;
		min-width: 0;
		padding: var(--space-3) var(--space-4);
		border: 1px solid var(--color-border-subtle);
		border-radius: var(--radius-field);
		background: var(--color-surface);
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
</style>
