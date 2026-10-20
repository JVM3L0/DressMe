import { describe, expect, it, vi } from 'vitest';
import { page, userEvent } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import ImagePicker from './ImagePicker.svelte';

const photo = (name = 'minha-foto.jpg', size = 2048) =>
	new File([new Uint8Array(size)], name, { type: 'image/jpeg' });

const input = () => page.getByLabelText(/Foto da peça/);

describe('ImagePicker', () => {
	it('aceita só JPEG e PNG, para o celular já filtrar a galeria', async () => {
		await render(ImagePicker, { label: 'Foto da peça' });

		await expect.element(input()).toHaveAttribute('accept', 'image/jpeg,image/png');
		await expect.element(page.getByText('JPEG ou PNG, até 10 MB')).toBeVisible();
	});

	it('mostra a pré-visualização, o nome e o tamanho do arquivo escolhido', async () => {
		await render(ImagePicker, { label: 'Foto da peça' });

		await userEvent.upload(input(), photo('camisa.jpg', 3 * 1024));

		await expect.element(page.getByAltText('Pré-visualização da imagem escolhida')).toBeVisible();
		await expect.element(page.getByText('camisa.jpg')).toBeVisible();
		await expect.element(page.getByText('3 KB')).toBeVisible();
		await expect.element(page.getByText('Trocar')).toBeVisible();
	});

	it('entrega o arquivo ao formulário e avisa a mudança', async () => {
		const onchange = vi.fn();
		let file: File | undefined;
		await render(ImagePicker, {
			label: 'Foto da peça',
			onchange,
			// `bind:file` no componente chega aqui por getter e setter
			get file() {
				return file;
			},
			set file(value) {
				file = value;
			}
		});

		await userEvent.upload(input(), photo('camisa.jpg'));

		expect(file?.name).toBe('camisa.jpg');
		expect(onchange).toHaveBeenCalledOnce();
	});

	it('volta ao estado vazio quando o formulário limpa o arquivo', async () => {
		let file: File | undefined = $state();
		await render(ImagePicker, {
			label: 'Foto da peça',
			get file() {
				return file;
			},
			set file(value) {
				file = value;
			}
		});
		await userEvent.upload(input(), photo());
		await expect.element(page.getByText('Trocar')).toBeVisible();

		file = undefined;

		await expect.element(page.getByText('Escolher imagem')).toBeVisible();
		await expect.element(input()).toHaveValue('');
	});

	it('liga o erro ao campo, e o erro substitui a dica', async () => {
		await render(ImagePicker, {
			label: 'Foto da peça',
			hint: 'De corpo inteiro.',
			error: 'Escolha uma imagem.'
		});

		await expect.element(input()).toHaveAttribute('aria-invalid', 'true');
		await expect.element(input()).toHaveAccessibleDescription('Escolha uma imagem.');
		await expect.element(page.getByText('De corpo inteiro.')).not.toBeInTheDocument();
	});

	it('descreve o campo pela dica quando não há erro', async () => {
		await render(ImagePicker, { label: 'Foto da peça', hint: 'De corpo inteiro.' });

		await expect.element(input()).toHaveAccessibleDescription('De corpo inteiro.');
		await expect.element(input()).not.toHaveAttribute('aria-invalid');
	});
});
