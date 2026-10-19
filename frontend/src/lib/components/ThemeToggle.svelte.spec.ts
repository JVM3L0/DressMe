import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { STORAGE_KEY, applyTheme, currentTheme, toggleTheme } from '#lib/theme.ts';

import ThemeToggle from './ThemeToggle.svelte';

const root = document.documentElement;
let themeColor: HTMLMetaElement;

beforeEach(() => {
	localStorage.clear();
	delete root.dataset.theme;
	themeColor = document.createElement('meta');
	themeColor.name = 'theme-color';
	document.head.append(themeColor);
});

afterEach(() => {
	themeColor.remove();
	delete root.dataset.theme;
	localStorage.clear();
	vi.restoreAllMocks();
});

describe('tema', () => {
	it('sem escolha salva, segue o tema do sistema', () => {
		const system = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

		expect(currentTheme()).toBe(system);
	});

	it('aplica, salva e atualiza a cor da barra do navegador', () => {
		applyTheme('dark');

		expect(root.dataset.theme).toBe('dark');
		expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
		expect(themeColor.content).toBe('#1d2021');
		expect(currentTheme()).toBe('dark');
	});

	it('alterna entre claro e escuro', () => {
		applyTheme('light');

		expect(toggleTheme()).toBe('dark');
		expect(toggleTheme()).toBe('light');
		expect(themeColor.content).toBe('#f9f5d7');
	});

	it('funciona mesmo sem acesso ao armazenamento', () => {
		vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
			throw new DOMException('bloqueado', 'SecurityError');
		});

		expect(() => applyTheme('dark')).not.toThrow();
		expect(root.dataset.theme).toBe('dark');
	});
});

describe('ThemeToggle', () => {
	it('descreve a ação, e não o estado atual', async () => {
		root.dataset.theme = 'light';
		await render(ThemeToggle);

		await expect.element(page.getByRole('button', { name: 'Usar tema escuro' })).toBeVisible();
	});

	it('troca o tema ao clicar e atualiza o rótulo', async () => {
		root.dataset.theme = 'light';
		await render(ThemeToggle);

		await page.getByRole('button', { name: 'Usar tema escuro' }).click();

		expect(root.dataset.theme).toBe('dark');
		expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
		await expect.element(page.getByRole('button', { name: 'Usar tema claro' })).toBeVisible();
	});
});
