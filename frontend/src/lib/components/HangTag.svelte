<script lang="ts">
	import type { Snippet } from 'svelte';

	/** Etiqueta de roupa: o elemento de destaque da identidade visual */
	let { children }: { children: Snippet } = $props();
</script>

<div class="tag">
	<span class="hole" aria-hidden="true"></span>
	<div class="stitch">
		{@render children()}
	</div>
</div>

<style>
	.tag {
		/* Os campos dentro da etiqueta usam tons próprios, iguais nos dois temas */
		--field-bg: var(--tag-field-bg);
		--field-text: var(--tag-text);
		--field-muted: var(--tag-text);
		--field-border: var(--tag-text);
		--field-danger: var(--tag-danger);
		--field-focus: var(--tag-focus);

		position: relative;
		padding: var(--space-12) var(--space-4) var(--space-4);
		border-radius: var(--radius-tag) var(--radius-tag) var(--space-2) var(--space-2);
		background: var(--tag-bg);
		color: var(--tag-text);
		box-shadow: 0 1.25rem 2.5rem -1.5rem rgb(60 56 54 / 0.45);
	}

	.hole {
		position: absolute;
		top: var(--space-4);
		left: 50%;
		width: 1.25rem;
		height: 1.25rem;
		translate: -50% 0;
		border: 2px solid var(--tag-stitch);
		border-radius: 50%;
		background: var(--color-bg);
	}

	/* Alinhavo: a costura provisória tracejada da prova de roupa */
	.stitch {
		padding: var(--space-6) var(--space-4);
		border: 2px dashed var(--tag-stitch);
		border-radius: calc(var(--radius-tag) - var(--space-2)) calc(var(--radius-tag) - var(--space-2))
			var(--space-1) var(--space-1);
	}

	.tag :global(a:not(.button)) {
		color: var(--tag-text);
	}

	.tag :global(:focus-visible) {
		outline-color: var(--tag-focus);
	}
</style>
