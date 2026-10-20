import { cellRect, fitInCell, gridFor } from './grid.ts';

/** Lado de cada célula da imagem das roupas, em pixels */
export const CELL_SIZE = 512;
const PADDING = 24;
/** Branco liso: é o fundo que as IAs de imagem entendem melhor, e as peças em PNG recortado ficam nítidas */
const BACKGROUND = '#ffffff';

function toPng(canvas: HTMLCanvasElement): Promise<Blob> {
	return new Promise((resolve, reject) =>
		canvas.toBlob(
			(blob) => (blob ? resolve(blob) : reject(new Error('Não foi possível gerar a imagem.'))),
			'image/png'
		)
	);
}

function newCanvas(width: number, height: number) {
	const canvas = document.createElement('canvas');
	canvas.width = width;
	canvas.height = height;
	const context = canvas.getContext('2d');
	if (!context) throw new Error('Este navegador não consegue gerar a imagem.');
	return { canvas, context };
}

/**
 * Junta as imagens numa grade de células quadradas, na ordem recebida (da
 * esquerda para a direita, de cima para baixo), sobre fundo branco. Tudo
 * acontece no navegador: nada é enviado ao servidor.
 */
export async function composeCollage(images: readonly Blob[]): Promise<Blob> {
	if (images.length === 0) throw new Error('Escolha ao menos uma peça.');
	const { columns, rows } = gridFor(images.length);
	const { canvas, context } = newCanvas(columns * CELL_SIZE, rows * CELL_SIZE);
	context.fillStyle = BACKGROUND;
	context.fillRect(0, 0, canvas.width, canvas.height);

	const bitmaps = await Promise.all(images.map((blob) => createImageBitmap(blob)));
	try {
		bitmaps.forEach((bitmap, index) => {
			const cell = cellRect(index, columns, CELL_SIZE);
			const target = fitInCell(bitmap.width, bitmap.height, cell, PADDING);
			context.drawImage(bitmap, target.x, target.y, target.width, target.height);
		});
	} finally {
		bitmaps.forEach((bitmap) => bitmap.close());
	}
	return toPng(canvas);
}

/**
 * Converte a imagem para PNG, o único formato de imagem que a área de
 * transferência aceita em todos os navegadores (as fotos são JPEG).
 */
export async function toPngBlob(image: Blob): Promise<Blob> {
	if (image.type === 'image/png') return image;
	const bitmap = await createImageBitmap(image);
	try {
		const { canvas, context } = newCanvas(bitmap.width, bitmap.height);
		context.drawImage(bitmap, 0, 0);
		return await toPng(canvas);
	} finally {
		bitmap.close();
	}
}
