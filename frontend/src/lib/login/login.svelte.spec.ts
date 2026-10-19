// Roda no navegador (projeto "client"): o cliente da API usa a URL relativa
// /api, que só resolve com uma página aberta
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { MESSAGES } from '#lib/signup/validation.ts';

import { LOGIN_MESSAGES, submitLogin, validateLogin } from './login.ts';

const USER = {
	uid: '00000000-0000-0000-0000-000000000001',
	username: 'joao',
	email: 'joao@example.com',
	created_at: '2026-10-19T12:00:00Z'
};

const fetchMock = vi.fn<typeof fetch>();

const respondWith = (status: number, body?: unknown) =>
	fetchMock.mockResolvedValueOnce(
		new Response(body === undefined ? null : JSON.stringify(body), {
			status,
			headers: { 'Content-Type': 'application/json' }
		})
	);

beforeEach(() => {
	fetchMock.mockReset();
	vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('validateLogin', () => {
	it('aceita e-mail e senha preenchidos', () => {
		expect(validateLogin({ email: 'joao@example.com', password: 'x' })).toEqual({});
	});

	it('aponta campos vazios e e-mail inválido', () => {
		expect(validateLogin({ email: '', password: '' })).toEqual({
			email: MESSAGES.email.missing,
			password: LOGIN_MESSAGES.passwordMissing
		});
		expect(validateLogin({ email: 'joao', password: 'x' })).toEqual({
			email: MESSAGES.email.invalid
		});
	});

	it('não aplica as regras de senha nova', () => {
		expect(validateLogin({ email: 'joao@example.com', password: '123' })).toEqual({});
	});
});

describe('submitLogin', () => {
	it('envia as credenciais e devolve o usuário', async () => {
		respondWith(200, USER);

		const result = await submitLogin({ email: ' joao@example.com ', password: ' senha ' });

		expect(result).toEqual({ kind: 'authenticated', user: USER });
		const request = fetchMock.mock.calls[0][0] as Request;
		expect(request.method).toBe('POST');
		expect(new URL(request.url).pathname).toBe('/api/auth/login');
		// O e-mail perde os espaços; a senha é enviada como foi digitada
		expect(await request.json()).toEqual({ email: 'joao@example.com', password: ' senha ' });
	});

	it.each([
		[401, 'invalid_credentials'],
		[422, 'invalid_credentials'],
		[429, 'rate_limited'],
		[500, 'unexpected']
	])('traduz a resposta %i', async (status, kind) => {
		respondWith(status, { detail: 'erro' });

		expect(await submitLogin({ email: 'joao@example.com', password: 'x' })).toEqual({ kind });
	});

	it('avisa quando não há conexão', async () => {
		fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));

		expect(await submitLogin({ email: 'joao@example.com', password: 'x' })).toEqual({
			kind: 'network_error'
		});
	});
});
