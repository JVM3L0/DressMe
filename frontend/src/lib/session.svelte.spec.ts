import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { loadSession, session, signIn, signOut } from './session.svelte.ts';

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

describe('sessão', () => {
	it('fica autenticada quando a API reconhece o cookie', async () => {
		respondWith(200, USER);

		expect(await loadSession()).toEqual({ status: 'authenticated', user: USER });
		expect(session.current).toEqual({ status: 'authenticated', user: USER });
		const request = fetchMock.mock.calls[0][0] as Request;
		expect(new URL(request.url).pathname).toBe('/api/users/me');
	});

	it.each([[401], [500]])('fica anônima com a resposta %i', async (status) => {
		respondWith(status, { detail: 'erro' });

		expect(await loadSession()).toEqual({ status: 'anonymous' });
	});

	it('fica anônima sem conexão com a API', async () => {
		fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));

		expect(await loadSession()).toEqual({ status: 'anonymous' });
	});

	it('entra com o usuário devolvido pelo login', () => {
		signIn(USER);

		expect(session.current).toEqual({ status: 'authenticated', user: USER });
	});

	it('sai quando a API confirma', async () => {
		signIn(USER);
		respondWith(204);

		expect(await signOut()).toBe(true);
		expect(session.current).toEqual({ status: 'anonymous' });
		expect((fetchMock.mock.calls[0][0] as Request).method).toBe('POST');
	});

	it('continua autenticada se a API não confirmar a saída', async () => {
		signIn(USER);
		fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));

		expect(await signOut()).toBe(false);
		expect(session.current.status).toBe('authenticated');
	});
});
