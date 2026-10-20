<script lang="ts">
	import { resolve } from '$app/paths';
	import { tick } from 'svelte';

	import FormAlert from '#lib/components/FormAlert.svelte';
	import GarmentPicker from '#lib/components/GarmentPicker.svelte';
	import OutfitOutput from '#lib/components/OutfitOutput.svelte';
	import OutfitSlot from '#lib/components/OutfitSlot.svelte';
	import RequireSession from '#lib/components/RequireSession.svelte';
	import SavedOutfits from '#lib/components/SavedOutfits.svelte';
	import TextField from '#lib/components/TextField.svelte';
	import { FAILURE_MESSAGES, type FailureKind } from '#lib/media/request.ts';
	import {
		OUTFIT_NAME_MAX,
		deleteOutfit,
		listOutfits,
		outfitFailureMessage,
		saveOutfit,
		updateOutfit,
		type Outfit
	} from '#lib/outfit/outfits.ts';
	import {
		choose,
		clear,
		idsOf,
		isEmpty,
		orderedPieces,
		replacedBy,
		selectionFromIds,
		visibleSlots,
		type Selection
	} from '#lib/outfit/slots.ts';
	import { listPhotos, photoImageUrl, photoThumbnailUrl, type Photo } from '#lib/photos/photos.ts';
	import { loadSession, session } from '#lib/session.svelte.ts';
	import type { GarmentCategory } from '#lib/wardrobe/categories.ts';
	import { listGarments, type Garment } from '#lib/wardrobe/garments.ts';

	let garments: Garment[] = $state([]);
	let photos: Photo[] = $state([]);
	let outfits: Outfit[] = $state([]);
	let loading: 'loading' | 'ready' | 'error' = $state('loading');
	let loadError = $state('');

	let selection: Selection = $state({});
	let photoUid: string | undefined = $state();
	let picking: GarmentCategory | undefined = $state();

	let active: Outfit | undefined = $state();
	let outfitName = $state('');
	let nameError = $state('');
	let saving = $state(false);
	let deletingUid: string | undefined = $state();
	let formError = $state('');
	let notice = $state('');

	let stageHeading: HTMLHeadingElement | undefined = $state();
	let nameInput: HTMLInputElement | undefined = $state();

	const pieces = $derived(orderedPieces(selection));
	const slots = $derived(visibleSlots(selection));
	const photo = $derived(photos.find((item) => item.uid === photoUid));

	$effect(() => {
		if (session.current.status === 'authenticated') load();
	});

	/** Sessão vencida: ao marcá-la como anônima, a página manda para o login */
	async function failed(kind: FailureKind): Promise<string> {
		if (kind === 'unauthenticated') await loadSession();
		return FAILURE_MESSAGES[kind];
	}

	async function load() {
		loading = 'loading';
		const [garmentResult, photoResult, outfitResult] = await Promise.all([
			listGarments(),
			listPhotos(),
			listOutfits()
		]);
		if (garmentResult.kind === 'ok' && photoResult.kind === 'ok' && outfitResult.kind === 'ok') {
			garments = garmentResult.data;
			photos = photoResult.data;
			outfits = outfitResult.data;
			// A foto mais recente já vem escolhida
			photoUid ??= photos[0]?.uid;
			loading = 'ready';
			return;
		}
		const problem = [garmentResult, photoResult, outfitResult].find((r) => r.kind !== 'ok');
		loadError = await failed((problem?.kind ?? 'unexpected') as FailureKind);
		loading = 'error';
	}

	function handlePick(garment: Garment) {
		selection = choose(selection, garment);
		picking = undefined;
		notice = '';
	}

	function handleClear(category: GarmentCategory) {
		selection = clear(selection, category);
		notice = '';
	}

	function startOver() {
		selection = {};
		active = undefined;
		outfitName = '';
		nameError = '';
		notice = '';
		formError = '';
	}

	async function handleUse(outfit: Outfit) {
		selection = selectionFromIds(outfit.garment_ids, garments);
		active = outfit;
		outfitName = outfit.name;
		nameError = formError = '';
		const missing = outfit.garment_ids.length - idsOf(selection).length;
		notice =
			missing > 0
				? `Conjunto “${outfit.name}” carregado. ${missing === 1 ? 'Uma peça não existe mais' : `${missing} peças não existem mais`}.`
				: `Conjunto “${outfit.name}” carregado.`;
		// O conjunto aparece no alto da página: leva o foco até lá
		await tick();
		stageHeading?.focus();
		stageHeading?.scrollIntoView({ block: 'start' });
	}

	/** Valida o formulário de salvar; foca o primeiro campo com problema */
	function validateSave(): boolean {
		formError = '';
		nameError = outfitName.trim() ? '' : 'Dê um nome ao conjunto.';
		if (nameError) {
			nameInput?.focus();
			return false;
		}
		if (isEmpty(selection)) {
			formError = 'Escolha ao menos uma peça.';
			return false;
		}
		return true;
	}

	async function save(mode: 'create' | 'update') {
		if (!validateSave()) return;
		saving = true;
		notice = '';
		const ids = idsOf(selection);
		const result =
			mode === 'update' && active
				? await updateOutfit(active.uid, outfitName, ids)
				: await saveOutfit(outfitName, ids);
		saving = false;

		if (result.kind !== 'ok') {
			if (result.kind === 'unauthenticated') await loadSession();
			formError = outfitFailureMessage(result.kind);
			return;
		}
		const saved = result.data;
		outfits =
			mode === 'update'
				? outfits.map((o) => (o.uid === saved.uid ? saved : o))
				: [saved, ...outfits];
		active = saved;
		outfitName = saved.name;
		notice = mode === 'update' ? 'Conjunto atualizado.' : 'Conjunto salvo.';
	}

	async function handleDelete(outfit: Outfit) {
		formError = '';
		notice = '';
		deletingUid = outfit.uid;
		const result = await deleteOutfit(outfit.uid);
		deletingUid = undefined;

		// "Não existe mais" também resolve: o conjunto já não está lá
		if (result.kind === 'ok' || result.kind === 'not_found') {
			outfits = outfits.filter((item) => item.uid !== outfit.uid);
			if (active?.uid === outfit.uid) active = undefined;
			notice = 'Conjunto excluído.';
			return;
		}
		formError = await failed(result.kind);
	}
</script>

<svelte:head>
	<title>Provador | VirtualFit</title>
</svelte:head>

<RequireSession>
	<div class="stack">
		<div class="intro">
			<h1 tabindex="-1" bind:this={stageHeading}>Provador</h1>
			<p>Monte um conjunto com as suas peças e leve para uma IA de imagens vestir a sua foto.</p>
		</div>

		{#if loading === 'loading'}
			<p role="status" class="muted">Carregando seu provador…</p>
		{:else if loading === 'error'}
			<FormAlert message={loadError} />
			<button class="retry" type="button" onclick={load}>Tentar de novo</button>
		{:else if garments.length === 0}
			<p class="muted">
				Seu guarda-roupa está vazio. Para montar um conjunto, primeiro adicione peças.
			</p>
			<a class="button go" href={resolve('/guarda-roupa')}>Ir para o guarda-roupa</a>
		{:else}
			<section class="stage" aria-label="Montagem do conjunto">
				<div class="photo">
					{#if photo}
						<img
							class="main-photo"
							src={photoImageUrl(photo.uid)}
							width={photo.width}
							height={photo.height}
							alt="Sua foto escolhida"
						/>
						{#if photos.length > 1}
							<div class="strip" role="group" aria-label="Trocar foto">
								{#each photos as item, index (item.uid)}
									<button
										type="button"
										aria-pressed={item.uid === photoUid}
										aria-label={`Foto ${index + 1} de ${photos.length}`}
										onclick={() => (photoUid = item.uid)}
									>
										<img src={photoThumbnailUrl(item.uid)} alt="" loading="lazy" decoding="async" />
									</button>
								{/each}
							</div>
						{/if}
					{:else}
						<div class="no-photo">
							<p>Você ainda não enviou nenhuma foto.</p>
							<a href={resolve('/fotos')}>Enviar uma foto</a>
						</div>
					{/if}
				</div>

				<div class="body">
					<!-- Mapa do corpo: cabeça, tronco (agasalho e parte de cima), pernas e pés -->
					<div class="map" role="group" aria-label="Peças do conjunto, na posição do corpo">
						{#each slots as category (category)}
							<div class={['cell', category, selection.one_piece && 'covered']}>
								<OutfitSlot
									{category}
									piece={selection[category]}
									wide={category === 'one_piece'}
									onpick={() => (picking = category)}
									onclear={() => handleClear(category)}
								/>
							</div>
						{/each}
					</div>
					{#if !selection.one_piece}
						<button type="button" class="one-piece" onclick={() => (picking = 'one_piece')}>
							Escolher peça única (vestido, macacão)
						</button>
					{/if}
				</div>
			</section>

			<FormAlert kind="success" message={notice} />

			<section class="save" aria-labelledby="salvar-conjunto">
				<h2 id="salvar-conjunto">
					{active ? `Conjunto: ${active.name}` : 'Salvar este conjunto'}
				</h2>
				<form
					novalidate
					onsubmit={(event) => {
						event.preventDefault();
						save(active ? 'update' : 'create');
					}}
				>
					<TextField
						label="Nome do conjunto"
						name="outfit-name"
						maxlength={OUTFIT_NAME_MAX}
						autocomplete="off"
						hint="Por exemplo: “Look de sexta”."
						error={nameError}
						bind:value={outfitName}
						bind:input={nameInput}
						oninput={() => (nameError = '')}
					/>
					<FormAlert message={formError} />
					<div class="actions">
						<button class="primary" type="submit" disabled={saving} aria-busy={saving}>
							{#if saving}Salvando…{:else if active}Atualizar conjunto{:else}Salvar conjunto{/if}
						</button>
						{#if active}
							<button type="button" disabled={saving} onclick={() => save('create')}>
								Salvar como novo
							</button>
						{/if}
						<button type="button" disabled={saving} onclick={startOver}>Começar de novo</button>
					</div>
				</form>
			</section>

			<OutfitOutput {pieces} photoUid={photo?.uid} />

			<SavedOutfits
				{outfits}
				{garments}
				activeUid={active?.uid}
				{deletingUid}
				onuse={handleUse}
				ondelete={handleDelete}
			/>
		{/if}
	</div>

	<GarmentPicker
		category={picking}
		{garments}
		current={picking ? selection[picking] : undefined}
		replaced={picking ? replacedBy(selection, picking) : []}
		onselect={handlePick}
		onclose={() => (picking = undefined)}
	/>
</RequireSession>

<style>
	.intro {
		display: grid;
		gap: var(--space-2);
		max-width: var(--measure);
	}

	h1 {
		font-size: var(--text-2xl);
	}

	.intro p,
	.muted {
		margin: 0;
		color: var(--color-text-muted);
	}

	.stack {
		display: grid;
		gap: var(--space-8);
	}

	.stage {
		display: grid;
		gap: var(--space-6);
		align-items: start;
	}

	.photo {
		display: grid;
		gap: var(--space-2);
		justify-items: center;
	}

	.main-photo {
		width: 100%;
		max-height: 26rem;
		object-fit: contain;
		border: 1px solid var(--color-border-subtle);
		border-radius: var(--radius-field);
		background: var(--color-surface);
	}

	.strip {
		display: flex;
		gap: var(--space-2);
		max-width: 100%;
		overflow-x: auto;
	}

	.strip button {
		flex: none;
		width: 2.75rem;
		height: 2.75rem;
		padding: 2px;
		border: 2px solid var(--color-border-subtle);
		border-radius: var(--radius-field);
		background: var(--color-surface);
		cursor: pointer;
	}

	.strip button[aria-pressed='true'] {
		border-color: var(--color-primary);
	}

	.strip img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.no-photo {
		display: grid;
		gap: var(--space-2);
		place-content: center;
		justify-items: center;
		width: 100%;
		min-height: 14rem;
		border: 2px dashed var(--color-border);
		border-radius: var(--radius-field);
		text-align: center;
	}

	.no-photo p {
		margin: 0;
		color: var(--color-text-muted);
	}

	.body {
		display: grid;
		gap: var(--space-3);
		justify-items: center;
		width: min(100%, 15rem);
		justify-self: center;
	}

	/* Mapa do corpo: os quadradinhos ficam onde a peça é vestida. Cabeça, pernas e
	   pés são um quadrado no meio; o tronco tem dois (agasalho e parte de cima) */
	.map {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: var(--space-3);
		width: 100%;
	}

	.cell {
		min-width: 0;
	}

	.cell.accessory,
	.cell.bottom,
	.cell.footwear,
	.cell.one_piece {
		grid-column: 1 / -1;
	}

	.cell.accessory,
	.cell.bottom,
	.cell.footwear {
		width: calc(50% - var(--space-3) / 2);
		justify-self: center;
	}

	/* Com a peça única, o agasalho fica sozinho no tronco, centralizado */
	.cell.outerwear.covered {
		grid-column: 1 / -1;
		width: calc(50% - var(--space-3) / 2);
		justify-self: center;
	}

	.one-piece {
		min-height: 2.75rem;
		padding: var(--space-2) var(--space-4);
		border: 1px dashed var(--color-border);
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--color-text-muted);
		font: inherit;
		font-size: var(--text-sm);
		cursor: pointer;
	}

	.one-piece:hover {
		border-color: var(--color-primary);
		color: var(--color-text);
	}

	.save {
		display: grid;
		gap: var(--space-4);
		max-width: 30rem;
	}

	h2 {
		font-size: var(--text-xl);
	}

	.save form {
		display: grid;
		gap: var(--space-4);
	}

	.actions {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}

	.actions button,
	.retry {
		min-height: 2.75rem;
		padding: var(--space-2) var(--space-4);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--color-text);
		font: inherit;
		font-weight: 600;
		cursor: pointer;
	}

	.actions .primary {
		border-color: var(--color-primary);
		background: var(--color-primary);
		color: var(--color-on-primary);
	}

	.actions button:disabled {
		cursor: progress;
		opacity: 0.6;
	}

	.retry {
		justify-self: start;
	}

	.go {
		justify-self: start;
	}

	@media (min-width: 48rem) {
		.stage {
			grid-template-columns: minmax(0, 22rem) minmax(0, 15rem);
			justify-content: start;
			gap: var(--space-8);
			/* A foto tem a altura do mapa do corpo: cabeça, tronco, pernas e pés
			   ficam na altura dos quadradinhos correspondentes */
			align-items: stretch;
		}

		.photo {
			grid-template-rows: minmax(0, 1fr) auto;
		}

		.main-photo {
			height: 100%;
			max-height: none;
		}
	}
</style>
