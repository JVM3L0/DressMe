import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page, userEvent } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { signIn } from '#lib/session.svelte.ts';
import { USER, imageFile, json, mockApi } from '#lib/testing/api-mock.ts';

import Page from './+page.svelte';

const { goto } = vi.hoisted(() => ({ goto: vi.fn() }));
vi.mock('$app/navigation', () => ({ goto }));

const garment = (n: number, category: string, name: string | null = null) => ({
	uid: `00000000-0000-0000-0000-00000000000${n}`,
	category,
	name,
	width: 400,
	height: 500,
	created_at: '2026-10-19T12:00:00Z'
});

const SHIRT = garment(1, 'top', 'Camisa azul');
const PANTS = garment(2, 'bottom', 'Calça preta');
const SNEAKER = garment(3, 'footwear');

const picker = () => page.getByLabelText(/Foto da peça/);
const category = () => page.getByLabelText('Categoria', { exact: true });
const add = () => page.getByRole('button', { name: 'Adicionar peça' });
const alert = (text: string) => page.getByRole('alert').filter({ hasText: text });

beforeEach(() => {
	goto.mockReset();
	signIn(USER);
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('guarda-roupa: lista', () => {
	it('mostra uma orientação quando está vazio, sem o filtro', async () => {
		mockApi({ 'GET /api/garments/': () => json(200, []) });
		await render(Page);

		await expect.element(page.getByText(/guarda-roupa está vazio/)).toBeVisible();
		await expect
			.element(page.getByRole('group', { name: 'Filtrar por categoria' }))
			.not.toBeInTheDocument();
	});

	it('lista as peças com nome e categoria, e usa a categoria quando não há nome', async () => {
		mockApi({ 'GET /api/garments/': () => json(200, [SHIRT, SNEAKER]) });
		await render(Page);

		const image = page.getByAltText('Camisa azul');
		await expect.element(image).toHaveAttribute('src', `/api/garments/${SHIRT.uid}/image`);
		await expect.element(page.getByText('Parte de cima', { exact: true }).last()).toBeVisible();
		await expect.element(page.getByAltText('Calçado')).toBeVisible();
	});

	it('filtra por categoria, com a contagem de cada uma', async () => {
		mockApi({ 'GET /api/garments/': () => json(200, [SHIRT, PANTS, SNEAKER]) });
		await render(Page);
		await expect.element(page.getByRole('button', { name: 'Tudo 3' })).toBeVisible();

		await page.getByRole('button', { name: 'Parte de baixo 1' }).click();

		await expect.element(page.getByAltText('Calça preta')).toBeVisible();
		await expect.element(page.getByAltText('Camisa azul')).not.toBeInTheDocument();

		await page.getByRole('button', { name: 'Agasalho 0' }).click();
		await expect.element(page.getByText('Nenhuma peça nessa categoria ainda.')).toBeVisible();

		await page.getByRole('button', { name: 'Tudo 3' }).click();
		await expect.element(page.getByAltText('Camisa azul')).toBeVisible();
	});

	it('manda para o login quando a sessão venceu', async () => {
		mockApi({
			'GET /api/garments/': () => json(401, { detail: 'Faça login para continuar.' }),
			'GET /api/users/me': () => json(401, { detail: 'Faça login para continuar.' })
		});
		await render(Page);

		await vi.waitFor(() => expect(goto).toHaveBeenCalledWith('/entrar', { replaceState: true }));
	});
});

describe('guarda-roupa: adicionar peça', () => {
	it('exige imagem e categoria, e foca o primeiro campo com erro', async () => {
		const api = mockApi({ 'GET /api/garments/': () => json(200, []) });
		await render(Page);

		await add().click();

		await expect.element(page.getByText('Escolha uma imagem.')).toBeVisible();
		await expect.element(page.getByText('Escolha a categoria da peça.')).toBeVisible();
		await expect.element(picker()).toHaveFocus();
		expect(api.to('POST /api/garments/')).toHaveLength(0);
	});

	it('com a imagem escolhida, o erro seguinte é a categoria', async () => {
		mockApi({ 'GET /api/garments/': () => json(200, []) });
		await render(Page);
		await userEvent.upload(picker(), imageFile('camisa.png', 'image/png'));

		await add().click();

		await expect.element(page.getByText('Escolha a categoria da peça.')).toBeVisible();
		await expect.element(category()).toHaveFocus();
	});

	it('dá exemplos da categoria escolhida', async () => {
		mockApi({ 'GET /api/garments/': () => json(200, []) });
		await render(Page);
		await expect.element(page.getByText('Onde a peça é vestida.')).toBeVisible();

		await category().selectOptions('outerwear');

		await expect
			.element(page.getByText('Por exemplo: jaqueta, casaco, blazer, cardigã.'))
			.toBeVisible();
	});

	it('envia imagem, categoria e nome, e mostra a peça nova', async () => {
		const api = mockApi({
			'GET /api/garments/': () => json(200, [PANTS]),
			'POST /api/garments/': () => json(201, SHIRT)
		});
		await render(Page);
		await expect.element(page.getByAltText('Calça preta')).toBeVisible();

		await userEvent.upload(picker(), imageFile('camisa.png', 'image/png'));
		await category().selectOptions('top');
		await page.getByLabelText('Nome (opcional)').fill('  Camisa azul ');
		await add().click();

		await expect.element(page.getByText('Peça adicionada.')).toBeVisible();
		const [request] = api.to('POST /api/garments/');
		const form = await request.formData();
		expect((form.get('file') as File).name).toBe('camisa.png');
		expect(form.get('category')).toBe('top');
		expect(form.get('name')).toBe('Camisa azul');
		await expect.element(page.getByAltText('Camisa azul')).toBeVisible();
	});

	it('não envia o nome quando ele está em branco', async () => {
		const api = mockApi({
			'GET /api/garments/': () => json(200, []),
			'POST /api/garments/': () => json(201, SNEAKER)
		});
		await render(Page);
		await userEvent.upload(picker(), imageFile());
		await category().selectOptions('footwear');
		await page.getByLabelText('Nome (opcional)').fill('   ');

		await add().click();

		await expect.element(page.getByText('Peça adicionada.')).toBeVisible();
		expect((await api.to('POST /api/garments/')[0].formData()).has('name')).toBe(false);
	});

	it('limpa a imagem e o nome depois de enviar, mas mantém a categoria', async () => {
		mockApi({
			'GET /api/garments/': () => json(200, []),
			'POST /api/garments/': () => json(201, SHIRT)
		});
		await render(Page);
		await userEvent.upload(picker(), imageFile('camisa.png', 'image/png'));
		await category().selectOptions('top');
		await page.getByLabelText('Nome (opcional)').fill('Camisa azul');

		await add().click();

		await expect.element(page.getByText('Escolher imagem')).toBeVisible();
		await expect.element(page.getByLabelText('Nome (opcional)')).toHaveValue('');
		await expect.element(category()).toHaveValue('top');
	});

	it.each([
		[413, 'A imagem passa de 10 MB.'],
		[415, 'Envie uma imagem JPEG ou PNG.'],
		[429, 'Muitos envios seguidos.'],
		[500, 'Tente de novo em instantes.']
	])('explica a resposta %i e mantém os dados', async (status, message) => {
		mockApi({
			'GET /api/garments/': () => json(200, []),
			'POST /api/garments/': () => json(status, { detail: 'erro' })
		});
		await render(Page);
		await userEvent.upload(picker(), imageFile('camisa.png', 'image/png'));
		await category().selectOptions('top');

		await add().click();

		await expect.element(alert(message)).toBeVisible();
		await expect.element(category()).toHaveValue('top');
		await expect.element(page.getByText('camisa.png')).toBeVisible();
	});
});

describe('guarda-roupa: exclusão', () => {
	const remove = async (name: string, extra: Parameters<typeof mockApi>[0]) => {
		const api = mockApi({ 'GET /api/garments/': () => json(200, [SHIRT, PANTS]), ...extra });
		await render(Page);
		await page.getByRole('button', { name: `Excluir ${name}` }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		return api;
	};

	it('exclui só a peça escolhida, depois da confirmação', async () => {
		const api = await remove('Camisa azul', {
			[`DELETE /api/garments/${SHIRT.uid}`]: () => json(204)
		});

		await expect.element(page.getByText('Peça excluída.')).toBeVisible();
		await expect.element(page.getByAltText('Camisa azul')).not.toBeInTheDocument();
		await expect.element(page.getByAltText('Calça preta')).toBeVisible();
		expect(api.to(`DELETE /api/garments/${SHIRT.uid}`)).toHaveLength(1);
		expect(api.to(`DELETE /api/garments/${PANTS.uid}`)).toHaveLength(0);
	});

	it('atualiza a contagem do filtro', async () => {
		await remove('Camisa azul', { [`DELETE /api/garments/${SHIRT.uid}`]: () => json(204) });

		await expect.element(page.getByRole('button', { name: 'Tudo 1' })).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Parte de cima 0' })).toBeVisible();
	});

	it('mantém a peça e avisa quando a exclusão falha', async () => {
		await remove('Camisa azul', { [`DELETE /api/garments/${SHIRT.uid}`]: () => json(500, {}) });

		await expect.element(alert('Tente de novo em instantes')).toBeVisible();
		await expect.element(page.getByAltText('Camisa azul')).toBeVisible();
	});
});
