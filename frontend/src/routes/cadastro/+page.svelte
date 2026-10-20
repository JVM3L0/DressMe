<script lang="ts">
	import { resolve } from '$app/paths';
	import { tick } from 'svelte';

	import FormAlert from '#lib/components/FormAlert.svelte';
	import FormPage from '#lib/components/FormPage.svelte';
	import PasswordField from '#lib/components/PasswordField.svelte';
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
	let created: CreatedUser | undefined = $state();

	const inputs: Partial<Record<SignupField, HTMLInputElement>> = $state({});
	let formErrorElement: HTMLParagraphElement | undefined = $state();
	let successHeading: HTMLHeadingElement | undefined = $state();

	/** Valida ao sair do campo, e não a cada tecla, para não interromper quem digita */
	function handleBlur(field: SignupField) {
		touched[field] = true;
		errors[field] = validateField(field, values[field], values);
	}

	/** Depois do primeiro erro, a mensagem some assim que o campo fica válido */
	function handleInput(field: SignupField) {
		if (touched[field]) errors[field] = validateField(field, values[field], values);
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

<FormPage title="Criar conta" lead="Guarde suas fotos e o seu guarda-roupa num lugar só.">
	{#if created}
		<div class="panel" role="status">
			<h2 tabindex="-1" bind:this={successHeading}>Conta criada</h2>
			<p>Tudo pronto, {created.username}. Entre com o seu e-mail e a senha que acabou de criar.</p>
			<a class="button" href={resolve('/entrar')}>Entrar</a>
		</div>
	{:else}
		<form novalidate onsubmit={handleSubmit}>
			<TextField
				label="Nome de usuário"
				name="username"
				autocomplete="nickname"
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

			<!-- O login é por e-mail: o gerenciador de senhas guarda o e-mail (autocomplete
			     "username"), e o nome de usuário é só o apelido (nickname) -->
			<TextField
				label="E-mail"
				name="email"
				type="email"
				autocomplete="username"
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

			<PasswordField
				label="Senha"
				name="password"
				autocomplete="new-password"
				required
				minlength={PASSWORD_MIN}
				hint={`Pelo menos ${PASSWORD_MIN} caracteres. Senhas comuns e com o seu nome não valem.`}
				error={errors.password}
				bind:value={values.password}
				bind:input={inputs.password}
				onblur={() => handleBlur('password')}
				oninput={() => handleInput('password')}
			/>

			<FormAlert message={formError} bind:element={formErrorElement} />

			<button class="button" type="submit" disabled={submitting} aria-busy={submitting}>
				{submitting ? 'Criando conta…' : 'Criar conta'}
			</button>

			<p class="switch">Já tem conta? <a href={resolve('/entrar')}>Entrar</a></p>
		</form>
	{/if}
</FormPage>
