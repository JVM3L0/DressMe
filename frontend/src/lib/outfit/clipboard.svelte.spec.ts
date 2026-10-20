import { afterEach, describe, expect, it, vi } from 'vitest';

import { solidImage } from '#lib/testing/api-mock.ts';

import { canCopyImages, canShareFiles, copyImage, copyText, downloadBlob } from './clipboard.ts';

const original = Object.getOwnPropertyDescriptor(Navigator.prototype, 'clipboard');

function stubClipboard(value: unknown) {
	Object.defineProperty(navigator, 'clipboard', { value, configurable: true });
}

afterEach(() => {
	// Remove o stub da instância e volta ao `navigator.clipboard` de verdade
	Reflect.deleteProperty(navigator, 'clipboard');
	expect(Object.getOwnPropertyDescriptor(Navigator.prototype, 'clipboard')).toEqual(original);
	vi.restoreAllMocks();
	vi.unstubAllGlobals();
});

describe('canCopyImages', () => {
	it('vale em contexto seguro (localhost), com a API de imagens', () => {
		expect(window.isSecureContext).toBe(true);
		expect(canCopyImages()).toBe(true);
	});

	it('não vale sem a API de escrita na área de transferência', () => {
		stubClipboard({});

		expect(canCopyImages()).toBe(false);
	});

	it('não vale sem ClipboardItem', () => {
		vi.stubGlobal('ClipboardItem', undefined);

		expect(canCopyImages()).toBe(false);
	});
});

describe('copyImage', () => {
	it('grava um PNG na área de transferência, entregando a promessa da imagem', async () => {
		const write = vi.fn().mockResolvedValue(undefined);
		stubClipboard({ write });
		const png = await solidImage('#ff0000');

		await copyImage(Promise.resolve(png));

		const [items] = write.mock.calls[0] as [ClipboardItem[]];
		expect(items).toHaveLength(1);
		expect(items[0].types).toEqual(['image/png']);
		expect(await items[0].getType('image/png')).toBe(png);
	});

	it('chama a escrita de forma síncrona, como o Safari exige', async () => {
		const write = vi.fn().mockResolvedValue(undefined);
		stubClipboard({ write });

		const pending = copyImage(new Promise(() => {}));

		expect(write).toHaveBeenCalledOnce();
		void pending;
	});

	it('repassa o erro quando o navegador bloqueia', async () => {
		stubClipboard({
			write: vi.fn().mockRejectedValue(new DOMException('bloqueado', 'NotAllowedError'))
		});

		await expect(copyImage(Promise.resolve(new Blob()))).rejects.toThrow('bloqueado');
	});
});

describe('copyText', () => {
	it('usa a área de transferência moderna', async () => {
		const writeText = vi.fn().mockResolvedValue(undefined);
		stubClipboard({ writeText });

		await copyText('olá');

		expect(writeText).toHaveBeenCalledWith('olá');
	});

	it('sem a API moderna (HTTP), copia pelo método antigo e limpa a página', async () => {
		stubClipboard(undefined);
		const execCommand = vi.spyOn(document, 'execCommand').mockReturnValue(true);
		let copied = '';
		execCommand.mockImplementation(() => {
			copied = (document.activeElement as HTMLTextAreaElement).value;
			return true;
		});

		await copyText('texto do prompt');

		expect(execCommand).toHaveBeenCalledWith('copy');
		expect(copied).toBe('texto do prompt');
		expect(document.querySelector('textarea[readonly]')).toBeNull();
	});

	it('avisa quando nem o método antigo funciona', async () => {
		stubClipboard(undefined);
		vi.spyOn(document, 'execCommand').mockReturnValue(false);

		await expect(copyText('x')).rejects.toThrow('Não foi possível copiar o texto.');
		expect(document.querySelector('textarea[readonly]')).toBeNull();
	});
});

describe('downloadBlob', () => {
	it('baixa o arquivo com o nome dado, e libera o endereço depois', async () => {
		vi.useFakeTimers();
		const revoke = vi.spyOn(URL, 'revokeObjectURL');
		const clicked: { download: string; href: string }[] = [];
		vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
			this: HTMLAnchorElement
		) {
			clicked.push({ download: this.download, href: this.href });
		});

		downloadBlob(new Blob(['x'], { type: 'image/png' }), 'roupas.png');

		expect(clicked).toHaveLength(1);
		expect(clicked[0].download).toBe('roupas.png');
		expect(clicked[0].href).toMatch(/^blob:/);
		expect(document.querySelector('a[download]')).toBeNull();
		expect(revoke).not.toHaveBeenCalled();
		vi.advanceTimersByTime(1000);
		expect(revoke).toHaveBeenCalledOnce();
		vi.useRealTimers();
	});
});

describe('canShareFiles', () => {
	it('depende de o navegador saber compartilhar esses arquivos', () => {
		const file = new File([], 'x.png', { type: 'image/png' });
		vi.stubGlobal('navigator', { canShare: ({ files }: { files: File[] }) => files.length > 0 });

		expect(canShareFiles([file])).toBe(true);
		expect(canShareFiles([])).toBe(false);
	});

	it('é falso sem a API de compartilhamento', () => {
		vi.stubGlobal('navigator', {});

		expect(canShareFiles([new File([], 'x.png')])).toBe(false);
	});
});
