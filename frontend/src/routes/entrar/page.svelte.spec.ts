import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { loadSession, session } from '#lib/session.svelte.ts';

import Page from './+page.svelte';

const { goto } = vi.hoisted(() => ({ goto: vi.fn() }));
vi.mock('$app/navigation', () => ({ goto }));

const USER = {
	uid: '00000000-0000-0000-0000-000000000001',
	username: 'joao',
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

async function fillForm(password = 'senha-segura') {
	await page.getByLabelText('E-mail').fill('joao@example.com');
	await page.getByLabelText('Senha', { exact: true }).fill(password);
}

const submit = () => page.getByRole('button', { name: 'Entrar' }).click();

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
	await render(Page);
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('login', () => {
	it('pede e-mail e senha sem chamar a API', async () => {
		await submit();

		await expect.element(page.getByText('Informe seu e-mail.')).toBeVisible();
		await expect.element(page.getByText('Informe sua senha.')).toBeVisible();
		await expect.element(page.getByLabelText('E-mail')).toHaveFocus();
		expect(fetchMock).not.toHaveBeenCalled();
	});

	it('entra, guarda o usuário na sessão e vai para a conta', async () => {
		respondWith(200, USER);

		await fillForm();
		await submit();

		await vi.waitFor(() => expect(goto).toHaveBeenCalledWith('/conta'));
		expect(session.current).toEqual({ status: 'authenticated', user: USER });
		const request = fetchMock.mock.calls[0][0] as Request;
		expect(new URL(request.url).pathname).toBe('/api/auth/login');
	});

	it('explica credenciais erradas, limpa a senha e mantém o e-mail', async () => {
		respondWith(401, { detail: 'E-mail ou senha incorretos.' });

		await fillForm('senha-errada');
		await submit();

		await expect
			.element(page.getByRole('alert'))
			.toHaveTextContent('E-mail ou senha incorretos. Confira e tente de novo.');
		await expect.element(page.getByLabelText('Senha', { exact: true })).toHaveValue('');
		await expect.element(page.getByLabelText('E-mail')).toHaveValue('joao@example.com');
		expect(goto).not.toHaveBeenCalled();
	});

	it.each([
		[429, 'Muitas tentativas seguidas. Aguarde um minuto e tente de novo.'],
		[500, 'Não foi possível entrar agora. Tente de novo em instantes.']
	])('explica a resposta %i', async (status, message) => {
		respondWith(status, { detail: 'erro' });

		await fillForm();
		await submit();

		await expect.element(page.getByRole('alert')).toHaveTextContent(message);
		await expect.element(page.getByRole('alert')).toHaveFocus();
	});

	it('desabilita o botão enquanto envia', async () => {
		let release!: (response: Response) => void;
		fetchMock.mockReturnValueOnce(new Promise((resolve) => (release = resolve)));

		await fillForm();
		await submit();

		await expect.element(page.getByRole('button', { name: 'Entrando…' })).toBeDisabled();
		release(new Response(null, { status: 500 }));
		await expect.element(page.getByRole('button', { name: 'Entrar' })).toBeEnabled();
	});

	it('usa o preenchimento automático de senha salva', async () => {
		await expect
			.element(page.getByLabelText('Senha', { exact: true }))
			.toHaveAttribute('autocomplete', 'current-password');
	});

	it('leva para o cadastro', async () => {
		await expect
			.element(page.getByRole('link', { name: 'Criar conta' }))
			.toHaveAttribute('href', '/cadastro');
	});
});
