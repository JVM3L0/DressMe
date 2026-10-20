<script lang="ts">
	import type { Snippet } from 'svelte';

	import HangTag from './HangTag.svelte';

	interface Props {
		title: string;
		lead: string;
		/** Formulário de envio, dentro da etiqueta */
		form: Snippet;
		/** A coleção (fotos ou peças) */
		children: Snippet;
	}

	let { title, lead, form, children }: Props = $props();
</script>

<!-- Telas de coleção: no celular, o formulário vem antes da lista (sem nada
     ainda, é o que a pessoa precisa); no computador, a etiqueta fica ao lado e
     acompanha a rolagem -->
<div class="layout">
	<div class="intro">
		<h1>{title}</h1>
		<p>{lead}</p>
	</div>

	<div class="tag-slot">
		<HangTag>{@render form()}</HangTag>
	</div>

	<div class="collection">
		{@render children()}
	</div>
</div>

<style>
	.layout {
		display: grid;
		grid-template-areas: 'intro' 'tag' 'collection';
		gap: var(--space-8);
	}

	.intro {
		grid-area: intro;
		display: grid;
		gap: var(--space-2);
		max-width: var(--measure);
	}

	h1 {
		font-size: var(--text-2xl);
	}

	.intro p {
		color: var(--color-text-muted);
	}

	.tag-slot {
		grid-area: tag;
		width: min(100%, 26rem);
		--button-bg: var(--tag-button-bg);
		--button-text: var(--tag-button-text);
	}

	.tag-slot :global(form) {
		display: grid;
		gap: var(--space-6);
	}

	.collection {
		grid-area: collection;
		display: grid;
		gap: var(--space-6);
		align-content: start;
		min-width: 0;
	}

	@media (min-width: 64rem) {
		.layout {
			grid-template-columns: minmax(0, 1fr) 22rem;
			grid-template-areas: 'intro tag' 'collection tag';
			grid-template-rows: auto 1fr;
			column-gap: var(--space-12);
			align-items: start;
		}

		.tag-slot {
			position: sticky;
			top: var(--space-4);
			width: 100%;
		}
	}
</style>
