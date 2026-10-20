/**
 * Gera, por regras, o texto para pedir a uma IA de imagens que vista a pessoa
 * da foto com as roupas do conjunto (ADR-0008). O VirtualFit não fala com
 * nenhuma IA: a pessoa cola a foto, a imagem das roupas e este texto onde
 * preferir. O texto é em inglês, que as IAs de imagem costumam entender
 * melhor; os nomes das peças seguem como a pessoa os escreveu.
 */

import type { GarmentCategory } from '#lib/wardrobe/categories.ts';

export interface PromptItem {
	category: GarmentCategory;
	name?: string | null;
}

export interface PromptOptions {
	/** Mantém o fundo da foto original (padrão) ou deixa a IA escolher um neutro */
	keepBackground?: boolean;
	/** Pedido extra, em texto livre ("em um café", "mais justo") */
	note?: string;
}

export const NOTE_MAX = 200;

const CATEGORY_NAMES: Record<GarmentCategory, string> = {
	top: 'Top',
	outerwear: 'Outerwear',
	bottom: 'Bottom',
	one_piece: 'One-piece (dress or jumpsuit)',
	footwear: 'Footwear',
	accessory: 'Accessory'
};

/** Texto de uma linha: sem quebras, espaços repetidos nem aspas que fechariam a citação */
function oneLine(text: string): string {
	return text.replace(/\s+/g, ' ').replace(/"/g, "'").trim();
}

function describe(item: PromptItem, index: number): string {
	const category = CATEGORY_NAMES[item.category];
	const name = item.name ? oneLine(item.name) : '';
	return name ? `  ${index + 1}. ${category}: "${name}"` : `  ${index + 1}. ${category}`;
}

/** `items` já deve vir na ordem da imagem das roupas (`orderedPieces`) */
export function buildPrompt(items: readonly PromptItem[], options: PromptOptions = {}): string {
	const { keepBackground = true } = options;
	const note = oneLine(options.note ?? '').slice(0, NOTE_MAX);
	const single = items.length === 1;

	const lines = [
		'You are given two images. Image 1 is a photo of a person. ' +
			(single
				? 'Image 2 shows one clothing item:'
				: 'Image 2 is a grid of clothing items, read left to right, top to bottom:'),
		...items.map(describe),
		'',
		`Generate a photorealistic image of the same person from Image 1 wearing exactly ${
			single ? 'this item' : 'these items'
		}. Keep the face, hair, skin tone, body shape and pose unchanged.` +
			(keepBackground
				? ' Keep the original background.'
				: ' Use a clean, neutral studio background.'),
		'Fit the clothes naturally, with realistic folds, shadows and lighting. ' +
			'Do not add any other clothing or accessories. Show the full body.'
	];
	if (note) lines.push('', `Additional request: ${note}`);
	return lines.join('\n');
}
