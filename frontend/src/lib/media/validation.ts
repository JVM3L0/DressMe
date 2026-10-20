/**
 * Regras das imagens enviadas, espelhando o backend (ADR-0003). A checagem no
 * navegador só poupa um envio inútil; o backend confere o conteúdo de verdade.
 */

export const IMAGE_MAX_BYTES = 10 * 1024 * 1024;

export const IMAGE_TYPES = ['image/jpeg', 'image/png'] as const;

/** Valor do atributo `accept`: no celular, abre a câmera ou a galeria já filtrada */
export const IMAGE_ACCEPT = IMAGE_TYPES.join(',');

export type ImageProblem = 'missing' | 'unsupported' | 'too_large';

export const IMAGE_MESSAGES: Record<ImageProblem, string> = {
	missing: 'Escolha uma imagem.',
	unsupported: 'Envie uma imagem JPEG ou PNG.',
	too_large: 'A imagem passa de 10 MB. Escolha uma menor.'
};

export function imageProblem(file: File | undefined | null): ImageProblem | undefined {
	if (!file) return 'missing';
	// Alguns aparelhos não informam o tipo: nesse caso, o backend decide
	if (file.type && !(IMAGE_TYPES as readonly string[]).includes(file.type)) return 'unsupported';
	if (file.size > IMAGE_MAX_BYTES) return 'too_large';
}

/** Mensagem de erro da imagem, ou `undefined` se ela puder ser enviada */
export function validateImage(file: File | undefined | null): string | undefined {
	const problem = imageProblem(file);
	return problem && IMAGE_MESSAGES[problem];
}

/** Tamanho para exibir, ex.: "2,4 MB" */
export function formatFileSize(bytes: number): string {
	if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
	return `${(bytes / (1024 * 1024)).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} MB`;
}
