<script lang="ts">
	import CategoryFilter from '#lib/components/CategoryFilter.svelte';
	import FormAlert from '#lib/components/FormAlert.svelte';
	import ImagePicker from '#lib/components/ImagePicker.svelte';
	import LibraryPage from '#lib/components/LibraryPage.svelte';
	import MediaCard from '#lib/components/MediaCard.svelte';
	import MediaGrid from '#lib/components/MediaGrid.svelte';
	import RequireSession from '#lib/components/RequireSession.svelte';
	import SelectField from '#lib/components/SelectField.svelte';
	import TextField from '#lib/components/TextField.svelte';
	import { FAILURE_MESSAGES, type FailureKind } from '#lib/media/request.ts';
	import { validateImage } from '#lib/media/validation.ts';
	import { loadSession, session } from '#lib/session.svelte.ts';
	import {
		CATEGORIES,
		GARMENT_NAME_MAX,
		categoryLabel,
		countByCategory,
		isCategory,
		type GarmentCategory
	} from '#lib/wardrobe/categories.ts';
	import {
		addGarment,
		deleteGarment,
		garmentThumbnailUrl,
		listGarments,
		type Garment
	} from '#lib/wardrobe/garments.ts';

	const CATEGORY_OPTIONS = CATEGORIES.map(({ value, label }) => ({ value, label }));

	let garments: Garment[] = $state([]);
	let loading: 'loading' | 'ready' | 'error' = $state('loading');
	let filter: GarmentCategory | undefined = $state();

	let file: File | undefined = $state();
	let category = $state('');
	let name = $state('');
	let errors: { file?: string; category?: string } = $state({});
	let formError = $state('');
	let notice = $state('');
	let saving = $state(false);

	let listError = $state('');
	let deletingUid: string | undefined = $state();

	let picker: HTMLInputElement | undefined = $state();
	let categoryInput: HTMLSelectElement | undefined = $state();
	let formErrorElement: HTMLParagraphElement | undefined = $state();

	const counts = $derived(countByCategory(garments));
	const visible = $derived(filter ? garments.filter((item) => item.category === filter) : garments);
	const examples = $derived(CATEGORIES.find((item) => item.value === category)?.examples);

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
		const result = await listGarments();
		if (result.kind === 'ok') {
			garments = result.data;
			loading = 'ready';
		} else {
			listError = await failed(result.kind);
			loading = 'error';
		}
	}

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		formError = '';
		notice = '';
		errors = {
			file: validateImage(file),
			category: isCategory(category) ? undefined : 'Escolha a categoria da peça.'
		};
		if (errors.file) return picker?.focus();
		if (errors.category) return categoryInput?.focus();
		if (!file || !isCategory(category)) return;

		saving = true;
		const result = await addGarment({ file, category, name });
		saving = false;

		if (result.kind === 'ok') {
			garments = [result.data, ...garments];
			// A categoria fica, para cadastrar várias peças do mesmo tipo em sequência
			file = undefined;
			name = '';
			notice = 'Peça adicionada.';
			return;
		}
		formError = await failed(result.kind);
		formErrorElement?.focus();
	}

	async function handleDelete(garment: Garment) {
		listError = '';
		notice = '';
		deletingUid = garment.uid;
		const result = await deleteGarment(garment.uid);
		deletingUid = undefined;

		// "Não existe mais" também resolve: a peça já não está lá
		if (result.kind === 'ok' || result.kind === 'not_found') {
			garments = garments.filter((item) => item.uid !== garment.uid);
			notice = 'Peça excluída.';
			return;
		}
		listError = await failed(result.kind);
	}
</script>

<svelte:head>
	<title>Guarda-roupa | VirtualFit</title>
</svelte:head>

<RequireSession>
	<LibraryPage
		title="Guarda-roupa"
		lead="Fotografe as peças que você já tem. Fundo liso, ou PNG recortado, fica melhor na prova."
	>
		{#snippet form()}
			<form novalidate onsubmit={handleSubmit}>
				<ImagePicker
					label="Foto da peça"
					bind:file
					bind:input={picker}
					error={errors.file}
					onchange={() => (errors.file = undefined)}
				/>

				<SelectField
					label="Categoria"
					name="category"
					placeholder="Escolha a categoria"
					options={CATEGORY_OPTIONS}
					required
					hint={examples ? `Por exemplo: ${examples}.` : 'Onde a peça é vestida.'}
					error={errors.category}
					bind:value={category}
					bind:input={categoryInput}
					onchange={() => (errors.category = undefined)}
				/>

				<TextField
					label="Nome (opcional)"
					name="name"
					maxlength={GARMENT_NAME_MAX}
					autocomplete="off"
					hint="Inclua a cor e o tipo, como “Camisa de linho azul”. O nome também descreve a peça para a IA."
					bind:value={name}
				/>

				<FormAlert message={formError} bind:element={formErrorElement} />

				<button class="button" type="submit" disabled={saving} aria-busy={saving}>
					{saving ? 'Enviando…' : 'Adicionar peça'}
				</button>
			</form>
		{/snippet}

		<FormAlert message={listError} />
		<FormAlert kind="success" message={notice} />

		{#if loading === 'loading'}
			<p role="status" class="muted">Carregando seu guarda-roupa…</p>
		{:else if loading === 'error'}
			<button class="button secondary retry" type="button" onclick={load}>Tentar de novo</button>
		{:else if garments.length === 0}
			<p class="muted">Seu guarda-roupa está vazio. Adicione a primeira peça pelo formulário.</p>
		{:else}
			<CategoryFilter bind:selected={filter} {counts} total={garments.length} />

			{#if visible.length === 0}
				<p class="muted">Nenhuma peça nessa categoria ainda.</p>
			{:else}
				<MediaGrid>
					{#each visible as garment (garment.uid)}
						{@const label = categoryLabel(garment.category)}
						<li>
							<MediaCard
								src={garmentThumbnailUrl(garment.uid)}
								width={garment.width}
								height={garment.height}
								alt={garment.name ?? label}
								title={garment.name ?? label}
								detail={garment.name ? label : undefined}
								subject={garment.name ?? label}
								busy={deletingUid === garment.uid}
								ondelete={() => handleDelete(garment)}
							/>
						</li>
					{/each}
				</MediaGrid>
			{/if}
		{/if}
	</LibraryPage>
</RequireSession>

<style>
	.muted {
		color: var(--color-text-muted);
	}

	.retry {
		justify-self: start;
	}
</style>
