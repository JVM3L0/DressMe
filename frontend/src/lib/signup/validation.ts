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

/** Trechos menores que isso aparecem por acaso em senhas boas (ex.: "ana") */
export const PERSONAL_FRAGMENT_MIN = 4;

/**
 * Tipos de problema, compartilhados com os erros 422 da API. `common` e
 * `personal` são da política de senha; a lista de senhas comuns só existe no
 * backend, então `common` chega sempre pela API.
 */
export type Problem = 'missing' | 'too_short' | 'too_long' | 'invalid' | 'common' | 'personal';

type FieldMessages = Record<'missing' | 'too_short' | 'too_long' | 'invalid', string> &
	Partial<Record<Problem, string>>;

export const MESSAGES: Record<SignupField, FieldMessages> = {
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
		invalid: 'Escolha outra senha.',
		common: 'Essa senha é muito comum e fácil de adivinhar. Escolha outra.',
		personal: 'A senha não pode conter o seu nome de usuário ou e-mail.'
	}
};

/** Mensagem de um problema; tipos sem mensagem própria usam a genérica do campo */
export function messageFor(field: SignupField, problem: Problem): string {
	return MESSAGES[field][problem] ?? MESSAGES[field].invalid;
}

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

/** Mesma regra do backend (`password_policy.py`): sem username nem e-mail */
function containsPersonalData(password: string, values?: Partial<SignupValues>): boolean {
	const lowered = password.toLowerCase();
	const fragments = [values?.username?.trim(), values?.email?.trim().split('@')[0]];
	return fragments.some(
		(fragment) =>
			fragment &&
			fragment.length >= PERSONAL_FRAGMENT_MIN &&
			lowered.includes(fragment.toLowerCase())
	);
}

function passwordProblem(value: string, values?: Partial<SignupValues>): Problem | undefined {
	if (!value) return 'missing';
	if (value.length < PASSWORD_MIN) return 'too_short';
	if (byteLength(value) > PASSWORD_MAX_BYTES) return 'too_long';
	if (containsPersonalData(value, values)) return 'personal';
}

type Check = (value: string, values?: Partial<SignupValues>) => Problem | undefined;

const CHECKS: Record<SignupField, Check> = {
	username: usernameProblem,
	email: emailProblem,
	password: passwordProblem
};

/**
 * Mensagem de erro de um campo, ou `undefined` se ele for válido. A senha
 * depende dos outros campos (`values`), que não podem estar contidos nela.
 */
export function validateField(
	field: SignupField,
	value: string,
	values?: Partial<SignupValues>
): string | undefined {
	const problem = CHECKS[field](value, values);
	return problem && messageFor(field, problem);
}

export function validateSignup(values: SignupValues): SignupErrors {
	const errors: SignupErrors = {};
	for (const field of Object.keys(CHECKS) as SignupField[]) {
		const message = validateField(field, values[field], values);
		if (message) errors[field] = message;
	}
	return errors;
}
