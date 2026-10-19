<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	import FormAlert from '#lib/components/FormAlert.svelte';
	import FormPage from '#lib/components/FormPage.svelte';
	import { session, signOut } from '#lib/session.svelte.ts';

	const memberSince = new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' });

	let signingOut = $state(false);
	let formError = $state('');
	let formErrorElement: HTMLParagraphElement | undefined = $state();

	// Página protegida: sem sessão, vai para o login (sem deixar esta página
	// no histórico, para o "voltar" não cair aqui de novo)
	$effect(() => {
		if (session.current.status === 'anonymous') goto(resolve('/entrar'), { replaceState: true });
	});

	async function handleSignOut() {
		formError = '';
		signingOut = true;
		const done = await signOut();
		signingOut = false;

		if (done) return goto(resolve('/'));
		formError = 'Não foi possível sair agora. Verifique sua conexão e tente de novo.';
		formErrorElement?.focus();
	}
</script>

<svelte:head>
	<title>Sua conta | VirtualFit</title>
</svelte:head>

<FormPage title="Sua conta" lead="Em breve, suas fotos e o seu guarda-roupa ficam aqui.">
	{#if session.current.status === 'authenticated'}
		{@const user = session.current.user}
		<div class="panel">
			<h2>{user.username}</h2>
			<dl>
				<dt>E-mail</dt>
				<dd>{user.email}</dd>
				<dt>Conta criada em</dt>
				<dd>{memberSince.format(new Date(user.created_at))}</dd>
			</dl>

			<FormAlert message={formError} bind:element={formErrorElement} />

			<button
				class="button"
				type="button"
				disabled={signingOut}
				aria-busy={signingOut}
				onclick={handleSignOut}
			>
				{signingOut ? 'Saindo…' : 'Sair'}
			</button>
		</div>
	{:else}
		<p class="panel" role="status">Carregando sua conta…</p>
	{/if}
</FormPage>

<style>
	dl {
		display: grid;
		gap: var(--space-1);
		margin: 0;
	}

	dt {
		font-size: var(--text-sm);
	}

	dd {
		margin: 0 0 var(--space-3);
		font-weight: 600;
		overflow-wrap: anywhere;
	}
</style>
