import { describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import type { GarmentCategory } from '#lib/wardrobe/categories.ts';

import SavedOutfits from './SavedOutfits.svelte';

const garment = (uid: string, category: GarmentCategory) => ({
	uid,
	category,
	name: null,
	width: 1,
	height: 1,
	created_at: '2026-10-19T12:00:00Z'
});

const GARMENTS = [garment('g1', 'top'), garment('g2', 'bottom')];

const outfit = (uid: string, name: string, garment_ids: string[]) => ({
	uid,
	name,
	garment_ids,
	created_at: '2026-10-19T12:00:00Z'
});

const props = (overrides: Record<string, unknown> = {}) => ({
	outfits: [outfit('o1', 'Look de sexta', ['g1', 'g2'])],
	garments: GARMENTS,
	onuse: vi.fn(),
	ondelete: vi.fn(),
	...overrides
});

describe('SavedOutfits', () => {
	it('orienta quando ainda não há conjuntos', async () => {
		await render(SavedOutfits, props({ outfits: [] }));

		await expect.element(page.getByText(/Nenhum conjunto salvo ainda/)).toBeVisible();
	});

	it('mostra o nome, a quantidade de peças e as miniaturas', async () => {
		await render(SavedOutfits, props());

		await expect.element(page.getByText('Look de sexta')).toBeVisible();
		await expect.element(page.getByText('2 peças')).toBeVisible();
		const sources = [...document.querySelectorAll('.thumbs img')].map((i) => i.getAttribute('src'));
		expect(sources).toEqual(['/api/garments/g1/thumbnail', '/api/garments/g2/thumbnail']);
	});

	it('conta só as peças que ainda existem', async () => {
		await render(
			SavedOutfits,
			props({ outfits: [outfit('o1', 'Look', ['g1', 'sumiu']), outfit('o2', 'Vazio', ['sumiu'])] })
		);

		await expect.element(page.getByText('1 peça', { exact: true })).toBeVisible();
		await expect.element(page.getByText('Conjunto vazio')).toBeVisible();
	});

	it('usa o conjunto escolhido', async () => {
		const onuse = vi.fn();
		const outfits = [outfit('o1', 'Look de sexta', ['g1'])];
		await render(SavedOutfits, props({ outfits, onuse }));

		await page.getByRole('button', { name: 'Usar o conjunto Look de sexta' }).click();

		expect(onuse).toHaveBeenCalledWith(outfits[0]);
	});

	it('só exclui depois da confirmação, e dá para desistir', async () => {
		const ondelete = vi.fn();
		await render(SavedOutfits, props({ ondelete }));

		await page.getByRole('button', { name: 'Excluir o conjunto Look de sexta' }).click();
		expect(ondelete).not.toHaveBeenCalled();
		await page.getByRole('button', { name: 'Cancelar' }).click();
		await expect
			.element(page.getByRole('button', { name: 'Excluir o conjunto Look de sexta' }))
			.toBeVisible();

		await page.getByRole('button', { name: 'Excluir o conjunto Look de sexta' }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		expect(ondelete).toHaveBeenCalledOnce();
	});

	it('destaca o conjunto em edição', async () => {
		await render(SavedOutfits, props({ activeUid: 'o1' }));

		expect(document.querySelector('.item')?.classList.contains('active')).toBe(true);
	});
});
