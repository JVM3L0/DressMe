import { api } from '#lib/api/client.ts';
import { signupErrorsFromApi, type ValidationIssue } from '#lib/api/errors.ts';
import type { components } from '#lib/api/schema.ts';

import type { SignupErrors, SignupValues } from './validation.ts';

export type CreatedUser = components['schemas']['UserPublic'];

export type SignupResult =
	| { kind: 'created'; user: CreatedUser }
	| { kind: 'invalid'; errors: SignupErrors }
	| { kind: 'conflict' }
	| { kind: 'rate_limited' }
	| { kind: 'network_error' }
	| { kind: 'unexpected' };

/** Cria a conta e traduz cada resposta da API num resultado que a tela entende */
export async function submitSignup(values: SignupValues): Promise<SignupResult> {
	try {
		const { data, error, response } = await api.POST('/users/', { body: values });

		if (data) return { kind: 'created', user: data };

		switch (response.status) {
			case 409:
				return { kind: 'conflict' };
			case 422:
				return {
					kind: 'invalid',
					errors: signupErrorsFromApi((error?.detail ?? []) as ValidationIssue[])
				};
			case 429:
				return { kind: 'rate_limited' };
			default:
				return { kind: 'unexpected' };
		}
	} catch {
		return { kind: 'network_error' };
	}
}
