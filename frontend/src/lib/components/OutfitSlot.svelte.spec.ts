import { describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import type { GarmentCategory } from '#lib/wardrobe/categories.ts';

import OutfitSlot from './OutfitSlot.svelte';

const PIECE = { uid: 'abc', category: 'top', name: 'Camisa azul' } as const;

const props = (overrides: Record<string, unknown> = {}) => ({
	category: 'top' as GarmentCategory,
	onpick: vi.fn(),
	onclear: vi.fn(),
	...overrides
});

describe('OutfitSlot', () => {
	it('vazio, convida a escolher uma peça daquela categoria', async () => {
		const onpick = vi.fn();
		await render(OutfitSlot, props({ onpick }));

		await page.getByRole('button', { name: 'Escolher Parte de cima' }).click();

		expect(onpick).toHaveBeenCalledOnce();
		await expect.element(page.getByRole('button', { name: /Tirar/ })).not.toBeInTheDocument();
	});

	it('preenchido, mostra a miniatura, a categoria e o nome', async () => {
		await render(OutfitSlot, props({ piece: PIECE }));

		await expect.element(page.getByText('Parte de cima')).toBeVisible();
		await expect.element(page.getByText('Camisa azul')).toBeVisible();
		const image = document.querySelector('img');
		expect(image?.getAttribute('src')).toBe('/api/garments/abc/thumbnail');
		expect(image?.getAttribute('alt')).toBe('');
	});

	it('o botão de trocar diz a categoria e a peça atual', async () => {
		const onpick = vi.fn();
		await render(OutfitSlot, props({ piece: PIECE, onpick }));

		await page.getByRole('button', { name: 'Trocar Parte de cima: Camisa azul' }).click();

		expect(onpick).toHaveBeenCalledOnce();
	});

	it('tira a peça sem abrir a escolha', async () => {
		const onpick = vi.fn();
		const onclear = vi.fn();
		await render(OutfitSlot, props({ piece: PIECE, onpick, onclear }));

		await page.getByRole('button', { name: 'Tirar Camisa azul do conjunto' }).click();

		expect(onclear).toHaveBeenCalledOnce();
		expect(onpick).not.toHaveBeenCalled();
	});

	it('usa a categoria como nome quando a peça não tem nome', async () => {
		await render(OutfitSlot, props({ piece: { ...PIECE, name: null } }));

		await expect
			.element(page.getByRole('button', { name: 'Tirar Parte de cima do conjunto' }))
			.toBeVisible();
	});
});
