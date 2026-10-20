<script lang="ts">
	import { IMAGE_ACCEPT, formatFileSize } from '#lib/media/validation.ts';

	interface Props {
		label: string;
		name?: string;
		/** Arquivo escolhido. Voltar a `undefined` limpa o campo */
		file?: File;
		error?: string;
		hint?: string;
		input?: HTMLInputElement;
		onchange?: () => void;
	}

	let {
		label,
		name = 'file',
		file = $bindable(),
		error,
		hint,
		input = $bindable(),
		onchange
	}: Props = $props();

	const id = $props.id();
	const messageId = `${id}-message`;

	let previewUrl: string | undefined = $state();

	// Pré-visualização local (blob:), antes de enviar; o endereço é liberado
	// quando o arquivo muda ou o componente sai da tela
	$effect(() => {
		if (!file) {
			previewUrl = undefined;
			return;
		}
		const url = URL.createObjectURL(file);
		previewUrl = url;
		return () => URL.revokeObjectURL(url);
	});

	// O navegador não deixa definir o arquivo por código, mas deixa limpar
	$effect(() => {
		if (!file && input) input.value = '';
	});

	function handleChange(event: Event) {
		file = (event.currentTarget as HTMLInputElement).files?.[0];
		onchange?.();
	}

	const message = $derived(error ?? hint);
</script>

<div class="field" class:has-error={error}>
	<label class="picker" for={id}>
		<span class="label">{label}</span>
		<span class="area">
			{#if previewUrl && file}
				<img src={previewUrl} alt="Pré-visualização da imagem escolhida" />
				<span class="file">
					<span class="file-name">{file.name}</span>
					<span class="file-size">{formatFileSize(file.size)}</span>
				</span>
				<span class="action">Trocar</span>
			{:else}
				<span class="text">
					<span class="empty">Escolher imagem</span>
					<span class="action">JPEG ou PNG, até 10 MB</span>
				</span>
			{/if}
		</span>
	</label>
	<input
		{id}
		{name}
		type="file"
		accept={IMAGE_ACCEPT}
		class="visually-hidden"
		bind:this={input}
		aria-invalid={error ? 'true' : undefined}
		aria-describedby={message ? messageId : undefined}
		onchange={handleChange}
	/>
	{#if message}
		<p id={messageId} class={error ? 'error' : 'hint'}>{message}</p>
	{/if}
</div>

<style>
	.field {
		display: grid;
		gap: var(--space-1);
	}

	.picker {
		display: grid;
		gap: var(--space-1);
		cursor: pointer;
	}

	.label {
		font-weight: 600;
	}

	.area {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		min-height: 4.5rem;
		padding: var(--space-3);
		border: 2px dashed var(--field-border, var(--color-border));
		border-radius: var(--radius-field);
		background: var(--field-bg, var(--color-surface));
		color: var(--field-text, var(--color-text));
	}

	/* O campo de arquivo fica fora da tela, e o foco dele aparece na área */
	.field:has(input:focus-visible) .area {
		outline: 3px solid var(--field-focus, var(--color-focus));
		outline-offset: 2px;
	}

	.has-error .area {
		border-color: var(--field-danger, var(--color-danger));
	}

	img {
		width: 3.5rem;
		height: 3.5rem;
		flex: none;
		border-radius: var(--radius-field);
		object-fit: cover;
	}

	.empty {
		font-weight: 600;
	}

	.file {
		display: grid;
		min-width: 0;
		flex: 1;
	}

	.file-name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 600;
	}

	.file-size,
	.action {
		font-size: var(--text-sm);
	}

	.text {
		display: grid;
	}

	.file + .action {
		font-weight: 600;
		text-decoration: underline;
	}

	.hint {
		font-size: var(--text-sm);
		color: var(--field-muted, var(--color-text-muted));
	}

	.error {
		font-size: var(--text-sm);
		font-weight: 600;
		color: var(--field-danger, var(--color-danger));
	}
</style>
