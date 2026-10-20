<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import type { Snippet } from 'svelte';

	import { session, type CurrentUser } from '#lib/session.svelte.ts';

	/** `children` recebe o usuário: só é exibido com a sessão confirmada */
	let { children }: { children: Snippet<[CurrentUser]> } = $props();

	// Página protegida: sem sessão, vai para o login, sem deixar esta página no
	// histórico (para o "voltar" não cair aqui de novo)
	$effect(() => {
		if (session.current.status === 'anonymous') goto(resolve('/entrar'), { replaceState: true });
	});
</script>

{#if session.current.status === 'authenticated'}
	{@render children(session.current.user)}
{:else}
	<p role="status" class="loading">Carregando…</p>
{/if}

<style>
	.loading {
		color: var(--color-text-muted);
	}
</style>
