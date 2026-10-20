import { describe, expect, it } from 'vitest';

import {
	IMAGE_MAX_BYTES,
	IMAGE_MESSAGES,
	formatFileSize,
	imageProblem,
	validateImage
} from './validation.ts';

const file = (type: string, size = 1000) => new File([new Uint8Array(size)], 'foto', { type });

describe('imageProblem', () => {
	it('exige uma imagem', () => {
		expect(imageProblem(undefined)).toBe('missing');
		expect(imageProblem(null)).toBe('missing');
	});

	it.each(['image/jpeg', 'image/png'])('aceita %s', (type) => {
		expect(imageProblem(file(type))).toBeUndefined();
	});

	it.each(['image/gif', 'image/webp', 'image/heic', 'application/pdf', 'text/plain'])(
		'recusa %s',
		(type) => {
			expect(imageProblem(file(type))).toBe('unsupported');
		}
	);

	it('deixa o backend decidir quando o aparelho não informa o tipo', () => {
		expect(imageProblem(file(''))).toBeUndefined();
	});

	it('aceita exatamente 10 MB e recusa acima disso', () => {
		expect(imageProblem(file('image/png', IMAGE_MAX_BYTES))).toBeUndefined();
		expect(imageProblem(file('image/png', IMAGE_MAX_BYTES + 1))).toBe('too_large');
	});

	it('o tipo errado vem antes do tamanho', () => {
		expect(imageProblem(file('image/gif', IMAGE_MAX_BYTES + 1))).toBe('unsupported');
	});
});

describe('validateImage', () => {
	it('devolve a mensagem em português, ou nada se for válida', () => {
		expect(validateImage(undefined)).toBe(IMAGE_MESSAGES.missing);
		expect(validateImage(file('image/gif'))).toBe(IMAGE_MESSAGES.unsupported);
		expect(validateImage(file('image/jpeg'))).toBeUndefined();
	});
});

describe('formatFileSize', () => {
	it.each([
		[500, '1 KB'],
		[200 * 1024, '200 KB'],
		[Math.round(2.4 * 1024 * 1024), '2,4 MB'],
		[IMAGE_MAX_BYTES, '10 MB']
	])('%i bytes -> %s', (bytes, text) => {
		expect(formatFileSize(bytes)).toBe(text);
	});
});
