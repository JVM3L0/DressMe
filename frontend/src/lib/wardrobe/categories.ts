import type { components } from '#lib/api/schema.ts';

export type GarmentCategory = components['schemas']['GarmentCategory'];

export interface CategoryInfo {
	value: GarmentCategory;
	/** Nome curto, para o filtro e as legendas */
	label: string;
	/** Exemplos, para quem não sabe onde a peça se encaixa */
	examples: string;
}

/**
 * Categorias pela região do corpo (ADR-0001): definem a camada e a posição
 * inicial da peça no provador. Em ordem de baixo para cima, como se veste.
 */
export const CATEGORIES: readonly CategoryInfo[] = [
	{ value: 'top', label: 'Parte de cima', examples: 'camiseta, camisa, blusa, suéter' },
	{ value: 'outerwear', label: 'Agasalho', examples: 'jaqueta, casaco, blazer, cardigã' },
	{ value: 'bottom', label: 'Parte de baixo', examples: 'calça, short, saia' },
	{ value: 'one_piece', label: 'Peça única', examples: 'vestido, macacão' },
	{ value: 'footwear', label: 'Calçado', examples: 'tênis, sapato, sandália, bota' },
	{ value: 'accessory', label: 'Acessório', examples: 'bolsa, boné, óculos, cinto' }
];

export const categoryLabel = (value: GarmentCategory): string =>
	CATEGORIES.find((category) => category.value === value)?.label ?? value;

export const isCategory = (value: unknown): value is GarmentCategory =>
	CATEGORIES.some((category) => category.value === value);

export const GARMENT_NAME_MAX = 60;

/** Quantas peças há em cada categoria, para o filtro */
export function countByCategory(garments: { category: GarmentCategory }[]) {
	const counts = Object.fromEntries(CATEGORIES.map((c) => [c.value, 0])) as Record<
		GarmentCategory,
		number
	>;
	for (const garment of garments) counts[garment.category] += 1;
	return counts;
}
