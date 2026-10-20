import { describe, expect, it } from 'vitest';

import { pixelAt, solidImage } from '#lib/testing/api-mock.ts';

import { CELL_SIZE, composeCollage, toPngBlob } from './collage.ts';

const RED = [255, 0, 0, 255];
const BLUE = [0, 0, 255, 255];
const WHITE = [255, 255, 255, 255];

async function size(blob: Blob) {
	const bitmap = await createImageBitmap(blob);
	return [bitmap.width, bitmap.height];
}

describe('composeCollage', () => {
	it('uma peça: uma célula quadrada, com a peça no centro e fundo branco', async () => {
		const collage = await composeCollage([await solidImage('#ff0000', 200, 100)]);

		expect(collage.type).toBe('image/png');
		expect(await size(collage)).toEqual([CELL_SIZE, CELL_SIZE]);
		expect(await pixelAt(collage, CELL_SIZE / 2, CELL_SIZE / 2)).toEqual(RED);
		expect(await pixelAt(collage, 2, 2)).toEqual(WHITE);
		// A peça é larga (2:1): sobra fundo branco em cima e embaixo
		expect(await pixelAt(collage, CELL_SIZE / 2, 60)).toEqual(WHITE);
	});

	it('duas peças: lado a lado, na ordem recebida', async () => {
		const collage = await composeCollage([
			await solidImage('#ff0000'),
			await solidImage('#0000ff')
		]);

		expect(await size(collage)).toEqual([2 * CELL_SIZE, CELL_SIZE]);
		expect(await pixelAt(collage, CELL_SIZE / 2, CELL_SIZE / 2)).toEqual(RED);
		expect(await pixelAt(collage, CELL_SIZE * 1.5, CELL_SIZE / 2)).toEqual(BLUE);
	});

	it('quatro peças: duas linhas de duas, da esquerda para a direita e de cima para baixo', async () => {
		const colors = ['#ff0000', '#0000ff', '#00ff00', '#000000'];
		const collage = await composeCollage(await Promise.all(colors.map((c) => solidImage(c))));

		expect(await size(collage)).toEqual([2 * CELL_SIZE, 2 * CELL_SIZE]);
		const center = (column: number, row: number) =>
			pixelAt(collage, CELL_SIZE * (column + 0.5), CELL_SIZE * (row + 0.5));
		expect(await center(0, 0)).toEqual(RED);
		expect(await center(1, 0)).toEqual(BLUE);
		expect(await center(0, 1)).toEqual([0, 255, 0, 255]);
		expect(await center(1, 1)).toEqual([0, 0, 0, 255]);
	});

	it('cinco peças: três colunas, e a última célula fica em branco', async () => {
		const collage = await composeCollage(
			await Promise.all(Array.from({ length: 5 }, () => solidImage('#ff0000')))
		);

		expect(await size(collage)).toEqual([3 * CELL_SIZE, 2 * CELL_SIZE]);
		expect(await pixelAt(collage, CELL_SIZE * 2.5, CELL_SIZE * 1.5)).toEqual(WHITE);
	});

	it('peça recortada (PNG transparente) fica sobre o fundo branco', async () => {
		const canvas = document.createElement('canvas');
		canvas.width = canvas.height = 50;
		const transparent = await new Promise<Blob>((resolve) =>
			canvas.toBlob((blob) => resolve(blob!), 'image/png')
		);

		const collage = await composeCollage([transparent]);

		expect(await pixelAt(collage, CELL_SIZE / 2, CELL_SIZE / 2)).toEqual(WHITE);
	});

	it('recusa um conjunto vazio', async () => {
		await expect(composeCollage([])).rejects.toThrow('Escolha ao menos uma peça.');
	});
});

describe('toPngBlob', () => {
	it('converte JPEG em PNG, mantendo o tamanho', async () => {
		const jpeg = await solidImage('#ff0000', 120, 80, 'image/jpeg');

		const png = await toPngBlob(jpeg);

		expect(png.type).toBe('image/png');
		expect(await size(png)).toEqual([120, 80]);
	});

	it('devolve o mesmo arquivo se já for PNG', async () => {
		const png = await solidImage('#ff0000');

		expect(await toPngBlob(png)).toBe(png);
	});
});
