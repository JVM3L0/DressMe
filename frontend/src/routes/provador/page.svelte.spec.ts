import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { signIn } from '#lib/session.svelte.ts';
import { USER, json, mockApi, type Handler } from '#lib/testing/api-mock.ts';
import type { GarmentCategory } from '#lib/wardrobe/categories.ts';

import Page from './+page.svelte';

const { goto } = vi.hoisted(() => ({ goto: vi.fn() }));
vi.mock('$app/navigation', () => ({ goto }));

const garment = (uid: string, category: GarmentCategory, name: string | null) => ({
	uid,
	category,
	name,
	width: 400,
	height: 500,
	created_at: '2026-10-19T12:00:00Z'
});

const SHIRT = garment('g-shirt', 'top', 'Camisa azul');
const PANTS = garment('g-pants', 'bottom', 'Calça preta');
const DRESS = garment('g-dress', 'one_piece', 'Vestido vermelho');
const SHOES = garment('g-shoes', 'footwear', 'Tênis branco');
const PHOTO = { uid: 'photo-1', width: 600, height: 800, created_at: '2026-10-19T12:00:00Z' };
const OLD_PHOTO = { ...PHOTO, uid: 'photo-0' };

const outfit = (uid: string, name: string, garment_ids: string[]) => ({
	uid,
	name,
	garment_ids,
	created_at: '2026-10-19T12:00:00Z'
});
const FRIDAY = outfit('o-1', 'Look de sexta', ['g-shirt', 'g-pants']);

const alert = (text: string) => page.getByRole('alert').filter({ hasText: text });
const slot = (label: string) => page.getByRole('button', { name: `Escolher ${label}` });
const pick = async (label: string, piece: string) => {
	await slot(label).click();
	await page.getByRole('dialog').getByRole('button', { name: piece }).click();
};
const promptText = () => page.getByLabelText('Texto para colar na IA');

function open(
	routes: Record<string, Handler> = {},
	data: { outfits?: unknown[]; photos?: unknown[] } = {}
) {
	return mockApi({
		'GET /api/garments/': () => json(200, [SHIRT, PANTS, DRESS, SHOES]),
		'GET /api/photos/': () => json(200, data.photos ?? [PHOTO]),
		'GET /api/outfits/': () => json(200, data.outfits ?? []),
		...routes
	});
}

beforeEach(() => {
	goto.mockReset();
	signIn(USER);
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('provador: carregamento', () => {
	it('mostra os 6 encaixes vazios e a foto mais recente', async () => {
		open();
		await render(Page);

		for (const label of [
			'Acessório',
			'Agasalho',
			'Parte de cima',
			'Parte de baixo',
			'Peça única',
			'Calçado'
		]) {
			await expect.element(slot(label)).toBeVisible();
		}
		await expect
			.element(page.getByAltText('Sua foto escolhida'))
			.toHaveAttribute('src', '/api/photos/photo-1/image');
	});

	it('com guarda-roupa vazio, leva ao guarda-roupa', async () => {
		open({ 'GET /api/garments/': () => json(200, []) });
		await render(Page);

		await expect.element(page.getByText(/guarda-roupa está vazio/)).toBeVisible();
		await expect
			.element(page.getByRole('link', { name: 'Ir para o guarda-roupa' }))
			.toHaveAttribute('href', '/guarda-roupa');
	});

	it('sem fotos, convida a enviar uma, e o resto continua funcionando', async () => {
		open({}, { photos: [] });
		await render(Page);

		await expect.element(page.getByText('Você ainda não enviou nenhuma foto.')).toBeVisible();
		await expect
			.element(page.getByRole('link', { name: 'Enviar uma foto' }))
			.toHaveAttribute('href', '/fotos');
		await pick('Parte de cima', 'Camisa azul');
		await expect.element(page.getByRole('button', { name: 'Copiar roupas' })).toBeEnabled();
	});

	it('oferece tentar de novo quando algo não carrega', async () => {
		let attempts = 0;
		open({ 'GET /api/outfits/': () => (++attempts === 1 ? json(500, {}) : json(200, [])) });
		await render(Page);

		await expect.element(alert('Tente de novo em instantes')).toBeVisible();
		await page.getByRole('button', { name: 'Tentar de novo' }).click();

		await expect.element(slot('Parte de cima')).toBeVisible();
	});

	it('manda para o login quando a sessão venceu', async () => {
		open({
			'GET /api/garments/': () => json(401, { detail: 'Faça login para continuar.' }),
			'GET /api/users/me': () => json(401, { detail: 'Faça login para continuar.' })
		});
		await render(Page);

		await vi.waitFor(() => expect(goto).toHaveBeenCalledWith('/entrar', { replaceState: true }));
	});

	it('troca a foto escolhida quando há mais de uma', async () => {
		open({}, { photos: [PHOTO, OLD_PHOTO] });
		await render(Page);

		await page.getByRole('button', { name: 'Foto 2 de 2' }).click();

		await expect
			.element(page.getByAltText('Sua foto escolhida'))
			.toHaveAttribute('src', '/api/photos/photo-0/image');
	});
});

describe('provador: montagem', () => {
	it('escolhe uma peça num encaixe e atualiza o texto', async () => {
		open();
		await render(Page);

		await pick('Parte de cima', 'Camisa azul');

		await expect
			.element(page.getByRole('button', { name: 'Trocar Parte de cima: Camisa azul' }))
			.toBeVisible();
		await expect
			.element(promptText())
			.toHaveValue(expect.stringContaining('1. Top: "Camisa azul"'));
	});

	it('o texto e a imagem seguem a ordem do corpo, não a da escolha', async () => {
		open();
		await render(Page);

		await pick('Calçado', 'Tênis branco');
		await pick('Parte de baixo', 'Calça preta');
		await pick('Parte de cima', 'Camisa azul');

		const text = (promptText().element() as HTMLTextAreaElement).value;
		expect(text.indexOf('1. Top')).toBeGreaterThan(-1);
		expect(text.indexOf('2. Bottom')).toBeGreaterThan(text.indexOf('1. Top'));
		expect(text.indexOf('3. Footwear')).toBeGreaterThan(text.indexOf('2. Bottom'));
	});

	it('tira uma peça do conjunto', async () => {
		open();
		await render(Page);
		await pick('Parte de cima', 'Camisa azul');

		await page.getByRole('button', { name: 'Tirar Camisa azul do conjunto' }).click();

		await expect.element(slot('Parte de cima')).toBeVisible();
		await expect.element(promptText()).toHaveValue('');
	});

	it('a peça única substitui cima e baixo, avisando antes', async () => {
		open();
		await render(Page);
		await pick('Parte de cima', 'Camisa azul');
		await pick('Parte de baixo', 'Calça preta');

		await slot('Peça única').click();
		await expect
			.element(page.getByText('Isso tira Camisa azul e Calça preta do conjunto.'))
			.toBeVisible();
		await page.getByRole('dialog').getByRole('button', { name: 'Vestido vermelho' }).click();

		await expect.element(slot('Parte de cima')).not.toBeInTheDocument();
		await expect.element(slot('Parte de baixo')).not.toBeInTheDocument();
		await expect
			.element(page.getByRole('button', { name: 'Trocar Peça única: Vestido vermelho' }))
			.toBeVisible();
		await expect.element(promptText()).toHaveValue(expect.stringContaining('1. One-piece'));
	});

	it('escolher uma parte de cima de novo tira a peça única', async () => {
		open();
		await render(Page);
		await pick('Peça única', 'Vestido vermelho');

		await page.getByRole('button', { name: 'Tirar Vestido vermelho do conjunto' }).click();
		await pick('Parte de cima', 'Camisa azul');

		await expect.element(slot('Peça única')).toBeVisible();
	});

	it('começar de novo esvazia o conjunto', async () => {
		open();
		await render(Page);
		await pick('Parte de cima', 'Camisa azul');

		await page.getByRole('button', { name: 'Começar de novo' }).click();

		await expect.element(slot('Parte de cima')).toBeVisible();
	});
});

describe('provador: conjuntos salvos', () => {
	it('exige nome e ao menos uma peça antes de salvar', async () => {
		const api = open();
		await render(Page);

		await page.getByRole('button', { name: 'Salvar conjunto' }).click();
		await expect.element(page.getByText('Dê um nome ao conjunto.')).toBeVisible();
		await expect.element(page.getByLabelText('Nome do conjunto')).toHaveFocus();

		await page.getByLabelText('Nome do conjunto').fill('Look de sexta');
		await page.getByRole('button', { name: 'Salvar conjunto' }).click();
		await expect.element(alert('Escolha ao menos uma peça.')).toBeVisible();
		expect(api.to('POST /api/outfits/')).toHaveLength(0);
	});

	it('salva o conjunto com o nome e os ids das peças, na ordem do corpo', async () => {
		const api = open({
			'POST /api/outfits/': () =>
				json(201, outfit('o-new', 'Look de sexta', ['g-shirt', 'g-shoes']))
		});
		await render(Page);
		await pick('Calçado', 'Tênis branco');
		await pick('Parte de cima', 'Camisa azul');

		await page.getByLabelText('Nome do conjunto').fill('  Look de sexta ');
		await page.getByRole('button', { name: 'Salvar conjunto' }).click();

		await expect.element(page.getByText('Conjunto salvo.')).toBeVisible();
		expect(await api.to('POST /api/outfits/')[0].json()).toEqual({
			name: 'Look de sexta',
			garment_ids: ['g-shirt', 'g-shoes']
		});
		await expect
			.element(page.getByRole('heading', { name: 'Conjunto: Look de sexta' }))
			.toBeVisible();
		await expect
			.element(page.getByRole('button', { name: 'Usar o conjunto Look de sexta' }))
			.toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Atualizar conjunto' })).toBeVisible();
	});

	it('usa um conjunto salvo: monta os encaixes e preenche o nome', async () => {
		open({}, { outfits: [FRIDAY] });
		await render(Page);

		await page.getByRole('button', { name: 'Usar o conjunto Look de sexta' }).click();

		await expect.element(page.getByText('Conjunto “Look de sexta” carregado.')).toBeVisible();
		await expect
			.element(page.getByRole('button', { name: 'Trocar Parte de cima: Camisa azul' }))
			.toBeVisible();
		await expect
			.element(page.getByRole('button', { name: 'Trocar Parte de baixo: Calça preta' }))
			.toBeVisible();
		await expect.element(page.getByLabelText('Nome do conjunto')).toHaveValue('Look de sexta');
	});

	it('avisa quando alguma peça do conjunto já não existe', async () => {
		open({}, { outfits: [outfit('o-2', 'Antigo', ['g-shirt', 'g-sumiu', 'g-sumiu-2'])] });
		await render(Page);

		await page.getByRole('button', { name: 'Usar o conjunto Antigo' }).click();

		await expect.element(page.getByText(/2 peças não existem mais/)).toBeVisible();
		await expect
			.element(page.getByRole('button', { name: 'Trocar Parte de cima: Camisa azul' }))
			.toBeVisible();
	});

	it('atualiza o conjunto em uso, ou salva como novo', async () => {
		const api = open(
			{
				'PUT /api/outfits/o-1': () =>
					json(200, outfit('o-1', 'Look novo', ['g-shirt', 'g-pants', 'g-shoes'])),
				'POST /api/outfits/': () =>
					json(201, outfit('o-2', 'Look novo', ['g-shirt', 'g-pants', 'g-shoes']))
			},
			{ outfits: [FRIDAY] }
		);
		await render(Page);
		await page.getByRole('button', { name: 'Usar o conjunto Look de sexta' }).click();
		await pick('Calçado', 'Tênis branco');
		await page.getByLabelText('Nome do conjunto').fill('Look novo');

		await page.getByRole('button', { name: 'Atualizar conjunto' }).click();
		await expect.element(page.getByText('Conjunto atualizado.')).toBeVisible();
		expect(await api.to('PUT /api/outfits/o-1')[0].json()).toEqual({
			name: 'Look novo',
			garment_ids: ['g-shirt', 'g-pants', 'g-shoes']
		});
		expect(api.to('POST /api/outfits/')).toHaveLength(0);

		await page.getByRole('button', { name: 'Salvar como novo' }).click();
		await expect.element(page.getByText('Conjunto salvo.')).toBeVisible();
		expect(api.to('POST /api/outfits/')).toHaveLength(1);
	});

	it('explica quando a API recusa o conjunto (uma peça sumiu)', async () => {
		open({
			'POST /api/outfits/': () =>
				json(422, { detail: 'Alguma das peças não existe mais.', code: 'outfit_unknown_garment' })
		});
		await render(Page);
		await pick('Parte de cima', 'Camisa azul');
		await page.getByLabelText('Nome do conjunto').fill('Look');

		await page.getByRole('button', { name: 'Salvar conjunto' }).click();

		await expect.element(alert('não está mais no guarda-roupa')).toBeVisible();
	});

	it('exclui um conjunto depois da confirmação, sem apagar as peças', async () => {
		const api = open({ 'DELETE /api/outfits/o-1': () => json(204) }, { outfits: [FRIDAY] });
		await render(Page);

		await page.getByRole('button', { name: 'Excluir o conjunto Look de sexta' }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();

		await expect.element(page.getByText('Conjunto excluído.')).toBeVisible();
		await expect.element(page.getByText(/Nenhum conjunto salvo ainda/)).toBeVisible();
		expect(api.to('DELETE /api/outfits/o-1')).toHaveLength(1);
		expect(
			api.all.filter((call) => call.url.includes('/garments/') && call.method !== 'GET')
		).toEqual([]);
	});
});
