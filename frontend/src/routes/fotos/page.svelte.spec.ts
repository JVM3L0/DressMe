import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page, userEvent } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { signIn } from '#lib/session.svelte.ts';
import { USER, imageFile, json, mockApi } from '#lib/testing/api-mock.ts';

import Page from './+page.svelte';

const { goto } = vi.hoisted(() => ({ goto: vi.fn() }));
vi.mock('$app/navigation', () => ({ goto }));

const PHOTO = {
	uid: '11111111-1111-1111-1111-111111111111',
	width: 400,
	height: 600,
	created_at: '2026-10-19T12:00:00Z'
};
const NEW_PHOTO = { ...PHOTO, uid: '22222222-2222-2222-2222-222222222222' };

const picker = () => page.getByLabelText(/Nova foto/);
/** Há mais de uma região de alerta na página: escolhe a que tem o texto */
const alert = (text: string) => page.getByRole('alert').filter({ hasText: text });
const send = () => page.getByRole('button', { name: 'Enviar foto' });

beforeEach(() => {
	goto.mockReset();
	signIn(USER);
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('fotos: lista', () => {
	it('mostra uma orientação quando ainda não há fotos', async () => {
		mockApi({ 'GET /api/photos/': () => json(200, []) });
		await render(Page);

		await expect.element(page.getByText(/ainda não enviou nenhuma foto/)).toBeVisible();
	});

	it('lista as fotos, buscando cada imagem pela API', async () => {
		mockApi({ 'GET /api/photos/': () => json(200, [PHOTO]) });
		await render(Page);

		const image = page.getByAltText('Foto enviada em 19 de out. de 2026');
		await expect.element(image).toHaveAttribute('src', `/api/photos/${PHOTO.uid}/image`);
		await expect.element(image).toHaveAttribute('width', '400');
		await expect.element(page.getByText('400 × 600')).toBeVisible();
	});

	it('oferece tentar de novo quando a lista não carrega', async () => {
		let attempts = 0;
		mockApi({ 'GET /api/photos/': () => (++attempts === 1 ? json(500, {}) : json(200, [PHOTO])) });
		await render(Page);

		await expect.element(alert('Tente de novo em instantes')).toBeVisible();
		await page.getByRole('button', { name: 'Tentar de novo' }).click();

		await expect.element(page.getByAltText(/Foto enviada em/)).toBeVisible();
	});

	it('manda para o login quando a sessão venceu', async () => {
		mockApi({
			'GET /api/photos/': () => json(401, { detail: 'Faça login para continuar.' }),
			'GET /api/users/me': () => json(401, { detail: 'Faça login para continuar.' })
		});
		await render(Page);

		await vi.waitFor(() => expect(goto).toHaveBeenCalledWith('/entrar', { replaceState: true }));
	});
});

describe('fotos: envio', () => {
	it('pede uma imagem antes de enviar, sem chamar a API', async () => {
		const api = mockApi({ 'GET /api/photos/': () => json(200, []) });
		await render(Page);

		await send().click();

		await expect.element(page.getByText('Escolha uma imagem.')).toBeVisible();
		expect(api.to('POST /api/photos/')).toHaveLength(0);
	});

	it.each([
		[imageFile('foto.gif', 'image/gif'), 'Envie uma imagem JPEG ou PNG.'],
		[imageFile('grande.jpg', 'image/jpeg', 10 * 1024 * 1024 + 1), 'A imagem passa de 10 MB.']
	])('recusa %o no navegador', async (file, message) => {
		const api = mockApi({ 'GET /api/photos/': () => json(200, []) });
		await render(Page);

		await userEvent.upload(picker(), file);
		await send().click();

		await expect.element(page.getByText(message, { exact: false })).toBeVisible();
		expect(api.to('POST /api/photos/')).toHaveLength(0);
	});

	it('envia o arquivo, mostra a foto nova primeiro e limpa o formulário', async () => {
		const api = mockApi({
			'GET /api/photos/': () => json(200, [PHOTO]),
			'POST /api/photos/': () => json(201, NEW_PHOTO)
		});
		await render(Page);
		await expect.element(page.getByAltText(/Foto enviada em/)).toBeVisible();

		await userEvent.upload(picker(), imageFile('eu.jpg'));
		await send().click();

		await expect.element(page.getByText('Foto enviada.')).toBeVisible();
		const [request] = api.to('POST /api/photos/');
		const sent = (await request.formData()).get('file') as File;
		expect(sent.name).toBe('eu.jpg');
		expect(request.headers.get('content-type')).toMatch(/^multipart\/form-data; boundary=/);
		const images = page.getByRole('img', { name: /Foto enviada em/ }).elements();
		expect(images.map((image) => image.getAttribute('src'))).toEqual([
			`/api/photos/${NEW_PHOTO.uid}/image`,
			`/api/photos/${PHOTO.uid}/image`
		]);
		await expect.element(page.getByText('Escolher imagem')).toBeVisible();
	});

	it('desabilita o botão enquanto envia, evitando envio duplicado', async () => {
		let release!: (response: Response) => void;
		mockApi({
			'GET /api/photos/': () => json(200, []),
			'POST /api/photos/': () => new Promise((resolve) => (release = resolve))
		});
		await render(Page);
		await userEvent.upload(picker(), imageFile());

		await send().click();

		const button = page.getByRole('button', { name: 'Enviando…' });
		await expect.element(button).toBeDisabled();
		await expect.element(button).toHaveAttribute('aria-busy', 'true');
		release(json(201, NEW_PHOTO));
		await expect.element(page.getByText('Foto enviada.')).toBeVisible();
	});

	it.each([
		[413, 'A imagem passa de 10 MB.'],
		[415, 'Envie uma imagem JPEG ou PNG.'],
		[429, 'Muitos envios seguidos.'],
		[500, 'Tente de novo em instantes.']
	])('explica a resposta %i e mantém o arquivo escolhido', async (status, message) => {
		mockApi({
			'GET /api/photos/': () => json(200, []),
			'POST /api/photos/': () => json(status, { detail: 'erro' })
		});
		await render(Page);
		await userEvent.upload(picker(), imageFile('eu.jpg'));

		await send().click();

		await expect.element(alert(message)).toBeVisible();
		await expect.element(alert(message)).toHaveFocus();
		await expect.element(page.getByText('eu.jpg')).toBeVisible();
	});

	it('avisa quando não há conexão', async () => {
		mockApi({
			'GET /api/photos/': () => json(200, []),
			'POST /api/photos/': () => {
				throw new TypeError('Failed to fetch');
			}
		});
		await render(Page);
		await userEvent.upload(picker(), imageFile());

		await send().click();

		await expect.element(alert('Verifique sua conexão')).toBeVisible();
	});
});

describe('fotos: exclusão', () => {
	const open = async (extra: Parameters<typeof mockApi>[0] = {}) => {
		const api = mockApi({ 'GET /api/photos/': () => json(200, [PHOTO]), ...extra });
		await render(Page);
		await page.getByRole('button', { name: 'Excluir foto' }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		return api;
	};

	it('exclui depois da confirmação e tira a foto da lista', async () => {
		const api = await open({ [`DELETE /api/photos/${PHOTO.uid}`]: () => json(204) });

		await expect.element(page.getByText('Foto excluída.')).toBeVisible();
		await expect.element(page.getByAltText(/Foto enviada em/)).not.toBeInTheDocument();
		await expect.element(page.getByText(/ainda não enviou nenhuma foto/)).toBeVisible();
		expect(api.to(`DELETE /api/photos/${PHOTO.uid}`)).toHaveLength(1);
	});

	it('trata "já não existe" como excluída', async () => {
		await open({ [`DELETE /api/photos/${PHOTO.uid}`]: () => json(404, {}) });

		await expect.element(page.getByText('Foto excluída.')).toBeVisible();
		await expect.element(page.getByAltText(/Foto enviada em/)).not.toBeInTheDocument();
	});

	it('mantém a foto e avisa quando a exclusão falha', async () => {
		await open({ [`DELETE /api/photos/${PHOTO.uid}`]: () => json(500, {}) });

		await expect.element(alert('Tente de novo em instantes')).toBeVisible();
		await expect.element(page.getByAltText(/Foto enviada em/)).toBeVisible();
	});
});
