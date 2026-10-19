<script lang="ts">
	import type { ComponentProps } from 'svelte';

	import TextField from './TextField.svelte';

	type Props = Omit<ComponentProps<typeof TextField>, 'type' | 'trailing'>;

	let { value = $bindable(''), input = $bindable(), ...rest }: Props = $props();

	let visible = $state(false);
</script>

<TextField type={visible ? 'text' : 'password'} bind:value bind:input {...rest}>
	{#snippet trailing()}
		<button
			type="button"
			class="toggle"
			aria-pressed={visible}
			onclick={() => (visible = !visible)}
		>
			{visible ? 'Ocultar' : 'Mostrar'}
			<span class="visually-hidden">senha</span>
		</button>
	{/snippet}
</TextField>

<style>
	.toggle {
		min-height: 2.75rem;
		padding-inline: var(--space-3);
		border: 1px solid var(--field-text, var(--color-text));
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--field-text, var(--color-text));
		font: inherit;
		font-weight: 600;
		cursor: pointer;
	}
</style>
