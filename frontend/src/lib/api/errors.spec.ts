import { describe, expect, it } from 'vitest';

import { MESSAGES } from '#lib/signup/validation.ts';

import { signupErrorsFromApi } from './errors.ts';

describe('signupErrorsFromApi', () => {
	it('traduz cada tipo de erro do FastAPI para a mensagem do campo', () => {
		const errors = signupErrorsFromApi([
			{ loc: ['body', 'username'], type: 'string_pattern_mismatch', msg: '' },
			{ loc: ['body', 'email'], type: 'value_error', msg: '' },
			{ loc: ['body', 'password'], type: 'string_too_short', msg: '' }
		]);

		expect(errors).toEqual({
			username: MESSAGES.username.invalid,
			email: MESSAGES.email.invalid,
			password: MESSAGES.password.too_short
		});
	});

	it('reconhece o limite de 72 bytes da senha', () => {
		const errors = signupErrorsFromApi([
			{
				loc: ['body', 'password'],
				type: 'value_error',
				msg: 'Value error, A senha deve ter no máximo 72 bytes.'
			}
		]);

		expect(errors).toEqual({ password: MESSAGES.password.too_long });
	});

	it('traduz os erros da política de senha', () => {
		expect(
			signupErrorsFromApi([{ loc: ['body', 'password'], type: 'password_common', msg: '' }])
		).toEqual({ password: MESSAGES.password.common });
		expect(
			signupErrorsFromApi([{ loc: ['body', 'password'], type: 'password_personal', msg: '' }])
		).toEqual({ password: MESSAGES.password.personal });
	});

	it('trata campo ausente', () => {
		expect(signupErrorsFromApi([{ loc: ['body', 'email'], type: 'missing', msg: '' }])).toEqual({
			email: MESSAGES.email.missing
		});
	});

	it('usa a mensagem genérica do campo para tipos desconhecidos', () => {
		expect(
			signupErrorsFromApi([{ loc: ['body', 'username'], type: 'novo_tipo', msg: '' }])
		).toEqual({ username: MESSAGES.username.invalid });
	});

	it('mantém o primeiro erro de cada campo', () => {
		expect(
			signupErrorsFromApi([
				{ loc: ['body', 'username'], type: 'string_too_short', msg: '' },
				{ loc: ['body', 'username'], type: 'string_pattern_mismatch', msg: '' }
			])
		).toEqual({ username: MESSAGES.username.too_short });
	});

	it('ignora erros fora do corpo ou de campos desconhecidos', () => {
		expect(
			signupErrorsFromApi([
				{ loc: ['query', 'username'], type: 'missing', msg: '' },
				{ loc: ['body', 'apelido'], type: 'missing', msg: '' },
				{ loc: ['body'], type: 'missing', msg: '' }
			])
		).toEqual({});
	});
});
