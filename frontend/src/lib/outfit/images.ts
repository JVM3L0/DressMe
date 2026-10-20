import { photoImageUrl } from '#lib/photos/photos.ts';
import { garmentImageUrl } from '#lib/wardrobe/garments.ts';

import { composeCollage, toPngBlob } from './collage.ts';
import type { Piece } from './slots.ts';

/** Baixa uma imagem da API (mesma origem, com o cookie da sessão) */
export async function fetchImage(url: string): Promise<Blob> {
	const response = await fetch(url);
	if (response.status === 404) {
		throw new Error(
			'O arquivo de uma das imagens não existe mais. Exclua essa peça (ou foto) e envie de novo.'
		);
	}
	if (!response.ok) throw new Error('Não foi possível carregar a imagem. Tente de novo.');
	return response.blob();
}

/** A foto da pessoa, em PNG (a área de transferência não aceita JPEG) */
export const photoAsPng = async (photoUid: string): Promise<Blob> =>
	toPngBlob(await fetchImage(photoImageUrl(photoUid)));

/** As roupas (imagens inteiras) numa imagem só, na ordem recebida */
export async function clothesAsPng(pieces: readonly Piece[]): Promise<Blob> {
	const images = await Promise.all(pieces.map((piece) => fetchImage(garmentImageUrl(piece.uid))));
	return composeCollage(images);
}
