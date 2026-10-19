import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { loadSession, session, signIn } from '#lib/session.svelte.ts';

import Page from './+page.svelte';

const { goto } = vi.hoisted(() => ({ goto: vi.fn() }));
vi.mock('$app/navigation', () => ({ goto }));

const USER = {
	uid: '00000000-0000-0000-0000-000000000001',
	username: 'Joao.Silva',
	email: 'joao@example.com',
	created_at: '2026-10-19T12:00:00Z'
};

const fetchMock = vi.fn<typeof fetch>();

function respondWith(status: number, body?: unknown) {
	fetchMock.mockResolvedValueOnce(
		new Response(body === undefined ? null : JSON.stringify(body), {
			status,
			headers: { 'Content-Type': 'application/json' }
		})
	);
}

/** A sessão é um estado do módulo, compartilhado entre os testes */
async function signOutForTest() {
	respondWith(401, { detail: 'Faça login para continuar.' });
	await loadSession();
	fetchMock.mockClear();
}

beforeEach(async () => {
	fetchMock.mockReset();
	goto.mockReset();
	vi.stubGlobal('fetch', fetchMock);
	await signOutForTest();
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('conta', () => {
	it('mostra os dados de quem está logado', async () => {
		signIn(USER);
		await render(Page);

		await expect.element(page.getByRole('heading', { name: 'Joao.Silva' })).toBeVisible();
		await expect.element(page.getByText('joao@example.com')).toBeVisible();
		await expect.element(page.getByText('outubro de 2026')).toBeVisible();
	});

	it('manda para o login quem não tem sessão, sem ficar no histórico', async () => {
		await render(Page);

		await vi.waitFor(() => expect(goto).toHaveBeenCalledWith('/entrar', { replaceState: true }));
	});

	it('sai da conta e volta para o início', async () => {
		signIn(USER);
		await render(Page);
		respondWith(204);

		await page.getByRole('button', { name: 'Sair' }).click();

		await vi.waitFor(() => expect(goto).toHaveBeenCalledWith('/'));
		const request = fetchMock.mock.calls[0][0] as Request;
		expect(new URL(request.url).pathname).toBe('/api/auth/logout');
	});

	it('avisa quando não consegue sair, e continua na conta', async () => {
		signIn(USER);
		await render(Page);
		fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));

		await page.getByRole('button', { name: 'Sair' }).click();

		await expect.element(page.getByRole('alert')).toHaveTextContent('Não foi possível sair agora.');
		expect(session.current.status).toBe('authenticated');
		expect(goto).not.toHaveBeenCalled();
	});
});
