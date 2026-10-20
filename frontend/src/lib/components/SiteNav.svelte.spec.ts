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

beforeEach(() => {
	state.pathname = '/fotos';
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
