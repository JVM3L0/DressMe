import { describe, expect, it } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { countByCategory, type GarmentCategory } from '#lib/wardrobe/categories.ts';

import CategoryFilter from './CategoryFilter.svelte';

const counts = countByCategory([{ category: 'top' }, { category: 'top' }, { category: 'bottom' }]);

describe('CategoryFilter', () => {
	it('lista "Tudo" e as 6 categorias, cada uma com a sua contagem', async () => {
		await render(CategoryFilter, { counts, total: 3 });

		await expect.element(page.getByRole('button', { name: 'Tudo 3' })).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Parte de cima 2' })).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Agasalho 0' })).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Acessório 0' })).toBeVisible();
		expect(page.getByRole('group', { name: 'Filtrar por categoria' }).elements()).toHaveLength(1);
	});

	it('marca "Tudo" como selecionado no início', async () => {
		await render(CategoryFilter, { counts, total: 3 });

		await expect
			.element(page.getByRole('button', { name: 'Tudo 3' }))
			.toHaveAttribute('aria-pressed', 'true');
		await expect
			.element(page.getByRole('button', { name: 'Parte de cima 2' }))
			.toHaveAttribute('aria-pressed', 'false');
	});

	it('seleciona uma categoria, e volta a "Tudo"', async () => {
		let selected: GarmentCategory | undefined = $state();
		await render(CategoryFilter, {
			counts,
			total: 3,
			get selected() {
				return selected;
			},
			set selected(value) {
				selected = value;
			}
		});

		await page.getByRole('button', { name: 'Parte de cima 2' }).click();
		expect(selected).toBe('top');
		await expect
			.element(page.getByRole('button', { name: 'Parte de cima 2' }))
			.toHaveAttribute('aria-pressed', 'true');

		await page.getByRole('button', { name: 'Tudo 3' }).click();
		expect(selected).toBeUndefined();
	});
});
