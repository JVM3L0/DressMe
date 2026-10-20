import { describe, expect, it } from 'vitest';

import { NOTE_MAX, buildPrompt } from './prompt.ts';

const OUTFIT = [
	{ category: 'outerwear', name: 'Jaqueta jeans azul' },
	{ category: 'top', name: 'Camisa de linho branca' },
	{ category: 'bottom', name: 'Calça preta' },
	{ category: 'footwear', name: 'Tênis branco' }
] as const;

describe('buildPrompt', () => {
	it('descreve as imagens e lista as peças na ordem da grade', () => {
		expect(buildPrompt(OUTFIT)).toBe(
			[
				'You are given two images. Image 1 is a photo of a person. Image 2 is a grid of clothing items, read left to right, top to bottom:',
				'  1. Outerwear: "Jaqueta jeans azul"',
				'  2. Top: "Camisa de linho branca"',
				'  3. Bottom: "Calça preta"',
				'  4. Footwear: "Tênis branco"',
				'',
				'Generate a photorealistic image of the same person from Image 1 wearing exactly these items. Keep the face, hair, skin tone, body shape and pose unchanged. Keep the original background.',
				'Fit the clothes naturally, with realistic folds, shadows and lighting. Do not add any other clothing or accessories. Show the full body.'
			].join('\n')
		);
	});

	it('fala no singular quando há uma peça só', () => {
		const prompt = buildPrompt([{ category: 'one_piece', name: 'Vestido azul' }]);

		expect(prompt).toContain('Image 2 shows one clothing item:');
		expect(prompt).toContain('1. One-piece (dress or jumpsuit): "Vestido azul"');
		expect(prompt).toContain('wearing exactly this item.');
		expect(prompt).not.toContain('grid');
	});

	it('lista a categoria mesmo sem nome', () => {
		const prompt = buildPrompt([{ category: 'top' }, { category: 'bottom', name: '' }]);

		expect(prompt).toContain('  1. Top\n');
		expect(prompt).toContain('  2. Bottom\n');
	});

	it.each([
		['top', 'Top'],
		['outerwear', 'Outerwear'],
		['bottom', 'Bottom'],
		['one_piece', 'One-piece (dress or jumpsuit)'],
		['footwear', 'Footwear'],
		['accessory', 'Accessory']
	] as const)('chama %s de "%s"', (category, label) => {
		expect(buildPrompt([{ category }])).toContain(`1. ${label}`);
	});

	it('pode deixar a IA escolher o fundo', () => {
		const prompt = buildPrompt(OUTFIT, { keepBackground: false });

		expect(prompt).toContain('Use a clean, neutral studio background.');
		expect(prompt).not.toContain('Keep the original background.');
	});

	it('acrescenta o pedido extra no fim', () => {
		const prompt = buildPrompt(OUTFIT, { note: 'em um café' });

		expect(prompt.endsWith('\n\nAdditional request: em um café')).toBe(true);
	});

	it('ignora um pedido extra em branco', () => {
		expect(buildPrompt(OUTFIT, { note: '   \n ' })).not.toContain('Additional request');
	});

	it('mantém cada peça e o pedido numa linha só, sem aspas soltas', () => {
		const prompt = buildPrompt([{ category: 'top', name: 'Camisa\n"slim"   azul' }], {
			note: 'linha 1\n\nlinha 2'
		});

		expect(prompt).toContain('1. Top: "Camisa \'slim\' azul"');
		expect(prompt).toContain('Additional request: linha 1 linha 2');
	});

	it('limita o tamanho do pedido extra', () => {
		const prompt = buildPrompt(OUTFIT, { note: 'a'.repeat(NOTE_MAX + 50) });

		expect(prompt.split('Additional request: ')[1]).toHaveLength(NOTE_MAX);
	});

	it('é determinístico', () => {
		expect(buildPrompt(OUTFIT, { note: 'x' })).toBe(buildPrompt(OUTFIT, { note: 'x' }));
	});
});
