import { describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import MediaCard from './MediaCard.svelte';

const props = (overrides: Record<string, unknown> = {}) => ({
	src: 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==',
	width: 400,
	height: 500,
	alt: 'Camisa azul',
	title: 'Camisa azul',
	detail: 'Parte de cima',
	subject: 'Camisa azul',
	ondelete: vi.fn(),
	...overrides
});

describe('MediaCard', () => {
	it('mostra a imagem com texto alternativo, o título e o detalhe', async () => {
		await render(MediaCard, props());

		await expect.element(page.getByAltText('Camisa azul')).toBeVisible();
		await expect.element(page.getByText('Parte de cima')).toBeVisible();
		await expect.element(page.getByAltText('Camisa azul')).toHaveAttribute('width', '400');
		await expect.element(page.getByAltText('Camisa azul')).toHaveAttribute('loading', 'lazy');
	});

	it('o botão diz o que será excluído, para quem usa leitor de tela', async () => {
		await render(MediaCard, props());

		await expect.element(page.getByRole('button', { name: 'Excluir Camisa azul' })).toBeVisible();
	});

	it('pede confirmação antes de excluir', async () => {
		const ondelete = vi.fn();
		await render(MediaCard, props({ ondelete }));

		await page.getByRole('button', { name: 'Excluir Camisa azul' }).click();

		expect(ondelete).not.toHaveBeenCalled();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		expect(ondelete).toHaveBeenCalledOnce();
	});

	it('permite desistir da exclusão', async () => {
		const ondelete = vi.fn();
		await render(MediaCard, props({ ondelete }));

		await page.getByRole('button', { name: 'Excluir Camisa azul' }).click();
		await page.getByRole('button', { name: 'Cancelar' }).click();

		await expect.element(page.getByRole('button', { name: 'Excluir Camisa azul' })).toBeVisible();
		await expect
			.element(page.getByRole('button', { name: 'Excluir mesmo' }))
			.not.toBeInTheDocument();
		expect(ondelete).not.toHaveBeenCalled();
	});

	it('desabilita a exclusão enquanto ela acontece', async () => {
		await render(MediaCard, props({ busy: true }));

		await expect.element(page.getByRole('button', { name: 'Excluir Camisa azul' })).toBeDisabled();
	});
});
