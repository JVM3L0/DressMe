<script lang="ts">
	import { resolve } from '$app/paths';
	import HangTag from '#lib/components/HangTag.svelte';

	const steps = [
		{
			title: 'Envie sua foto',
			description: 'De corpo inteiro, de frente e com boa luz.'
		},
		{
			title: 'Monte seu guarda-roupa',
			description: 'Fotografe as peças que você já tem.'
		},
		{
			title: 'Prove sem trocar de roupa',
			description: 'Posicione as peças sobre a sua foto e salve o resultado.'
		}
	];
</script>

<svelte:head>
	<title>Experimente antes de vestir | VirtualFit</title>
</svelte:head>

<section class="hero" aria-labelledby="titulo">
	<div class="intro">
		<h1 id="titulo">Experimente antes de vestir.</h1>
		<p class="lead">
			Veja como as suas roupas ficam em você, direto na sua foto. Sem provador, sem trocar de roupa.
		</p>
	</div>

	<div class="tag-slot">
		<HangTag>
			<p class="tag-title">Seu provador</p>
			<p class="tag-text">Crie uma conta para guardar suas fotos e montar seus looks.</p>
			<a class="button" href={resolve('/cadastro')}>Criar conta</a>
			<p class="tag-text">Já tem conta? <a href={resolve('/entrar')}>Entrar</a></p>
		</HangTag>
	</div>
</section>

<section class="how" aria-labelledby="como-funciona">
	<h2 id="como-funciona">Como funciona</h2>
	<ol class="steps">
		{#each steps as step, index (step.title)}
			<li>
				<span class="step-number" aria-hidden="true">{index + 1}</span>
				<div>
					<h3>{step.title}</h3>
					<p>{step.description}</p>
				</div>
			</li>
		{/each}
	</ol>
</section>

<style>
	.hero {
		display: grid;
		gap: var(--space-12);
		align-items: center;
	}

	.intro {
		display: grid;
		gap: var(--space-6);
		max-width: var(--measure);
	}

	h1 {
		font-size: var(--text-display);
		font-weight: 600;
		letter-spacing: -0.01em;
	}

	.lead {
		font-size: var(--text-lg);
		color: var(--color-text-muted);
	}

	.tag-slot {
		width: min(100%, 20rem);
		justify-self: center;
		rotate: -3deg;
		--button-bg: var(--tag-button-bg);
		--button-text: var(--tag-button-text);
	}

	.tag-slot :global(.stitch) {
		display: grid;
		gap: var(--space-4);
	}

	.tag-title {
		font-family: var(--font-display);
		font-size: var(--text-2xl);
		font-weight: 600;
		line-height: var(--leading-tight);
	}

	.how {
		display: grid;
		gap: var(--space-6);
		margin-top: var(--space-16);
	}

	h2 {
		font-size: var(--text-2xl);
	}

	.steps {
		display: grid;
		gap: var(--space-6);
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.steps li {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: var(--space-4);
		align-items: baseline;
	}

	.step-number {
		font-family: var(--font-display);
		font-size: var(--text-2xl);
		font-weight: 600;
		color: var(--color-primary);
		line-height: 1;
	}

	h3 {
		font-family: var(--font-body);
		font-size: var(--text-lg);
		font-weight: 600;
	}

	.steps p {
		color: var(--color-text-muted);
	}

	@media (min-width: 48rem) {
		.hero {
			grid-template-columns: 1.4fr 1fr;
		}

		.steps {
			grid-template-columns: repeat(3, 1fr);
		}
	}
</style>
