<script lang="ts">
	import type { Snippet } from 'svelte';

	/** Grade de cartas: duas colunas no celular, mais conforme a largura */
	let { children }: { children: Snippet } = $props();
</script>

<ul class="grid">
	{@render children()}
</ul>

<style>
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(9.5rem, 1fr));
		gap: var(--space-6) var(--space-4);
		margin: 0;
		padding: 0;
		list-style: none;
	}
</style>
