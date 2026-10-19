import {
	messageFor,
	type Problem,
	type SignupErrors,
	type SignupField
} from '#lib/signup/validation.ts';

/** Erro de validação no formato do FastAPI (o handler remove o `input`) */
export interface ValidationIssue {
	loc: (string | number)[];
	type: string;
	msg: string;
}

const PROBLEM_BY_TYPE: Record<string, Problem> = {
	missing: 'missing',
	string_too_short: 'too_short',
	string_too_long: 'too_long',
	string_pattern_mismatch: 'invalid',
	value_error: 'invalid',
	string_type: 'invalid',
	password_common: 'common',
	password_personal: 'personal'
};

const FIELDS: readonly SignupField[] = ['username', 'email', 'password'];

const isSignupField = (value: unknown): value is SignupField =>
	FIELDS.includes(value as SignupField);

/**
 * Traduz os erros 422 do backend para as mesmas mensagens da validação no
 * navegador. O limite de bytes da senha chega como `value_error`, por isso é
 * identificado pela mensagem.
 */
export function signupErrorsFromApi(issues: ValidationIssue[]): SignupErrors {
	const errors: SignupErrors = {};
	for (const issue of issues) {
		const [location, field] = issue.loc;
		if (location !== 'body' || !isSignupField(field) || errors[field]) continue;

		const problem =
			field === 'password' && issue.msg.includes('72 bytes')
				? 'too_long'
				: (PROBLEM_BY_TYPE[issue.type] ?? 'invalid');
		errors[field] = messageFor(field, problem);
	}
	return errors;
}
