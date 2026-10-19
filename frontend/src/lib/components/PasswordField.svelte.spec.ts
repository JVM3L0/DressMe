import { describe, expect, it } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import PasswordField from './PasswordField.svelte';

describe('PasswordField', () => {
	it('expõe o elemento do campo para o formulário focar', async () => {
		const props = $state({ label: 'Senha', name: 'password', input: undefined });
		await render(PasswordField, props);

		expect(props.input).toBeInstanceOf(HTMLInputElement);
	});

	it('mostra e oculta a senha sem perder o valor', async () => {
		await render(PasswordField, { label: 'Senha', name: 'password', value: 'segredo-1' });
		const field = page.getByLabelText('Senha', { exact: true });

		await expect.element(field).toHaveAttribute('type', 'password');
		await page.getByRole('button', { name: 'Mostrar senha' }).click();
		await expect.element(field).toHaveAttribute('type', 'text');
		await expect.element(field).toHaveValue('segredo-1');
	});
});
