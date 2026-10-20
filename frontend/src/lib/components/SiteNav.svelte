<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';

	import { session } from '#lib/session.svelte.ts';

	const LINKS = [
		{ href: '/fotos', label: 'Fotos', icon: 'camera' },
		{ href: '/guarda-roupa', label: 'Guarda-roupa', icon: 'hanger' },
		{ href: '/provador', label: 'Provador', icon: 'body' },
		{ href: '/conta', label: 'Sua conta', icon: 'user' }
	] as const;

	// `pathname` pode ter barra no fim, conforme o servidor
	const current = $derived(page.url.pathname.replace(/\/$/, ''));
</script>

<!--
	Até a API responder, nada é exibido: não dá para saber se a pessoa tem
	sessão, e mostrar "Entrar" para quem já entrou seria pior que esperar.

	Logado, é o mesmo menu nos dois tamanhos de tela: links no cabeçalho no
	computador e, no celular, uma barra fixa embaixo, ao alcance do polegar,
	com um ícone para cada destino (DT-14).
-->
{#if session.current.status === 'authenticated'}
	<nav class="site-nav bar" aria-label="Principal">
		<ul>
			{#each LINKS as link (link.href)}
				<li>
					<a href={resolve(link.href)} aria-current={current === link.href ? 'page' : undefined}>
						<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
							{#if link.icon === 'camera'}
								<path d="M4 8.5h3l1.5-2.5h7L17 8.5h3V19H4z" />
								<circle cx="12" cy="13.5" r="3.3" />
							{:else if link.icon === 'hanger'}
								<path d="M12 8.2a2.2 2.2 0 1 1 2.2 2.2c-1.2 0-2.2.8-2.2 2.1" />
								<path d="M12 12.5 4.6 17.4a1 1 0 0 0 .6 1.8h13.6a1 1 0 0 0 .6-1.8z" />
							{:else if link.icon === 'body'}
								<circle cx="12" cy="5.2" r="2.3" />
								<path
									d="M8.2 20.5v-6.4L6.4 10a1.4 1.4 0 0 1 1.3-1.9h8.6a1.4 1.4 0 0 1 1.3 1.9l-1.8 4.1v6.4"
								/>
							{:else}
								<circle cx="12" cy="8" r="3.4" />
								<path d="M5 20c.8-3.5 3.5-5.4 7-5.4s6.2 1.9 7 5.4" />
							{/if}
						</svg>
						<span class="label">{link.label}</span>
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
	.site-nav {
		order: 1; /* no cabeçalho: entre o logo e o botão de tema */
	}

	ul {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-1, 0.25rem) var(--space-4, 1rem);
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

	/* Ícones só na barra do celular */
	.icon {
		display: none;
		width: 1.5rem;
		height: 1.5rem;
		fill: none;
		stroke: currentColor;
		stroke-width: 1.75;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	/* Celular, logado: barra fixa embaixo, em quatro colunas iguais */
	@media (max-width: 47.99rem) {
		.bar {
			position: fixed;
			inset: auto 0 0;
			z-index: 10;
			border-top: 1px solid var(--color-border-subtle);
			background: var(--color-bg);
			padding-bottom: env(safe-area-inset-bottom, 0px);
		}

		.bar ul {
			display: grid;
			grid-template-columns: repeat(4, minmax(0, 1fr));
			gap: 0;
		}

		.bar a {
			display: flex;
			flex-direction: column;
			justify-content: center;
			gap: 2px;
			min-height: var(--tabbar-height, 3.5rem);
			padding: var(--space-1, 0.25rem);
			border-top: 3px solid transparent;
			font-size: 0.75rem;
			font-weight: 500;
			text-align: center;
			text-decoration: none;
			color: var(--color-text-muted);
		}

		.bar a:hover {
			text-decoration: none;
			color: var(--color-text);
		}

		.bar a[aria-current='page'] {
			border-top-color: var(--color-primary);
			font-weight: 700;
			color: var(--color-primary);
			text-decoration: none;
		}

		.bar .icon {
			display: block;
		}

		.bar .label {
			max-width: 100%;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}
	}
</style>
