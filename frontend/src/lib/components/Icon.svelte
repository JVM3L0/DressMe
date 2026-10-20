<script lang="ts">
	export type IconName =
		| 'copy'
		| 'download'
		| 'share'
		| 'eye'
		| 'plus'
		| 'swap'
		| 'accessory'
		| 'outerwear'
		| 'top'
		| 'bottom'
		| 'one_piece'
		| 'footwear';

	interface Props {
		name: IconName;
		/** `sm` 1rem, `md` 1.25rem, `lg` 2rem */
		size?: 'sm' | 'md' | 'lg';
	}

	let { name, size = 'md' }: Props = $props();
</script>

<!-- Ícones de traço, no mesmo estilo do menu. Decorativos: o texto do botão diz o que ele faz. -->
<svg class="icon {size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
	{#if name === 'copy'}
		<rect x="9" y="9" width="11" height="11" rx="2" />
		<path d="M5 15V6a2 2 0 0 1 2-2h9" />
	{:else if name === 'download'}
		<path d="M12 4v11" />
		<path d="m7.5 11 4.5 4.5 4.5-4.5" />
		<path d="M5 20h14" />
	{:else if name === 'share'}
		<circle cx="6" cy="12" r="2.2" />
		<circle cx="17.5" cy="6" r="2.2" />
		<circle cx="17.5" cy="18" r="2.2" />
		<path d="m8 11 7.5-4M8 13l7.5 4" />
	{:else if name === 'eye'}
		<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z" />
		<circle cx="12" cy="12" r="2.8" />
	{:else if name === 'plus'}
		<path d="M12 5v14M5 12h14" />
	{:else if name === 'swap'}
		<path d="M7 7h11l-3-3M17 17H6l3 3" />
	{:else if name === 'accessory'}
		<circle cx="7" cy="14" r="3.2" />
		<circle cx="17" cy="14" r="3.2" />
		<path d="M10.2 14h3.6M3.8 12.5 5 8M20.2 12.5 19 8" />
	{:else if name === 'outerwear'}
		<path d="M8 4 4 8l2 11h4V9l2 2 2-2v10h4l2-11-4-4" />
		<path d="M12 11v8" />
	{:else if name === 'top'}
		<path d="M8.5 4 3.5 7l2 4 2-1v10h9V10l2 1 2-4-5-3a3.5 3.5 0 0 1-7 0z" />
	{:else if name === 'bottom'}
		<path d="M7 4h10l1 16h-4.5L12 10l-1.5 10H6z" />
	{:else if name === 'one_piece'}
		<path d="M9 3h6l-1 6 4 12H6l4-12z" />
		<path d="M9.5 9h5" />
	{:else}
		<path d="M3 15v-3l5-2 3 3h5a5 5 0 0 1 5 5v1H3z" />
		<path d="M3 18h18" />
	{/if}
</svg>

<style>
	/* Tamanhos por classe (a CSP não permite o atributo style) */
	.sm {
		width: 1rem;
		height: 1rem;
	}

	.md {
		width: 1.25rem;
		height: 1.25rem;
	}

	.lg {
		width: 2rem;
		height: 2rem;
	}

	.icon {
		flex: none;
		fill: none;
		stroke: currentColor;
		stroke-width: 1.75;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
</style>
