import { beforeEach, describe, expect, it, vi } from 'vitest';
import { page } from 'vitest/browser';
import { render } from 'vitest-browser-svelte';

import { loadSession, signIn } from '#lib/session.svelte.ts';

import SiteNav from './SiteNav.svelte';

const state = vi.hoisted(() => ({ pathname: '/fotos' }));
vi.mock('$app/state', () => ({
	page: {
		get url() {
			return new URL(`http://localhost${state.pathname}`);
		}
	}
}));

const USER = {
	uid: '00000000-0000-0000-0000-000000000001',
	username: 'joao',
	email: 'joao@example.com',
	created_at: '2026-10-19T12:00:00Z'
};

beforeEach(async () => {
	state.pathname = '/fotos';
	// Tamanho de celular (o padrão do navegador de teste é parecido)
	await page.viewport(390, 844);
});

describe('SiteNav', () => {
	it('mostra os links da conta para quem está logado', async () => {
		signIn(USER);
		await render(SiteNav);

		await expect
			.element(page.getByRole('link', { name: 'Fotos' }))
			.toHaveAttribute('href', '/fotos');
		await expect
			.element(page.getByRole('link', { name: 'Guarda-roupa' }))
			.toHaveAttribute('href', '/guarda-roupa');
		await expect
			.element(page.getByRole('link', { name: 'Provador' }))
			.toHaveAttribute('href', '/provador');
		await expect
			.element(page.getByRole('link', { name: 'Sua conta' }))
			.toHaveAttribute('href', '/conta');
	});

	it('marca a página atual', async () => {
		signIn(USER);
		state.pathname = '/guarda-roupa';
		await render(SiteNav);

		await expect
			.element(page.getByRole('link', { name: 'Guarda-roupa' }))
			.toHaveAttribute('aria-current', 'page');
		await expect
			.element(page.getByRole('link', { name: 'Fotos' }))
			.not.toHaveAttribute('aria-current');
	});

	it('mostra só "Entrar" para quem não tem sessão', async () => {
		vi.stubGlobal('fetch', async () => new Response(null, { status: 401 }));
		await loadSession();
		vi.unstubAllGlobals();
		await render(SiteNav);

		await expect
			.element(page.getByRole('link', { name: 'Entrar' }))
			.toHaveAttribute('href', '/entrar');
		expect(page.getByRole('link', { name: 'Fotos' }).elements()).toHaveLength(0);
	});
});

describe('SiteNav: layout (DT-14)', () => {
	const nav = () => document.querySelector('nav') as HTMLElement;
	const style = (element: Element) => getComputedStyle(element);

	it('no celular, logado, vira uma barra fixa embaixo da tela', async () => {
		signIn(USER);
		await render(SiteNav);

		expect(style(nav()).position).toBe('fixed');
		const box = nav().getBoundingClientRect();
		expect(Math.round(box.bottom)).toBe(window.innerHeight);
		expect(Math.round(box.width)).toBe(window.innerWidth);
	});

	it('cada destino tem ícone e rótulo, em colunas iguais, com alvo de toque de 44px ou mais', async () => {
		signIn(USER);
		await render(SiteNav);

		const links = [...nav().querySelectorAll('a')];
		expect(links).toHaveLength(4);
		for (const link of links) {
			const box = link.getBoundingClientRect();
			expect(box.height).toBeGreaterThanOrEqual(44);
			expect(box.width).toBeGreaterThanOrEqual(44);
			expect(style(link.querySelector('svg')!).display).toBe('block');
			expect(link.querySelector('svg')?.getAttribute('aria-hidden')).toBe('true');
		}
		const widths = links.map((link) => Math.round(link.getBoundingClientRect().width));
		expect(new Set(widths).size).toBe(1);
	});

	it('o ícone não muda o nome do link para quem usa leitor de tela', async () => {
		signIn(USER);
		await render(SiteNav);

		await expect.element(page.getByRole('link', { name: 'Provador', exact: true })).toBeVisible();
		await expect.element(page.getByRole('link', { name: 'Sua conta', exact: true })).toBeVisible();
	});

	it('marca o destino atual na barra', async () => {
		signIn(USER);
		state.pathname = '/provador';
		await render(SiteNav);

		const current = nav().querySelector('a[aria-current="page"]');
		expect(current?.textContent?.trim()).toBe('Provador');
		expect(style(current!).borderTopColor).not.toBe('rgba(0, 0, 0, 0)');
	});

	it('no computador, volta a ser uma lista de links no cabeçalho, sem ícones', async () => {
		signIn(USER);
		await page.viewport(1280, 800);
		await render(SiteNav);

		expect(style(nav()).position).toBe('static');
		expect(style(nav().querySelector('svg')!).display).toBe('none');
	});

	it('sem sessão, "Entrar" fica no cabeçalho e não vira barra', async () => {
		vi.stubGlobal('fetch', async () => new Response(null, { status: 401 }));
		await loadSession();
		vi.unstubAllGlobals();
		await render(SiteNav);

		expect(style(nav()).position).not.toBe('fixed');
		expect(nav().querySelector('svg')).toBeNull();
	});
});
