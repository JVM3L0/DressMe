import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import Page from './+page.svelte';

const fetchMock = vi.fn<typeof fetch>();

function respondWith(status: number, body?: unknown) {
	fetchMock.mockResolvedValueOnce(
		new Response(body === undefined ? null : JSON.stringify(body), {
			status,
			headers: { 'Content-Type': 'application/json' }
		})
	);
}

async function fillValidForm() {
	await page.getByLabelText('Nome de usuário').fill('Joao.Silva');
	await page.getByLabelText('E-mail').fill('Joao@Example.com');
	await page.getByLabelText('Senha', { exact: true }).fill('senha-segura');
}

const submit = () => page.getByRole('button', { name: 'Criar conta' }).click();

beforeEach(async () => {
	fetchMock.mockReset();
	vi.stubGlobal('fetch', fetchMock);
	await render(Page);
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('cadastro', () => {
	it('valida no navegador sem chamar a API e foca o primeiro campo com erro', async () => {
		await submit();

		await expect.element(page.getByText('Informe um nome de usuário.')).toBeVisible();
		await expect.element(page.getByText('Informe seu e-mail.')).toBeVisible();
		await expect.element(page.getByText('Crie uma senha.')).toBeVisible();
		await expect.element(page.getByLabelText('Nome de usuário')).toHaveFocus();
		expect(fetchMock).not.toHaveBeenCalled();
	});

	it('valida o campo ao sair dele, e não enquanto a pessoa digita', async () => {
		const username = page.getByLabelText('Nome de usuário');

		await username.fill('ab');
		await expect.element(page.getByText('Use pelo menos 3 caracteres.')).not.toBeInTheDocument();

		await page.getByLabelText('E-mail').click();
		await expect.element(page.getByText('Use pelo menos 3 caracteres.')).toBeVisible();

		await username.fill('abc');
		await expect.element(page.getByText('Use pelo menos 3 caracteres.')).not.toBeInTheDocument();
	});

	it('envia os dados para a API e mostra a confirmação', async () => {
		respondWith(201, {
			uid: '00000000-0000-0000-0000-000000000001',
			username: 'Joao.Silva',
			email: 'joao@example.com',
			created_at: '2026-10-19T12:00:00Z'
		});

		await fillValidForm();
		await submit();

		const heading = page.getByRole('heading', { name: 'Conta criada' });
		await expect.element(heading).toBeVisible();
		await expect.element(heading).toHaveFocus();
		await expect.element(page.getByText(/Tudo pronto, Joao\.Silva/)).toBeVisible();

		const request = fetchMock.mock.calls[0][0] as Request;
		expect(request.method).toBe('POST');
		expect(new URL(request.url).pathname).toBe('/api/users/');
		expect(await request.json()).toEqual({
			username: 'Joao.Silva',
			email: 'Joao@Example.com',
			password: 'senha-segura'
		});
	});

	it('mostra os erros de validação devolvidos pela API em cada campo', async () => {
		respondWith(422, {
			detail: [{ loc: ['body', 'email'], type: 'value_error', msg: 'invalid' }]
		});

		await fillValidForm();
		await submit();

		await expect
			.element(page.getByText('Informe um e-mail válido, como nome@exemplo.com.'))
			.toBeVisible();
		await expect.element(page.getByLabelText('E-mail')).toHaveFocus();
	});

	it.each([
		[409, 'Já existe uma conta com esse e-mail ou nome de usuário. Use outro.'],
		[429, 'Muitas tentativas seguidas. Aguarde um minuto e tente de novo.'],
		[500, 'Não foi possível criar a conta agora. Tente de novo em instantes.']
	])('explica a resposta %i e mantém os dados do formulário', async (status, message) => {
		respondWith(status, { detail: 'erro' });

		await fillValidForm();
		await submit();

		await expect.element(page.getByRole('alert')).toHaveTextContent(message);
		await expect.element(page.getByLabelText('Nome de usuário')).toHaveValue('Joao.Silva');
	});

	it('avisa quando não consegue falar com o servidor', async () => {
		fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));

		await fillValidForm();
		await submit();

		await expect
			.element(page.getByRole('alert'))
			.toHaveTextContent('Não foi possível falar com o servidor.');
	});

	it('desabilita o botão enquanto envia, evitando cadastro duplicado', async () => {
		let release!: (response: Response) => void;
		fetchMock.mockReturnValueOnce(new Promise((resolve) => (release = resolve)));

		await fillValidForm();
		await submit();

		const button = page.getByRole('button', { name: 'Criando conta…' });
		await expect.element(button).toBeDisabled();
		await expect.element(button).toHaveAttribute('aria-busy', 'true');

		release(new Response(null, { status: 500 }));
		await expect.element(page.getByRole('button', { name: 'Criar conta' })).toBeEnabled();
	});

	it('mostra e oculta a senha', async () => {
		const password = page.getByLabelText('Senha', { exact: true });
		const toggle = page.getByRole('button', { name: 'Mostrar senha' });

		await expect.element(password).toHaveAttribute('type', 'password');
		await toggle.click();
		await expect.element(password).toHaveAttribute('type', 'text');
		await expect
			.element(page.getByRole('button', { name: 'Ocultar senha' }))
			.toHaveAttribute('aria-pressed', 'true');
	});
});
