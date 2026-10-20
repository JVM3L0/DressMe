import { describe, expect, it } from 'vitest';

import {
	choose,
	clear,
	idsOf,
	isEmpty,
	orderedPieces,
	replacedBy,
	selectionFromIds,
	visibleSlots,
	type Piece,
	type Selection
} from './slots.ts';

const piece = (uid: string, category: Piece['category'], name?: string): Piece => ({
	uid,
	category,
	name
});

const TOP = piece('top-1', 'top', 'Camisa');
const BOTTOM = piece('bottom-1', 'bottom', 'Calça');
const DRESS = piece('dress-1', 'one_piece', 'Vestido');
const SHOES = piece('shoes-1', 'footwear');
const COAT = piece('coat-1', 'outerwear');
const HAT = piece('hat-1', 'accessory');

describe('choose', () => {
	it('coloca a peça no encaixe da sua categoria', () => {
		expect(choose({}, TOP)).toEqual({ top: TOP });
	});

	it('troca a peça que já estava no encaixe', () => {
		const other = piece('top-2', 'top');

		expect(choose({ top: TOP }, other)).toEqual({ top: other });
	});

	it('não altera a seleção original', () => {
		const original: Selection = { top: TOP };
		choose(original, SHOES);

		expect(original).toEqual({ top: TOP });
	});

	it('a peça única tira a parte de cima e a de baixo', () => {
		expect(choose({ top: TOP, bottom: BOTTOM, footwear: SHOES }, DRESS)).toEqual({
			one_piece: DRESS,
			footwear: SHOES
		});
	});

	it.each([TOP, BOTTOM])('uma peça %o tira a peça única', (garment) => {
		expect(choose({ one_piece: DRESS }, garment)).toEqual({ [garment.category]: garment });
	});

	it('as outras categorias não mexem nas demais', () => {
		expect(choose({ one_piece: DRESS }, COAT)).toEqual({ one_piece: DRESS, outerwear: COAT });
	});
});

describe('replacedBy', () => {
	it('lista o que a peça única tiraria, para avisar antes', () => {
		expect(replacedBy({ top: TOP, bottom: BOTTOM, footwear: SHOES }, 'one_piece')).toEqual([
			TOP,
			BOTTOM
		]);
	});

	it('lista a peça única que uma parte de cima ou de baixo tiraria', () => {
		expect(replacedBy({ one_piece: DRESS }, 'top')).toEqual([DRESS]);
	});

	it('não lista nada quando não há conflito', () => {
		expect(replacedBy({ top: TOP }, 'footwear')).toEqual([]);
		expect(replacedBy({}, 'one_piece')).toEqual([]);
	});
});

describe('clear', () => {
	it('esvazia só o encaixe indicado', () => {
		expect(clear({ top: TOP, footwear: SHOES }, 'top')).toEqual({ footwear: SHOES });
	});
});

describe('orderedPieces', () => {
	it('segue a ordem do corpo, não a da escolha', () => {
		const selection = [SHOES, HAT, BOTTOM, COAT, TOP].reduce(choose, {} as Selection);

		expect(orderedPieces(selection).map((p) => p.uid)).toEqual([
			'hat-1',
			'coat-1',
			'top-1',
			'bottom-1',
			'shoes-1'
		]);
	});

	it('a peça única ocupa o lugar da parte de cima e da de baixo', () => {
		const selection = [SHOES, DRESS, COAT].reduce(choose, {} as Selection);

		expect(orderedPieces(selection).map((p) => p.category)).toEqual([
			'outerwear',
			'one_piece',
			'footwear'
		]);
	});

	it('vem vazia sem peças', () => {
		expect(orderedPieces({})).toEqual([]);
		expect(isEmpty({})).toBe(true);
		expect(isEmpty({ top: TOP })).toBe(false);
	});
});

describe('visibleSlots', () => {
	it('desenha o corpo de cima para baixo, sem o encaixe da peça única', () => {
		expect(visibleSlots({ top: TOP })).toEqual([
			'accessory',
			'outerwear',
			'top',
			'bottom',
			'footwear'
		]);
	});

	it('com uma peça única, ela fica no lugar da parte de cima e da de baixo', () => {
		expect(visibleSlots({ one_piece: DRESS })).toEqual([
			'accessory',
			'outerwear',
			'one_piece',
			'footwear'
		]);
	});
});

describe('selectionFromIds', () => {
	const pieces = [TOP, BOTTOM, DRESS, SHOES];

	it('monta a seleção com as peças dos ids', () => {
		expect(selectionFromIds(['top-1', 'shoes-1'], pieces)).toEqual({ top: TOP, footwear: SHOES });
	});

	it('ignora ids de peças que já não existem', () => {
		expect(selectionFromIds(['top-1', 'sumiu'], pieces)).toEqual({ top: TOP });
	});

	it('ida e volta com idsOf', () => {
		const selection = selectionFromIds(['shoes-1', 'bottom-1', 'top-1'], pieces);

		expect(idsOf(selection)).toEqual(['top-1', 'bottom-1', 'shoes-1']);
	});
});
