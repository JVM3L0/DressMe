<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';

	import { session } from '#lib/session.svelte.ts';

	const LINKS = [
		{ href: '/fotos', label: 'Fotos' },
		{ href: '/guarda-roupa', label: 'Guarda-roupa' },
		{ href: '/provador', label: 'Provador' },
		{ href: '/conta', label: 'Sua conta' }
	] as const;

	// `pathname` pode ter barra no fim, conforme o servidor
	const current = $derived(page.url.pathname.replace(/\/$/, ''));
</script>

<!-- Até a API responder, nada é exibido: não dá para saber se a pessoa tem
     sessão, e mostrar "Entrar" para quem já entrou seria pior que esperar -->
{#if session.current.status === 'authenticated'}
	<nav class="site-nav" aria-label="Principal">
		<ul>
			{#each LINKS as link (link.href)}
				<li>
					<a href={resolve(link.href)} aria-current={current === link.href ? 'page' : undefined}>
						{link.label}
					</a>
				</li>
			{/each}
		</ul>
	</nav>
{:else if session.current.status === 'anonymous'}
	<nav class="site-nav" aria-label="Principal">
		<ul>
			<li>
				<a href={resolve('/entrar')} aria-current={current === '/entrar' ? 'page' : undefined}>
					Entrar
				</a>
			</li>
		</ul>
	</nav>
{/if}

<style>
	ul {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-1) var(--space-4);
		margin: 0;
		padding: 0;
		list-style: none;
	}

	a {
		display: inline-flex;
		align-items: center;
		min-height: 2.75rem; /* alvo de toque de 44px */
		font-weight: 600;
		color: var(--color-text);
		text-decoration-thickness: 1px;
		text-underline-offset: 0.3em;
	}

	a:not([aria-current='page']) {
		text-decoration: none;
	}

	a:not([aria-current='page']):hover {
		text-decoration: underline;
	}
</style>
