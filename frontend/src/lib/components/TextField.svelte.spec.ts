import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';

import TextField from './TextField.svelte';

describe('TextField', () => {
	it('associa o rótulo ao campo', async () => {
		const screen = await render(TextField, { label: 'E-mail', name: 'email' });

		await expect.element(screen.getByLabelText('E-mail')).toHaveAttribute('name', 'email');
	});

	it('descreve o campo pela dica quando não há erro', async () => {
		const screen = await render(TextField, {
			label: 'Senha',
			name: 'password',
			hint: 'Pelo menos 8 caracteres.'
		});
		const input = screen.getByLabelText('Senha');

		await expect.element(input).toHaveAccessibleDescription('Pelo menos 8 caracteres.');
		await expect.element(input).not.toHaveAttribute('aria-invalid');
	});

	it('troca a dica pelo erro e marca o campo como inválido', async () => {
		const screen = await render(TextField, {
			label: 'Senha',
			name: 'password',
			hint: 'Pelo menos 8 caracteres.',
			error: 'Use pelo menos 8 caracteres.'
		});
		const input = screen.getByLabelText('Senha');

		await expect.element(input).toHaveAttribute('aria-invalid', 'true');
		await expect.element(input).toHaveAccessibleDescription('Use pelo menos 8 caracteres.');
		await expect
			.element(screen.getByText('Pelo menos 8 caracteres.', { exact: true }))
			.not.toBeInTheDocument();
	});

	it('repassa atributos nativos ao input', async () => {
		const screen = await render(TextField, {
			label: 'E-mail',
			name: 'email',
			type: 'email',
			autocomplete: 'email',
			required: true
		});
		const input = screen.getByLabelText('E-mail');

		await expect.element(input).toHaveAttribute('type', 'email');
		await expect.element(input).toHaveAttribute('autocomplete', 'email');
		await expect.element(input).toBeRequired();
	});
});
