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

	it('vazio, parece clicável: ícone da categoria, "+" e "Toque para escolher"', async () => {
		await render(OutfitSlot, props());

		await expect.element(page.getByText('Toque para escolher')).toBeVisible();
		await expect.element(page.getByText('Parte de cima')).toBeVisible();
		const face = document.querySelector('.face') as HTMLElement;
		expect(getComputedStyle(face).cursor).toBe('pointer');
		// Um ícone grande da categoria e o "+" do canto (ambos decorativos)
		expect(face.querySelectorAll('svg')).toHaveLength(2);
		expect(
			[...face.querySelectorAll('svg')].every((svg) => svg.getAttribute('aria-hidden') === 'true')
		).toBe(true);
	});

	it('preenchido, mostra o ícone de trocar ao lado do nome', async () => {
		await render(OutfitSlot, props({ piece: PIECE }));

		const swap = document.querySelector('.swap') as HTMLElement;
		expect(swap.getAttribute('aria-hidden')).toBe('true');
		expect(swap.querySelector('svg')).not.toBeNull();
		expect(document.querySelector('.cta')).toBeNull();
	});

	it('preenchido, mostra a miniatura e o nome numa linha só, sem repetir a categoria', async () => {
		await render(OutfitSlot, props({ piece: PIECE }));

		await expect.element(page.getByText('Camisa azul')).toBeVisible();
		await expect.element(page.getByText('Parte de cima')).not.toBeInTheDocument();
		const image = document.querySelector('img');
		expect(image?.getAttribute('src')).toBe('/api/garments/abc/thumbnail');
		expect(image?.getAttribute('alt')).toBe('');
		// A categoria continua no nome do botão, para quem usa leitor de tela
		await expect
			.element(page.getByRole('button', { name: 'Trocar Parte de cima: Camisa azul' }))
			.toBeVisible();
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
