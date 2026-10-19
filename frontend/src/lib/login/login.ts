import { api } from '#lib/api/client.ts';
import type { CurrentUser } from '#lib/session.svelte.ts';
import { validateField } from '#lib/signup/validation.ts';

export type LoginField = 'email' | 'password';

export type LoginValues = Record<LoginField, string>;

export type LoginErrors = Partial<Record<LoginField, string>>;

export const LOGIN_MESSAGES = {
	passwordMissing: 'Informe sua senha.'
} as const;

/**
 * Só confere o preenchimento: as regras de senha valem para senhas novas, e
 * uma conta antiga pode ter uma senha que hoje seria recusada.
 */
export function validateLogin(values: LoginValues): LoginErrors {
	const errors: LoginErrors = {};
	const email = validateField('email', values.email);
	if (email) errors.email = email;
	if (!values.password) errors.password = LOGIN_MESSAGES.passwordMissing;
	return errors;
}

export type LoginResult =
	| { kind: 'authenticated'; user: CurrentUser }
	| { kind: 'invalid_credentials' }
	| { kind: 'rate_limited' }
	| { kind: 'network_error' }
	| { kind: 'unexpected' };

/** Inicia a sessão; a API grava o cookie e devolve o usuário */
export async function submitLogin(values: LoginValues): Promise<LoginResult> {
	try {
		const { data, response } = await api.POST('/auth/login', {
			body: { email: values.email.trim(), password: values.password }
		});

		if (data) return { kind: 'authenticated', user: data };

		switch (response.status) {
			// 422 só passa da validação do navegador com um e-mail que o backend
			// recusa; para quem entra, é o mesmo que credenciais erradas
			case 401:
			case 422:
				return { kind: 'invalid_credentials' };
			case 429:
				return { kind: 'rate_limited' };
			default:
				return { kind: 'unexpected' };
		}
	} catch {
		return { kind: 'network_error' };
	}
}
