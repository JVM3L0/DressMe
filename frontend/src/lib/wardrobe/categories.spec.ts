import { describe, expect, it } from 'vitest';

import { CATEGORIES, categoryLabel, countByCategory, isCategory } from './categories.ts';

describe('categorias', () => {
	it('são as 6 do backend, sem repetição', () => {
		const values = CATEGORIES.map((category) => category.value);

		expect(values).toEqual(['top', 'outerwear', 'bottom', 'one_piece', 'footwear', 'accessory']);
		expect(new Set(values).size).toBe(values.length);
	});

	it('todas têm nome e exemplos', () => {
		for (const category of CATEGORIES) {
			expect(category.label).not.toBe('');
			expect(category.examples).not.toBe('');
		}
	});

	it('traduz o valor para o nome', () => {
		expect(categoryLabel('one_piece')).toBe('Peça única');
	});

	it('reconhece só valores válidos', () => {
		expect(isCategory('top')).toBe(true);
		expect(isCategory('chapeu')).toBe(false);
		expect(isCategory(undefined)).toBe(false);
	});

	it('conta as peças de cada categoria, incluindo as vazias', () => {
		const counts = countByCategory([
			{ category: 'top' },
			{ category: 'top' },
			{ category: 'bottom' }
		]);

		expect(counts).toEqual({
			top: 2,
			outerwear: 0,
			bottom: 1,
			one_piece: 0,
			footwear: 0,
			accessory: 0
		});
	});
});
