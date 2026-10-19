<script lang="ts">
	import { resolve } from '$app/paths';
	import { tick } from 'svelte';

	import HangTag from '#lib/components/HangTag.svelte';
	import TextField from '#lib/components/TextField.svelte';
	import { submitSignup, type CreatedUser } from '#lib/signup/submit.ts';
	import {
		PASSWORD_MIN,
		USERNAME_MAX,
		USERNAME_MIN,
		validateField,
		validateSignup,
		type SignupErrors,
		type SignupField,
		type SignupValues
	} from '#lib/signup/validation.ts';

	const FIELD_ORDER: SignupField[] = ['username', 'email', 'password'];

	const FORM_MESSAGES = {
		conflict: 'Já existe uma conta com esse e-mail ou nome de usuário. Use outro.',
		rate_limited: 'Muitas tentativas seguidas. Aguarde um minuto e tente de novo.',
		network_error: 'Não foi possível falar com o servidor. Verifique sua conexão e tente de novo.',
		unexpected: 'Não foi possível criar a conta agora. Tente de novo em instantes.'
	} as const;

	let values: SignupValues = $state({ username: '', email: '', password: '' });
	let errors: SignupErrors = $state({});
	let touched: Partial<Record<SignupField, boolean>> = $state({});
	let formError = $state('');
	let submitting = $state(false);
	let showPassword = $state(false);
	let created: CreatedUser | undefined = $state();

	const inputs: Partial<Record<SignupField, HTMLInputElement>> = $state({});
	let formErrorElement: HTMLParagraphElement | undefined = $state();
	let successHeading: HTMLHeadingElement | undefined = $state();

	/** Valida ao sair do campo, e não a cada tecla, para não interromper quem digita */
	function handleBlur(field: SignupField) {
		touched[field] = true;
		errors[field] = validateField(field, values[field]);
	}

	/** Depois do primeiro erro, a mensagem some assim que o campo fica válido */
	function handleInput(field: SignupField) {
		if (touched[field]) errors[field] = validateField(field, values[field]);
	}

	async function focusFirstError() {
		await tick();
		const first = FIELD_ORDER.find((field) => errors[field]);
		if (first) inputs[first]?.focus();
		else formErrorElement?.focus();
	}

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		formError = '';
		touched = { username: true, email: true, password: true };
		errors = validateSignup(values);
		if (Object.keys(errors).length) return focusFirstError();

		submitting = true;
		const result = await submitSignup(values);
		submitting = false;

		switch (result.kind) {
			case 'created':
				created = result.user;
				// O formulário some: o foco vai para a confirmação
				await tick();
				successHeading?.focus();
				return;
			case 'invalid':
				errors = result.errors;
				break;
			default:
				formError = FORM_MESSAGES[result.kind];
		}
		await focusFirstError();
	}
</script>

<svelte:head>
	<title>Criar conta | VirtualFit</title>
</svelte:head>

<div class="layout">
	<div class="intro">
		<h1>Criar conta</h1>
		<p>Guarde suas fotos e o seu guarda-roupa num lugar só.</p>
	</div>

	<div class="tag-slot">
		<HangTag>
			{#if created}
				<div class="success" role="status">
					<h2 tabindex="-1" bind:this={successHeading}>Conta criada</h2>
					<p>Tudo pronto, {created.username}. O login chega na próxima versão.</p>
					<a href={resolve('/')}>Voltar ao início</a>
				</div>
			{:else}
				<form novalidate onsubmit={handleSubmit}>
					<TextField
						label="Nome de usuário"
						name="username"
						autocomplete="username"
						autocapitalize="none"
						spellcheck="false"
						required
						minlength={USERNAME_MIN}
						maxlength={USERNAME_MAX}
						hint="Letras sem acento, números, ponto, hífen ou sublinhado."
						error={errors.username}
						bind:value={values.username}
						bind:input={inputs.username}
						onblur={() => handleBlur('username')}
						oninput={() => handleInput('username')}
					/>

					<TextField
						label="E-mail"
						name="email"
						type="email"
						autocomplete="email"
						inputmode="email"
						autocapitalize="none"
						spellcheck="false"
						required
						error={errors.email}
						bind:value={values.email}
						bind:input={inputs.email}
						onblur={() => handleBlur('email')}
						oninput={() => handleInput('email')}
					/>

					<TextField
						label="Senha"
						name="password"
						type={showPassword ? 'text' : 'password'}
						autocomplete="new-password"
						required
						minlength={PASSWORD_MIN}
						hint={`Pelo menos ${PASSWORD_MIN} caracteres.`}
						error={errors.password}
						bind:value={values.password}
						bind:input={inputs.password}
						onblur={() => handleBlur('password')}
						oninput={() => handleInput('password')}
					>
						{#snippet trailing()}
							<button
								type="button"
								class="toggle"
								aria-pressed={showPassword}
								onclick={() => (showPassword = !showPassword)}
							>
								{showPassword ? 'Ocultar' : 'Mostrar'}
								<span class="visually-hidden">senha</span>
							</button>
						{/snippet}
					</TextField>

					<p class="form-error" role="alert" tabindex="-1" bind:this={formErrorElement}>
						{formError}
					</p>

					<button class="button" type="submit" disabled={submitting} aria-busy={submitting}>
						{submitting ? 'Criando conta…' : 'Criar conta'}
					</button>
				</form>
			{/if}
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

	form,
	.success {
		display: grid;
		gap: var(--space-6);
	}

	.success h2 {
		font-size: var(--text-2xl);
	}

	.form-error {
		font-weight: 600;
		color: var(--tag-danger);
	}

	/* Vazia, a região continua na árvore de acessibilidade (para anunciar o
	   erro quando ele aparecer), mas fora do fluxo do layout */
	.form-error:empty {
		position: absolute;
	}

	.toggle {
		min-height: 2.75rem;
		padding-inline: var(--space-3);
		border: 1px solid var(--tag-text);
		border-radius: var(--radius-field);
		background: transparent;
		color: var(--tag-text);
		font: inherit;
		font-weight: 600;
		cursor: pointer;
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
