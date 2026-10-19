<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface Props extends Omit<HTMLInputAttributes, 'value'> {
		label: string;
		name: string;
		value?: string;
		hint?: string;
		error?: string;
		/** Conteúdo ao lado do campo, como o botão de mostrar senha */
		trailing?: Snippet;
		input?: HTMLInputElement;
	}

	let {
		label,
		name,
		value = $bindable(''),
		hint,
		error,
		trailing,
		input = $bindable(),
		...rest
	}: Props = $props();

	const id = $props.id();
	const hintId = `${id}-hint`;
	const errorId = `${id}-error`;

	// O erro substitui a dica: as duas juntas repetiriam a mesma orientação
	const describedBy = $derived(error ? errorId : hint ? hintId : undefined);
</script>

<div class="field" class:has-error={error}>
	<label for={id}>{label}</label>
	<div class="control">
		<input
			{id}
			{name}
			bind:value
			bind:this={input}
			aria-invalid={error ? 'true' : undefined}
			aria-describedby={describedBy}
			{...rest}
		/>
		{@render trailing?.()}
	</div>
	{#if hint || error}
		<!-- Dica e erro ocupam a mesma célula: quando o erro substitui a dica, a
		     altura não muda e o botão abaixo não sai do lugar no meio do clique
		     (validar ao sair do campo acontece no mousedown do botão) -->
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

	.control {
		display: flex;
		gap: var(--space-2);
	}

	input {
		flex: 1;
		min-width: 0;
		min-height: 2.75rem; /* alvo de toque de 44px */
		padding: var(--space-2) var(--space-3);
		border: 1px solid var(--field-border, var(--color-border));
		border-radius: var(--radius-field);
		background: var(--field-bg, var(--color-surface));
		color: var(--field-text, var(--color-text));
		font: inherit;
	}

	input:focus-visible {
		outline-color: var(--field-focus, var(--color-focus));
	}

	.has-error input {
		border-color: var(--field-danger, var(--color-danger));
		border-width: 2px;
	}

	.messages {
		display: grid;
	}

	.messages > * {
		grid-area: 1 / 1;
	}

	/* Fora da árvore de acessibilidade, mas reservando o espaço */
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
