/**
 * Tema da interface. Sem escolha salva, segue o sistema
 * (`prefers-color-scheme`); a escolha manual fica no `localStorage` e é
 * aplicada como `data-theme` no `<html>`. O script inline em `src/app.html`
 * repete a leitura inicial para evitar piscar o tema errado.
 */

export type Theme = 'light' | 'dark';

export const STORAGE_KEY = 'theme';

/** Cor da barra do navegador no celular, igual ao fundo de cada tema */
const THEME_COLOR: Record<Theme, string> = { light: '#f9f5d7', dark: '#1d2021' };

const isTheme = (value: unknown): value is Theme => value === 'light' || value === 'dark';

function systemTheme(): Theme {
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/** Tema em uso agora: a escolha aplicada no documento ou, sem ela, o do sistema */
export function currentTheme(): Theme {
	const applied = document.documentElement.dataset.theme;
	return isTheme(applied) ? applied : systemTheme();
}

export function applyTheme(theme: Theme): void {
	document.documentElement.dataset.theme = theme;
	document.querySelector('meta[name="theme-color"]')?.setAttribute('content', THEME_COLOR[theme]);
	try {
		localStorage.setItem(STORAGE_KEY, theme);
	} catch {
		// Armazenamento indisponível (ex.: modo privado): vale só nesta visita
	}
}

export function toggleTheme(): Theme {
	const next: Theme = currentTheme() === 'dark' ? 'light' : 'dark';
	applyTheme(next);
	return next;
}
