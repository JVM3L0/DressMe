<script lang="ts">
	import FormAlert from '#lib/components/FormAlert.svelte';
	import ImagePicker from '#lib/components/ImagePicker.svelte';
	import LibraryPage from '#lib/components/LibraryPage.svelte';
	import MediaCard from '#lib/components/MediaCard.svelte';
	import MediaGrid from '#lib/components/MediaGrid.svelte';
	import RequireSession from '#lib/components/RequireSession.svelte';
	import { FAILURE_MESSAGES, type FailureKind } from '#lib/media/request.ts';
	import { validateImage } from '#lib/media/validation.ts';
	import {
		deletePhoto,
		listPhotos,
		photoThumbnailUrl,
		uploadPhoto,
		type Photo
	} from '#lib/photos/photos.ts';
	import { loadSession, session } from '#lib/session.svelte.ts';

	const dateFormat = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' });

	let photos: Photo[] = $state([]);
	let loading: 'loading' | 'ready' | 'error' = $state('loading');

	let file: File | undefined = $state();
	let fileError = $state('');
	let formError = $state('');
	let notice = $state('');
	let uploading = $state(false);

	let listError = $state('');
	let deletingUid: string | undefined = $state();

	let picker: HTMLInputElement | undefined = $state();
	let formErrorElement: HTMLParagraphElement | undefined = $state();

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
		const result = await listPhotos();
		if (result.kind === 'ok') {
			photos = result.data;
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
		fileError = validateImage(file) ?? '';
		if (!file || fileError) return picker?.focus();

		uploading = true;
		const result = await uploadPhoto(file);
		uploading = false;

		if (result.kind === 'ok') {
			photos = [result.data, ...photos];
			file = undefined;
			notice = 'Foto enviada.';
			return;
		}
		formError = await failed(result.kind);
		formErrorElement?.focus();
	}

	async function handleDelete(photo: Photo) {
		listError = '';
		notice = '';
		deletingUid = photo.uid;
		const result = await deletePhoto(photo.uid);
		deletingUid = undefined;

		// "Não existe mais" também resolve: a foto já não está lá
		if (result.kind === 'ok' || result.kind === 'not_found') {
			photos = photos.filter((item) => item.uid !== photo.uid);
			notice = 'Foto excluída.';
			return;
		}
		listError = await failed(result.kind);
	}
</script>

<svelte:head>
	<title>Fotos | VirtualFit</title>
</svelte:head>

<RequireSession>
	<LibraryPage
		title="Suas fotos"
		lead="As roupas são provadas sobre uma foto sua. Só você vê essas imagens."
	>
		{#snippet form()}
			<form novalidate onsubmit={handleSubmit}>
				<ImagePicker
					label="Nova foto"
					hint="De corpo inteiro, de frente e com boa luz."
					bind:file
					bind:input={picker}
					error={fileError}
					onchange={() => (fileError = '')}
				/>

				<FormAlert message={formError} bind:element={formErrorElement} />

				<button class="button" type="submit" disabled={uploading} aria-busy={uploading}>
					{uploading ? 'Enviando…' : 'Enviar foto'}
				</button>
			</form>
		{/snippet}

		<FormAlert message={listError} />
		<FormAlert kind="success" message={notice} />

		{#if loading === 'loading'}
			<p role="status" class="muted">Carregando suas fotos…</p>
		{:else if loading === 'error'}
			<button class="retry" type="button" onclick={load}>Tentar de novo</button>
		{:else if photos.length === 0}
			<p class="muted">Você ainda não enviou nenhuma foto. Envie a primeira pelo formulário.</p>
		{:else}
			<MediaGrid>
				{#each photos as photo (photo.uid)}
					{@const date = dateFormat.format(new Date(photo.created_at))}
					<li>
						<MediaCard
							src={photoThumbnailUrl(photo.uid)}
							width={photo.width}
							height={photo.height}
							alt={`Foto enviada em ${date}`}
							title={date}
							detail={`${photo.width} × ${photo.height}`}
							subject="foto"
							busy={deletingUid === photo.uid}
							ondelete={() => handleDelete(photo)}
						/>
					</li>
				{/each}
			</MediaGrid>
		{/if}
	</LibraryPage>
</RequireSession>

<style>
	.muted {
		color: var(--color-text-muted);
	}

	.retry {
		justify-self: start;
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
