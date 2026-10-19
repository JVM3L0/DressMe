<script lang="ts">
	import { resolve } from '$app/paths';

	import { session } from '#lib/session.svelte.ts';
</script>

<!-- Até a API responder, o espaço fica reservado (sem texto) para o
     cabeçalho não pular quando o link aparecer -->
{#if session.current.status === 'authenticated'}
	<a class="account" href={resolve('/conta')}>Sua conta</a>
{:else if session.current.status === 'anonymous'}
	<a class="account" href={resolve('/entrar')}>Entrar</a>
{:else}
	<span class="account" aria-hidden="true"></span>
{/if}

<style>
	.account {
		display: inline-flex;
		align-items: center;
		min-width: 5.5rem;
		min-height: 2.75rem; /* alvo de toque de 44px */
		justify-content: center;
		font-weight: 600;
		color: var(--color-text);
	}
</style>
