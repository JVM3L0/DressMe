<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { tick } from 'svelte';

	import FormAlert from '#lib/components/FormAlert.svelte';
	import FormPage from '#lib/components/FormPage.svelte';
	import PasswordField from '#lib/components/PasswordField.svelte';
	import TextField from '#lib/components/TextField.svelte';
	import {
		submitLogin,
		validateLogin,
		type LoginErrors,
		type LoginField,
		type LoginValues
	} from '#lib/login/login.ts';
	import { session, signIn } from '#lib/session.svelte.ts';

	const FIELD_ORDER: LoginField[] = ['email', 'password'];

	const FORM_MESSAGES = {
		invalid_credentials: 'E-mail ou senha incorretos. Confira e tente de novo.',
		rate_limited: 'Muitas tentativas seguidas. Aguarde um minuto e tente de novo.',
		network_error: 'Não foi possível falar com o servidor. Verifique sua conexão e tente de novo.',
		unexpected: 'Não foi possível entrar agora. Tente de novo em instantes.'
	} as const;

	let values: LoginValues = $state({ email: '', password: '' });
	let errors: LoginErrors = $state({});
	let formError = $state('');
	let submitting = $state(false);

	const inputs: Partial<Record<LoginField, HTMLInputElement>> = $state({});
	let formErrorElement: HTMLParagraphElement | undefined = $state();

	// Quem já tem sessão não precisa ver o formulário
	$effect(() => {
		if (session.current.status === 'authenticated') goto(resolve('/conta'), { replaceState: true });
	});

	/** Só limpa o erro do campo editado: aqui não há regras a antecipar */
	function handleInput(field: LoginField) {
		errors[field] = undefined;
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
		errors = validateLogin(values);
		if (Object.keys(errors).length) return focusFirstError();

		submitting = true;
		const result = await submitLogin(values);
		submitting = false;

		if (result.kind === 'authenticated') {
			signIn(result.user);
			return goto(resolve('/conta'));
		}
		formError = FORM_MESSAGES[result.kind];
		// A senha errada é a causa mais comum: o campo é limpo para digitar de novo
		if (result.kind === 'invalid_credentials') values.password = '';
		await focusFirstError();
	}
</script>

<svelte:head>
	<title>Entrar | VirtualFit</title>
</svelte:head>

<FormPage title="Entrar" lead="Continue de onde parou: suas fotos e o seu guarda-roupa.">
	<form novalidate onsubmit={handleSubmit}>
		<!-- O login é por e-mail: é ele que o gerenciador de senhas guarda e preenche -->
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
			oninput={() => handleInput('email')}
		/>

		<PasswordField
			label="Senha"
			name="password"
			autocomplete="current-password"
			required
			error={errors.password}
			bind:value={values.password}
			bind:input={inputs.password}
			oninput={() => handleInput('password')}
		/>

		<FormAlert message={formError} bind:element={formErrorElement} />

		<button class="button" type="submit" disabled={submitting} aria-busy={submitting}>
			{submitting ? 'Entrando…' : 'Entrar'}
		</button>

		<p class="switch">Ainda não tem conta? <a href={resolve('/cadastro')}>Criar conta</a></p>
	</form>
</FormPage>
