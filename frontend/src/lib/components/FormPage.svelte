<script lang="ts">
	import type { Snippet } from 'svelte';

	import HangTag from './HangTag.svelte';

	interface Props {
		title: string;
		lead: string;
		/** Conteúdo da etiqueta: o formulário ou a confirmação */
		children: Snippet;
	}

	let { title, lead, children }: Props = $props();
</script>

<!-- Layout das telas de conta: o texto à esquerda e a etiqueta à direita (no
     celular, um embaixo do outro) -->
<div class="layout">
	<div class="intro">
		<h1>{title}</h1>
		<p>{lead}</p>
	</div>

	<div class="tag-slot">
		<HangTag>
			{@render children()}
		</HangTag>
	</div>
</div>

<style>
	.layout {
		display: grid;
		gap: var(--space-8);
		justify-items: center;
	}

	.intro {
		display: grid;
		gap: var(--space-2);
		width: min(100%, 26rem);
	}

	h1 {
		font-size: var(--text-2xl);
	}

	.intro p {
		color: var(--color-text-muted);
	}

	.tag-slot {
		width: min(100%, 26rem);
		--button-bg: var(--tag-button-bg);
		--button-text: var(--tag-button-text);
	}

	.tag-slot :global(form),
	.tag-slot :global(.panel) {
		display: grid;
		gap: var(--space-6);
	}

	.tag-slot :global(.panel h2) {
		font-size: var(--text-2xl);
	}

	/* Link para a outra tela de conta ("Já tem conta? Entrar") */
	.tag-slot :global(.switch) {
		text-align: center;
	}

	@media (min-width: 48rem) {
		.layout {
			grid-template-columns: 1fr 26rem;
			align-items: start;
			justify-items: start;
		}

		.intro {
			padding-top: var(--space-12);
		}
	}
</style>
