import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import type { Piece } from '#lib/outfit/slots.ts';
import { pixelAt, solidImage } from '#lib/testing/api-mock.ts';

import OutfitOutput from './OutfitOutput.svelte';

const PIECES = [
	{ uid: 'top-1', category: 'top', name: 'Camisa azul' },
	{ uid: 'bottom-1', category: 'bottom', name: 'Calça preta' }
] as const;

const write = vi.fn();
const writeText = vi.fn();
const fetched: string[] = [];

function stubClipboard(value: unknown) {
	Object.defineProperty(navigator, 'clipboard', { value, configurable: true });
}

beforeEach(async () => {
	// Como o navegador: a escrita só termina quando as imagens do item ficam prontas,
	// e falha se alguma falhar
	write.mockReset().mockImplementation(async (items: ClipboardItem[]) => {
		for (const item of items) for (const type of item.types) await item.getType(type);
	});
	writeText.mockReset().mockResolvedValue(undefined);
	fetched.length = 0;
	stubClipboard({ write, writeText });
	// A API devolve a foto em JPEG e as peças em PNG
	vi.stubGlobal(
		'fetch',
		vi.fn(async (input: RequestInfo | URL) => {
			const url = String(input instanceof Request ? input.url : input);
			fetched.push(url);
			const blob = url.includes('/photos/')
				? await solidImage('#00aa00', 300, 400, 'image/jpeg')
				: await solidImage('#ff0000', 100, 100);
			return new Response(blob);
		})
	);
});

afterEach(() => {
	Reflect.deleteProperty(navigator, 'clipboard');
	Reflect.deleteProperty(navigator, 'canShare');
	Reflect.deleteProperty(navigator, 'share');
	vi.restoreAllMocks();
	vi.unstubAllGlobals();
});

/** Imagem entregue ao `ClipboardItem` da última cópia */
async function copiedImage(): Promise<Blob> {
	const [items] = write.mock.calls.at(-1) as [ClipboardItem[]];
	return items[0].getType('image/png');
}

describe('OutfitOutput: texto', () => {
	it('mostra o texto gerado com as peças, na ordem', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		const text = page.getByLabelText('Texto para colar na IA');
		await expect.element(text).toHaveValue(expect.stringContaining('1. Top: "Camisa azul"'));
		await expect.element(text).toHaveValue(expect.stringContaining('2. Bottom: "Calça preta"'));
		await expect.element(text).toHaveAttribute('readonly');
	});

	it('o texto muda com o fundo e com o pedido extra', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });
		const text = page.getByLabelText('Texto para colar na IA');

		await page.getByLabelText('Manter o fundo da foto').click();
		await page.getByLabelText('Pedido extra (opcional)').fill('in a café');

		await expect.element(text).toHaveValue(expect.stringContaining('neutral studio background'));
		await expect
			.element(text)
			.toHaveValue(expect.stringContaining('Additional request: in a café'));
	});

	it('copia exatamente o texto exibido', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });
		const shown = (page.getByLabelText('Texto para colar na IA').element() as HTMLTextAreaElement)
			.value;

		await page.getByRole('button', { name: 'Copiar texto' }).click();

		await expect.element(page.getByText('Texto copiado. Cole na IA.')).toBeVisible();
		expect(writeText).toHaveBeenCalledWith(shown);
	});
});

describe('OutfitOutput: imagens', () => {
	it('copia a foto como PNG, convertida do JPEG da API', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Copiar foto' }).click();

		await expect.element(page.getByText('Foto copiada. Cole na IA.')).toBeVisible();
		expect(fetched.filter((url) => !url.includes('/thumbnail'))).toEqual(['/api/photos/p1/image']);
		const png = await copiedImage();
		expect(png.type).toBe('image/png');
		// O JPEG perde um pouco de cor ao ser comprimido
		const [red, green, blue, alpha] = await pixelAt(png, 150, 200);
		expect(red).toBeLessThan(8);
		expect(blue).toBeLessThan(8);
		expect(Math.abs(green - 170)).toBeLessThan(8);
		expect(alpha).toBe(255);
	});

	it('copia as roupas numa imagem só, buscando as imagens inteiras', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Copiar roupas' }).click();

		await expect.element(page.getByText('Roupas copiadas. Cole na IA.')).toBeVisible();
		expect(fetched.filter((url) => !url.includes('/thumbnail'))).toEqual([
			'/api/garments/top-1/image',
			'/api/garments/bottom-1/image'
		]);
		const collage = await copiedImage();
		const bitmap = await createImageBitmap(collage);
		expect([bitmap.width, bitmap.height]).toEqual([1024, 512]);
	});

	it('baixa a foto e as roupas com nomes fixos', async () => {
		const names: string[] = [];
		vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
			this: HTMLAnchorElement
		) {
			names.push(this.download);
		});
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Baixar foto' }).click();
		await expect.element(page.getByText('Foto baixada.')).toBeVisible();
		await page.getByRole('button', { name: 'Baixar roupas' }).click();
		await expect.element(page.getByText('Imagem das roupas baixada.')).toBeVisible();

		expect(names).toEqual(['minha-foto.png', 'roupas.png']);
	});

	it('explica quando o navegador bloqueia a cópia', async () => {
		write.mockRejectedValue(new DOMException('bloqueado', 'NotAllowedError'));
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Copiar foto' }).click();

		await expect
			.element(page.getByRole('alert'))
			.toHaveTextContent('O navegador bloqueou a cópia. Use o botão Baixar.');
	});

	it('mostra o erro quando a imagem não carrega', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn(async () => new Response(null, { status: 500 }))
		);
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Copiar roupas' }).click();

		await expect
			.element(page.getByRole('alert'))
			.toHaveTextContent('Não foi possível carregar a imagem. Tente de novo.');
	});
});

describe('OutfitOutput: pré-visualização', () => {
	it('mostra a imagem das roupas montada com as miniaturas, antes de copiar', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		const preview = page.getByAltText('Pré-visualização da imagem das roupas');
		await expect.element(preview).toBeVisible();
		await expect.element(preview).toHaveAttribute('src', expect.stringMatching(/^blob:/));
		expect(fetched.sort()).toEqual([
			'/api/garments/bottom-1/thumbnail',
			'/api/garments/top-1/thumbnail'
		]);
	});

	it('some quando o conjunto fica vazio, e não busca nada', async () => {
		await render(OutfitOutput, { pieces: [], photoUid: 'p1' });

		await expect
			.element(page.getByAltText('Pré-visualização da imagem das roupas'))
			.not.toBeInTheDocument();
		expect(fetched).toEqual([]);
	});

	it('segue sem pré-visualização, com as cópias funcionando, se as miniaturas falharem', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn(async (input: RequestInfo | URL) => {
				const url = String(input instanceof Request ? input.url : input);
				if (url.includes('/thumbnail')) return new Response(null, { status: 500 });
				return new Response(await solidImage('#ff0000'));
			})
		);
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Copiar roupas' }).click();

		await expect.element(page.getByText('Roupas copiadas. Cole na IA.')).toBeVisible();
		await expect
			.element(page.getByAltText('Pré-visualização da imagem das roupas'))
			.not.toBeInTheDocument();
	});
});

describe('OutfitOutput: imagem sem arquivo', () => {
	it('explica o que fazer quando o arquivo de uma peça não existe mais', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn(async () => new Response(null, { status: 404 }))
		);
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Copiar roupas' }).click();

		await expect
			.element(page.getByRole('alert'))
			.toHaveTextContent('O arquivo de uma das imagens não existe mais. Exclua essa peça');
	});
});

describe('OutfitOutput: estados', () => {
	it('sem foto, só o passo da foto fica desabilitado', async () => {
		await render(OutfitOutput, { pieces: PIECES });

		await expect.element(page.getByRole('button', { name: 'Copiar foto' })).toBeDisabled();
		await expect.element(page.getByRole('button', { name: 'Baixar foto' })).toBeDisabled();
		await expect.element(page.getByText('Escolha uma foto acima.')).toBeVisible();
		await expect.element(page.getByRole('button', { name: 'Copiar roupas' })).toBeEnabled();
	});

	it('sem peças, os passos das roupas e do texto ficam desabilitados', async () => {
		await render(OutfitOutput, { pieces: [], photoUid: 'p1' });

		await expect.element(page.getByRole('button', { name: 'Copiar roupas' })).toBeDisabled();
		await expect.element(page.getByRole('button', { name: 'Copiar texto' })).toBeDisabled();
		await expect.element(page.getByText('Escolha ao menos uma peça.')).toBeVisible();
		await expect.element(page.getByLabelText('Texto para colar na IA')).toHaveValue('');
		await expect.element(page.getByRole('button', { name: 'Copiar foto' })).toBeEnabled();
	});

	it('em contexto inseguro, oferece "mostrar para copiar" e baixar, e explica o porquê', async () => {
		stubClipboard({});
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await expect.element(page.getByRole('button', { name: 'Copiar foto' })).not.toBeInTheDocument();
		await expect
			.element(page.getByRole('button', { name: 'Copiar roupas' }))
			.not.toBeInTheDocument();
		await expect.element(page.getByRole('button', { name: 'Baixar foto' })).toBeEnabled();
		await expect
			.element(page.getByRole('button', { name: 'Mostrar foto para copiar' }))
			.toBeEnabled();
		await expect
			.element(page.getByRole('button', { name: 'Mostrar roupas para copiar' }))
			.toBeEnabled();
		await expect.element(page.getByText(/não é seguro \(HTTPS\)/)).toBeVisible();
		// O texto continua podendo ser copiado (tem alternativa sem a API moderna)
		await expect.element(page.getByRole('button', { name: 'Copiar texto' })).toBeEnabled();
	});
});

describe('OutfitOutput: mostrar para copiar (sem HTTPS)', () => {
	beforeEach(() => stubClipboard({}));

	it('mostra a foto inteira para segurar e copiar, com a dica', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Mostrar foto para copiar' }).click();

		const image = page.getByAltText('Sua foto: segure a imagem para copiar');
		await expect.element(image).toBeVisible();
		await expect.element(image).toHaveAttribute('src', expect.stringMatching(/^blob:/));
		await expect
			.element(page.getByText('Segure a imagem e toque em “Copiar imagem”.').first())
			.toBeVisible();
		expect(fetched).toContain('/api/photos/p1/image');
	});

	it('mostra a imagem das roupas, em tamanho inteiro, no lugar da pré-visualização', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Mostrar roupas para copiar' }).click();

		const image = page.getByAltText('Imagem das roupas: segure a imagem para copiar');
		await expect.element(image).toBeVisible();
		await expect
			.element(page.getByAltText('Pré-visualização da imagem das roupas'))
			.not.toBeInTheDocument();
		expect(fetched).toContain('/api/garments/top-1/image');
	});

	it('o mesmo botão esconde a imagem de novo, e marca o estado', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });
		await page.getByRole('button', { name: 'Mostrar foto para copiar' }).click();

		const toggle = page.getByRole('button', { name: 'Esconder foto' });
		await expect.element(toggle).toHaveAttribute('aria-pressed', 'true');
		await toggle.click();

		await expect
			.element(page.getByAltText('Sua foto: segure a imagem para copiar'))
			.not.toBeInTheDocument();
		await expect
			.element(page.getByRole('button', { name: 'Mostrar foto para copiar' }))
			.toHaveAttribute('aria-pressed', 'false');
	});

	it('a imagem some quando o conjunto muda, para não copiar uma montagem antiga', async () => {
		const props = $state<{ pieces: readonly Piece[]; photoUid: string }>({
			pieces: PIECES,
			photoUid: 'p1'
		});
		await render(OutfitOutput, props);
		await page.getByRole('button', { name: 'Mostrar roupas para copiar' }).click();
		await expect
			.element(page.getByAltText('Imagem das roupas: segure a imagem para copiar'))
			.toBeVisible();

		props.pieces = [PIECES[0]];

		await expect
			.element(page.getByAltText('Imagem das roupas: segure a imagem para copiar'))
			.not.toBeInTheDocument();
	});

	it('com acesso seguro, esses botões não existem (há Copiar)', async () => {
		Reflect.deleteProperty(navigator, 'clipboard');
		stubClipboard({ write, writeText });
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await expect
			.element(page.getByRole('button', { name: 'Mostrar foto para copiar' }))
			.not.toBeInTheDocument();
		await expect.element(page.getByRole('button', { name: 'Copiar foto' })).toBeVisible();
	});
});

describe('OutfitOutput: compartilhar', () => {
	it('só aparece quando o aparelho sabe compartilhar arquivos', async () => {
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await expect
			.element(page.getByRole('button', { name: 'Compartilhar tudo' }))
			.not.toBeInTheDocument();
	});

	it('envia as duas imagens e o texto ao menu de compartilhar', async () => {
		const share = vi.fn().mockResolvedValue(undefined);
		Object.defineProperty(navigator, 'canShare', { value: () => true, configurable: true });
		Object.defineProperty(navigator, 'share', { value: share, configurable: true });
		await render(OutfitOutput, { pieces: PIECES, photoUid: 'p1' });

		await page.getByRole('button', { name: 'Compartilhar tudo' }).click();

		await vi.waitFor(() => expect(share).toHaveBeenCalledOnce());
		const [data] = share.mock.calls[0] as [{ files: File[]; text: string }];
		expect(data.files.map((file) => file.name)).toEqual(['minha-foto.png', 'roupas.png']);
		expect(data.text).toContain('1. Top: "Camisa azul"');
	});
});
