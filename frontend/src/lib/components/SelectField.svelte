<script lang="ts">
	import type { HTMLSelectAttributes } from 'svelte/elements';

	export interface Option {
		value: string;
		label: string;
	}

	interface Props extends Omit<HTMLSelectAttributes, 'value'> {
		label: string;
		name: string;
		options: readonly Option[];
		value?: string;
		/** Primeira opção, sem valor: obriga a pessoa a escolher */
		placeholder?: string;
		hint?: string;
		error?: string;
		input?: HTMLSelectElement;
	}

	let {
		label,
		name,
		options,
		value = $bindable(''),
		placeholder,
		hint,
		error,
		input = $bindable(),
		...rest
	}: Props = $props();

	const id = $props.id();
	const hintId = `${id}-hint`;
	const errorId = `${id}-error`;

	const describedBy = $derived(error ? errorId : hint ? hintId : undefined);
</script>

<div class="field" class:has-error={error}>
	<label for={id}>{label}</label>
	<select
		{id}
		{name}
		bind:value
		bind:this={input}
		aria-invalid={error ? 'true' : undefined}
		aria-describedby={describedBy}
		{...rest}
	>
		{#if placeholder}
			<option value="" disabled>{placeholder}</option>
		{/if}
		{#each options as option (option.value)}
			<option value={option.value}>{option.label}</option>
		{/each}
	</select>
	{#if hint || error}
		<!-- Dica e erro na mesma célula, como no TextField: a altura não muda -->
		<div class="messages">
			{#if hint}
				<p id={hintId} class="hint" class:replaced={error}>{hint}</p>
			{/if}
			{#if error}
				<p id={errorId} class="error">{error}</p>
			{/if}
		</div>
	{/if}
</div>

<style>
	.field {
		display: grid;
		gap: var(--space-1);
	}

	label {
		font-weight: 600;
	}

	select {
		min-height: 2.75rem; /* alvo de toque de 44px */
		padding: var(--space-2) var(--space-3);
		border: 1px solid var(--field-border, var(--color-border));
		border-radius: var(--radius-field);
		background: var(--field-bg, var(--color-surface));
		color: var(--field-text, var(--color-text));
		font: inherit;
	}

	select:focus-visible {
		outline-color: var(--field-focus, var(--color-focus));
	}

	.has-error select {
		border-color: var(--field-danger, var(--color-danger));
		border-width: 2px;
	}

	.messages {
		display: grid;
	}

	.messages > * {
		grid-area: 1 / 1;
	}

	.replaced {
		visibility: hidden;
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
