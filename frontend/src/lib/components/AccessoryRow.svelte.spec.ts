import { describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import AccessoryRow from './AccessoryRow.svelte';

const hat = (n: number) => ({
	uid: `hat-${n}`,
	category: 'accessory' as const,
	name: n === 3 ? null : `Acessório ${n}`
});

const props = (pieces: ReturnType<typeof hat>[], overrides: Record<string, unknown> = {}) => ({
	pieces,
	onadd: vi.fn(),
	onedit: vi.fn(),
	...overrides
});

describe('AccessoryRow', () => {
	it('sem acessórios, só convida a adicionar, e mostra 0 de 4', async () => {
		await render(AccessoryRow, props([]));

		await expect.element(page.getByText('0 de 4')).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Adicionar acessório' })).toBeVisible();
	});

	it('mostra a miniatura de cada acessório, com o nome na dica e no rótulo', async () => {
		await render(AccessoryRow, props([hat(1), hat(3)]));

		const first = page.getByRole('button', { name: 'Trocar acessório: Acessório 1' });
		await expect.element(first).toHaveAttribute('title', 'Acessório 1');
		await expect
			.element(page.getByRole('button', { name: 'Trocar acessório: Acessório' }).last())
			.toBeVisible();
		const sources = [...document.querySelectorAll('img')].map((image) => image.getAttribute('src'));
		expect(sources).toEqual(['/api/garments/hat-1/thumbnail', '/api/garments/hat-3/thumbnail']);
		await expect.element(page.getByText('2 de 4')).toBeVisible();
	});

	it('o "+" tem ícone e rótulo, e a dica de tocar para trocar só aparece com acessórios', async () => {
		await render(AccessoryRow, props([]));
		await expect.element(page.getByText('Adicionar', { exact: true })).toBeVisible();
		await expect
			.element(page.getByText('Toque num acessório para trocar ou tirar.'))
			.not.toBeInTheDocument();
	});

	it('com acessórios, explica que dá para tocar neles', async () => {
		await render(AccessoryRow, props([hat(1)]));

		await expect.element(page.getByText('Toque num acessório para trocar ou tirar.')).toBeVisible();
	});

	it('abre a escolha ao adicionar, e a troca ao tocar num acessório', async () => {
		const onadd = vi.fn();
		const onedit = vi.fn();
		await render(AccessoryRow, props([hat(1)], { onadd, onedit }));

		await page.getByRole('button', { name: 'Adicionar acessório' }).click();
		await page.getByRole('button', { name: 'Trocar acessório: Acessório 1' }).click();

		expect(onadd).toHaveBeenCalledOnce();
		expect(onedit).toHaveBeenCalledWith(hat(1));
	});

	it('com 4 acessórios, o botão de adicionar some', async () => {
		await render(AccessoryRow, props([hat(1), hat(2), hat(3), hat(4)]));

		await expect.element(page.getByText('4 de 4')).toBeVisible();
		await expect
			.element(page.getByRole('button', { name: 'Adicionar acessório' }))
			.not.toBeInTheDocument();
	});
});
