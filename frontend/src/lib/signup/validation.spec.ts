import { describe, expect, it } from 'vitest';

import { MESSAGES, validateField, validateSignup } from './validation.ts';

const VALID = { username: 'Joao.Silva_1', email: 'joao@example.com', password: 'senha-segura' };

describe('validateSignup', () => {
	it('aceita um cadastro válido', () => {
		expect(validateSignup(VALID)).toEqual({});
	});

	it('aponta todos os campos vazios', () => {
		expect(validateSignup({ username: '', email: '', password: '' })).toEqual({
			username: MESSAGES.username.missing,
			email: MESSAGES.email.missing,
			password: MESSAGES.password.missing
		});
	});
});

describe('username', () => {
	it.each([
		['  ', MESSAGES.username.missing],
		['ab', MESSAGES.username.too_short],
		['  ab  ', MESSAGES.username.too_short],
		['a'.repeat(256), MESSAGES.username.too_long],
		['joao silva', MESSAGES.username.invalid],
		['joão', MESSAGES.username.invalid],
		['joao@x', MESSAGES.username.invalid]
	])('recusa %j', (value, message) => {
		expect(validateField('username', value)).toBe(message);
	});

	it.each(['joa', 'Joao.Silva', 'joao_silva-1', ' joao '])('aceita %j', (value) => {
		expect(validateField('username', value)).toBeUndefined();
	});
});

describe('email', () => {
	it.each(['joao', 'joao@', '@example.com', 'joao@example', 'jo ao@example.com'])(
		'recusa %j',
		(value) => {
			expect(validateField('email', value)).toBe(MESSAGES.email.invalid);
		}
	);

	it('recusa e-mail maior que a coluna do banco', () => {
		expect(validateField('email', `${'a'.repeat(250)}@example.com`)).toBe(MESSAGES.email.too_long);
	});

	it('aceita e-mail com espaços nas pontas', () => {
		expect(validateField('email', ' joao@example.com ')).toBeUndefined();
	});
});

describe('password', () => {
	it('recusa menos de 8 caracteres', () => {
		expect(validateField('password', '1234567')).toBe(MESSAGES.password.too_short);
	});

	it('aceita exatamente 72 bytes', () => {
		expect(validateField('password', 'a'.repeat(72))).toBeUndefined();
	});

	it('mede o limite em bytes, não em caracteres', () => {
		// 37 caracteres, 74 bytes em UTF-8
		expect(validateField('password', 'é'.repeat(37))).toBe(MESSAGES.password.too_long);
	});

	it.each([
		['Joao.Silva-2026', { username: 'joao.silva' }],
		['meu-JOAO-favorito', { username: 'Joao' }],
		['mariana@casa!', { email: 'Mariana@example.com' }]
	])('recusa %j por conter username ou e-mail', (value, values) => {
		expect(validateField('password', value, values)).toBe(MESSAGES.password.personal);
	});

	it('ignora trechos pessoais curtos, como o backend', () => {
		expect(validateField('password', 'banana-split-azul', { username: 'ana' })).toBeUndefined();
	});

	it('aplica a regra de dados pessoais no formulário inteiro', () => {
		expect(validateSignup({ ...VALID, password: 'Joao.Silva_1!' })).toEqual({
			password: MESSAGES.password.personal
		});
	});

	it('não remove espaços da senha', () => {
		expect(validateField('password', '        ')).toBeUndefined();
	});
});
