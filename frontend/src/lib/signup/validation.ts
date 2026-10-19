/**
 * Regras do cadastro, espelhando o backend (`UserCreate`). A validação no
 * navegador só antecipa erros para o usuário; o backend continua sendo a
 * fonte da verdade.
 */

export type SignupField = 'username' | 'email' | 'password';

export type SignupValues = Record<SignupField, string>;

export type SignupErrors = Partial<Record<SignupField, string>>;

export const USERNAME_MIN = 3;
export const USERNAME_MAX = 255;
export const PASSWORD_MIN = 8;
/** Limite do bcrypt, em bytes (letras acentuadas ocupam 2 bytes) */
export const PASSWORD_MAX_BYTES = 72;

const USERNAME_PATTERN = /^[A-Za-z0-9_.-]+$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Tipos de problema, compartilhados com os erros 422 da API */
export type Problem = 'missing' | 'too_short' | 'too_long' | 'invalid';

export const MESSAGES: Record<SignupField, Record<Problem, string>> = {
	username: {
		missing: 'Informe um nome de usuário.',
		too_short: `Use pelo menos ${USERNAME_MIN} caracteres.`,
		too_long: `Use no máximo ${USERNAME_MAX} caracteres.`,
		invalid: 'Use só letras sem acento, números, ponto, hífen ou sublinhado.'
	},
	email: {
		missing: 'Informe seu e-mail.',
		too_short: 'Informe um e-mail válido, como nome@exemplo.com.',
		too_long: 'Use um e-mail mais curto.',
		invalid: 'Informe um e-mail válido, como nome@exemplo.com.'
	},
	password: {
		missing: 'Crie uma senha.',
		too_short: `Use pelo menos ${PASSWORD_MIN} caracteres.`,
		too_long: 'Use uma senha mais curta. Letras com acento contam em dobro.',
		invalid: 'Escolha outra senha.'
	}
};

const byteLength = (value: string) => new TextEncoder().encode(value).length;

function usernameProblem(raw: string): Problem | undefined {
	const value = raw.trim();
	if (!value) return 'missing';
	if (value.length < USERNAME_MIN) return 'too_short';
	if (value.length > USERNAME_MAX) return 'too_long';
	if (!USERNAME_PATTERN.test(value)) return 'invalid';
}

function emailProblem(raw: string): Problem | undefined {
	const value = raw.trim();
	if (!value) return 'missing';
	if (value.length > 255) return 'too_long';
	if (!EMAIL_PATTERN.test(value)) return 'invalid';
}

function passwordProblem(value: string): Problem | undefined {
	if (!value) return 'missing';
	if (value.length < PASSWORD_MIN) return 'too_short';
	if (byteLength(value) > PASSWORD_MAX_BYTES) return 'too_long';
}

const CHECKS: Record<SignupField, (value: string) => Problem | undefined> = {
	username: usernameProblem,
	email: emailProblem,
	password: passwordProblem
};

/** Mensagem de erro de um campo, ou `undefined` se ele for válido */
export function validateField(field: SignupField, value: string): string | undefined {
	const problem = CHECKS[field](value);
	return problem && MESSAGES[field][problem];
}

export function validateSignup(values: SignupValues): SignupErrors {
	const errors: SignupErrors = {};
	for (const field of Object.keys(CHECKS) as SignupField[]) {
		const message = validateField(field, values[field]);
		if (message) errors[field] = message;
	}
	return errors;
}
