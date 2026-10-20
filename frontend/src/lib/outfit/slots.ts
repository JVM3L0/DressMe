/**
 * Encaixes do conjunto (ADR-0008): uma peça por categoria (até 4 acessórios), e a peça única
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

/** Peças escolhidas em cada categoria: uma, ou até `MAX_ACCESSORIES` nos acessórios. Nunca guarda lista vazia. */
export type Selection = Partial<Record<GarmentCategory, Piece[]>>;

export const MAX_ACCESSORIES = 4;

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

export const piecesIn = (selection: Selection, category: GarmentCategory): Piece[] =>
	selection[category] ?? [];

/** A peça de uma categoria de peça só (todas, menos os acessórios) */
export const firstIn = (selection: Selection, category: GarmentCategory): Piece | undefined =>
	selection[category]?.[0];

/** Peças que sairiam do conjunto se uma peça desta categoria fosse escolhida (para avisar antes) */
export function replacedBy(selection: Selection, category: GarmentCategory): Piece[] {
	return conflictsWith(category).flatMap((conflicting) => piecesIn(selection, conflicting));
}

/** Acessórios: somam-se (sem repetir a mesma peça); `replacing` troca um específico */
function withAccessory(current: Piece[], piece: Piece, replacing?: Piece): Piece[] {
	const list = replacing
		? current.map((item) => (item.uid === replacing.uid ? piece : item))
		: [...current, piece];
	const unique = list.filter((item, index) => list.findIndex((o) => o.uid === item.uid) === index);
	return unique.slice(0, MAX_ACCESSORIES);
}

/**
 * Escolhe a peça no seu encaixe, tirando as que não combinam com ela. Nos
 * acessórios, a peça entra junto com as outras (até 4), ou no lugar de
 * `replacing`; nas demais categorias, troca a que estava.
 */
export function choose(selection: Selection, piece: Piece, replacing?: Piece): Selection {
	const next: Selection = { ...selection };
	for (const category of conflictsWith(piece.category)) delete next[category];
	next[piece.category] =
		piece.category === 'accessory'
			? withAccessory(piecesIn(selection, 'accessory'), piece, replacing)
			: [piece];
	return next;
}

/** Tira uma peça do conjunto (e a categoria, se ela ficar sem peças) */
export function remove(selection: Selection, piece: Piece): Selection {
	const next = { ...selection };
	const rest = piecesIn(selection, piece.category).filter((item) => item.uid !== piece.uid);
	if (rest.length > 0) next[piece.category] = rest;
	else delete next[piece.category];
	return next;
}

export function clear(selection: Selection, category: GarmentCategory): Selection {
	const next = { ...selection };
	delete next[category];
	return next;
}

/** Peças escolhidas, na ordem do corpo (os acessórios, na ordem em que entraram) */
export function orderedPieces(selection: Selection): Piece[] {
	return SLOT_ORDER.flatMap((category) => piecesIn(selection, category));
}

/**
 * Encaixes desenhados no mapa do corpo: cabeça, tronco, pernas e pés. A peça
 * única só ganha um encaixe quando escolhida (antes disso, é uma opção à
 * parte), e então ocupa o lugar da parte de cima e da de baixo, que somem.
 */
export function visibleSlots(selection: Selection): GarmentCategory[] {
	if (selection.one_piece) return SLOT_ORDER.filter((c) => !COVERED_BY_ONE_PIECE.includes(c));
	return SLOT_ORDER.filter((category) => category !== 'one_piece');
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
