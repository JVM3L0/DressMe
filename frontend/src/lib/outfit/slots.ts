/**
 * Encaixes do conjunto (ADR-0008): uma peça por categoria, e a peça única
 * (vestido, macacão) ocupa o lugar da parte de cima e da parte de baixo. As
 * mesmas regras valem no backend (`domain/outfit_rules.py`), que é quem manda;
 * aqui elas evitam montar um conjunto que seria recusado.
 */

import type { GarmentCategory } from '#lib/wardrobe/categories.ts';

/** O que a montagem precisa saber de uma peça */
export interface Piece {
	uid: string;
	category: GarmentCategory;
	name?: string | null;
}

export type Selection = Partial<Record<GarmentCategory, Piece>>;

/**
 * Ordem dos encaixes na tela, do alto do corpo para baixo. É também a ordem
 * da imagem das roupas e do prompt (a IA lê a lista na mesma ordem da grade).
 */
export const SLOT_ORDER: readonly GarmentCategory[] = [
	'accessory',
	'outerwear',
	'top',
	'bottom',
	'one_piece',
	'footwear'
];

/** Categorias que a peça única substitui, e que a substituem */
const COVERED_BY_ONE_PIECE: readonly GarmentCategory[] = ['top', 'bottom'];

/** Categorias que não podem ficar junto com a peça escolhida */
function conflictsWith(category: GarmentCategory): readonly GarmentCategory[] {
	if (category === 'one_piece') return COVERED_BY_ONE_PIECE;
	if (COVERED_BY_ONE_PIECE.includes(category)) return ['one_piece'];
	return [];
}

/** Peças que sairiam do conjunto se uma peça desta categoria fosse escolhida (para avisar antes) */
export function replacedBy(selection: Selection, category: GarmentCategory): Piece[] {
	return conflictsWith(category).flatMap((conflicting) => selection[conflicting] ?? []);
}

/** Escolhe a peça no seu encaixe, tirando as que não combinam com ela */
export function choose(selection: Selection, piece: Piece): Selection {
	const next: Selection = { ...selection };
	for (const category of conflictsWith(piece.category)) delete next[category];
	next[piece.category] = piece;
	return next;
}

export function clear(selection: Selection, category: GarmentCategory): Selection {
	const next = { ...selection };
	delete next[category];
	return next;
}

/** Peças escolhidas, na ordem do corpo */
export function orderedPieces(selection: Selection): Piece[] {
	return SLOT_ORDER.flatMap((category) => selection[category] ?? []);
}

/**
 * Encaixes que aparecem na tela: com uma peça única escolhida, a parte de cima
 * e a de baixo somem (a peça única ocupa o lugar das duas), e sem ela o
 * encaixe da peça única fica como uma opção ao lado.
 */
export function visibleSlots(selection: Selection): GarmentCategory[] {
	if (selection.one_piece) return SLOT_ORDER.filter((c) => !COVERED_BY_ONE_PIECE.includes(c));
	return [...SLOT_ORDER];
}

/** Monta a seleção a partir dos ids de um conjunto salvo; ignora peças que já não existem */
export function selectionFromIds(ids: readonly string[], pieces: readonly Piece[]): Selection {
	const wanted = new Set(ids);
	let selection: Selection = {};
	for (const piece of pieces) {
		if (wanted.has(piece.uid)) selection = choose(selection, piece);
	}
	return selection;
}

export const idsOf = (selection: Selection): string[] =>
	orderedPieces(selection).map((piece) => piece.uid);

export const isEmpty = (selection: Selection): boolean => orderedPieces(selection).length === 0;
