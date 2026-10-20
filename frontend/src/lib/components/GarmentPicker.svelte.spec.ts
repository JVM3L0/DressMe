import { describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import type { GarmentCategory } from '#lib/wardrobe/categories.ts';

import GarmentPicker from './GarmentPicker.svelte';

const garment = (uid: string, category: GarmentCategory, name: string | null) => ({
	uid,
	category,
	name,
	width: 400,
	height: 500,
	created_at: '2026-10-19T12:00:00Z'
});

const GARMENTS = [
	garment('1', 'top', 'Camisa azul'),
	garment('2', 'top', 'Camisa verde'),
	garment('3', 'bottom', 'Calça preta')
];

const props = (overrides: Record<string, unknown> = {}) => ({
	category: 'top' as GarmentCategory | undefined,
	garments: GARMENTS,
	onselect: vi.fn(),
	onclose: vi.fn(),
	...overrides
});

describe('GarmentPicker', () => {
	it('abre como janela modal, só com as peças da categoria', async () => {
		await render(GarmentPicker, props());

		await expect
			.element(page.getByRole('dialog', { name: 'Escolher: Parte de cima' }))
			.toBeVisible();
		expect(document.querySelector('dialog')?.matches(':modal')).toBe(true);
		await expect.element(page.getByRole('button', { name: 'Camisa azul' })).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Camisa verde' })).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Calça preta' })).not.toBeInTheDocument();
	});

	it('fica fechada sem categoria', async () => {
		await render(GarmentPicker, props({ category: undefined }));

		expect(document.querySelector('dialog')?.open).toBe(false);
	});

	it('entrega a peça escolhida', async () => {
		const onselect = vi.fn();
		await render(GarmentPicker, props({ onselect }));

		await page.getByRole('button', { name: 'Camisa verde' }).click();

		expect(onselect).toHaveBeenCalledWith(GARMENTS[1]);
	});

	it('marca a peça que já está no conjunto', async () => {
		await render(GarmentPicker, props({ current: { uid: '2', category: 'top' } }));

		await expect
			.element(page.getByRole('button', { name: 'Camisa verde' }))
			.toHaveAttribute('aria-pressed', 'true');
		await expect
			.element(page.getByRole('button', { name: 'Camisa azul' }))
			.toHaveAttribute('aria-pressed', 'false');
	});

	it('avisa quando a escolha tira outras peças do conjunto', async () => {
		await render(
			GarmentPicker,
			props({
				category: 'one_piece',
				garments: [garment('9', 'one_piece', 'Vestido')],
				replaced: [
					{ uid: '1', category: 'top', name: 'Camisa azul' },
					{ uid: '3', category: 'bottom', name: null }
				]
			})
		);

		await expect
			.element(page.getByText('Isso tira Camisa azul e Parte de baixo do conjunto.'))
			.toBeVisible();
	});

	it('esconde as peças que não podem ser escolhidas de novo', async () => {
		await render(GarmentPicker, props({ exclude: ['1'] }));

		await expect.element(page.getByRole('button', { name: 'Camisa azul' })).not.toBeInTheDocument();
		await expect.element(page.getByRole('button', { name: 'Camisa verde' })).toBeVisible();
	});

	it('avisa quando todas as peças da categoria já estão no conjunto', async () => {
		await render(GarmentPicker, props({ exclude: ['1', '2'] }));

		await expect
			.element(page.getByText('Todas as suas peças dessa categoria já estão no conjunto.'))
			.toBeVisible();
		await expect
			.element(page.getByRole('link', { name: 'Adicionar peça' }))
			.not.toBeInTheDocument();
	});

	it('oferece tirar a peça do conjunto, e fecha', async () => {
		const onremove = vi.fn();
		await render(GarmentPicker, props({ current: { uid: '1', category: 'top' }, onremove }));

		await page.getByRole('button', { name: 'Tirar do conjunto' }).click();

		expect(onremove).toHaveBeenCalledOnce();
		await vi.waitFor(() => expect(document.querySelector('dialog')?.open).toBe(false));
	});

	it('sem uma peça para trocar, não oferece tirar', async () => {
		await render(GarmentPicker, props());

		await expect
			.element(page.getByRole('button', { name: 'Tirar do conjunto' }))
			.not.toBeInTheDocument();
	});

	it('sem peças na categoria, leva ao guarda-roupa', async () => {
		await render(GarmentPicker, props({ category: 'accessory' }));

		await expect.element(page.getByText('Você ainda não tem peças nessa categoria.')).toBeVisible();
		await expect
			.element(page.getByRole('link', { name: 'Adicionar peça' }))
			.toHaveAttribute('href', '/guarda-roupa');
	});

	it('avisa o pai quando é fechada pelo botão Cancelar', async () => {
		const onclose = vi.fn();
		await render(GarmentPicker, props({ onclose }));

		await page.getByRole('button', { name: 'Cancelar' }).click();

		await vi.waitFor(() => expect(onclose).toHaveBeenCalled());
		expect(document.querySelector('dialog')?.open).toBe(false);
	});

	it('fecha ao clicar no fundo escurecido', async () => {
		const onclose = vi.fn();
		await render(GarmentPicker, props({ onclose }));
		const dialog = document.querySelector('dialog')!;

		dialog.dispatchEvent(new MouseEvent('click', { bubbles: true }));

		await vi.waitFor(() => expect(onclose).toHaveBeenCalled());
	});
});
