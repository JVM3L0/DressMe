import { defineConfig } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';

import { CSP_DIRECTIVES } from './csp.config.ts';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			// Páginas pré-renderizadas; rotas não pré-renderizadas caem no fallback
			// (SPA). O nginx serve o resultado como arquivos estáticos (ADR-0004).
			adapter: adapter({ fallback: '200.html' }),
			// CSP em <meta>, com os hashes dos scripts inline do SvelteKit (csp.config.ts)
			csp: { mode: 'hash', directives: CSP_DIRECTIVES }
		})
	],
	server: {
		// Mesmo contrato do nginx em produção: /api/* vai para o FastAPI sem o
		// prefixo, mantendo front e API na mesma origem (sem CORS)
		proxy: {
			'/api': {
				target: process.env.API_PROXY_TARGET ?? 'http://localhost:8000',
				rewrite: (path) => path.replace(/^\/api/, '')
			}
		}
	},
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'client',
					browser: {
						enabled: true,
						provider: playwright(),
						instances: [{ browser: 'chromium', headless: true }]
					},
					include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
					exclude: ['src/lib/server/**']
				}
			},

			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			}
		]
	}
});
