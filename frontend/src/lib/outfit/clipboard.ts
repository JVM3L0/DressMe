/**
 * Área de transferência, download e compartilhamento. Copiar **imagem** só
 * funciona em contexto seguro (HTTPS ou localhost); em HTTP pela rede local o
 * navegador bloqueia, e a tela oferece o download no lugar.
 */

/** O navegador deixa copiar imagens? */
export function canCopyImages(): boolean {
	return (
		typeof window !== 'undefined' &&
		window.isSecureContext &&
		typeof ClipboardItem !== 'undefined' &&
		typeof navigator.clipboard?.write === 'function'
	);
}

/**
 * Copia uma imagem PNG. Recebe uma promessa, e não o arquivo pronto: o Safari
 * só aceita a cópia se o `ClipboardItem` nascer dentro do clique, e gerar a
 * imagem leva um tempo.
 */
export async function copyImage(png: Promise<Blob>): Promise<void> {
	await navigator.clipboard.write([new ClipboardItem({ 'image/png': png })]);
}

/** Copia texto. Em HTTP (sem a API moderna), usa o método antigo, que ainda funciona para texto */
export async function copyText(text: string): Promise<void> {
	if (window.isSecureContext && navigator.clipboard?.writeText) {
		await navigator.clipboard.writeText(text);
		return;
	}
	const field = document.createElement('textarea');
	field.value = text;
	field.setAttribute('readonly', '');
	field.style.position = 'fixed';
	field.style.opacity = '0';
	document.body.append(field);
	field.select();
	const copied = document.execCommand('copy');
	field.remove();
	if (!copied) throw new Error('Não foi possível copiar o texto.');
}

export function downloadBlob(blob: Blob, filename: string): void {
	const url = URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.href = url;
	link.download = filename;
	document.body.append(link);
	link.click();
	link.remove();
	// O download já começou: o endereço pode ser liberado logo depois
	setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** O aparelho deixa compartilhar arquivos (o menu "Compartilhar" do celular)? */
export function canShareFiles(files: File[]): boolean {
	return (
		typeof navigator !== 'undefined' &&
		typeof navigator.canShare === 'function' &&
		navigator.canShare({ files })
	);
}

export const shareFiles = (files: File[], text: string) => navigator.share({ files, text });
