/**
 * Content Security Policy das páginas (DT-09). O SvelteKit a escreve num
 * <meta> de cada página pré-renderizada, junto com os hashes dos próprios
 * scripts inline. Tudo vem da mesma origem: a API em /api, as fontes
 * auto-hospedadas e o script de tema (static/theme-init.js). As diretivas que
 * não funcionam em <meta> (frame-ancestors) ficam no nginx.
 */

import type { sveltekit } from '@sveltejs/kit/vite';

// Tipo das diretivas aceitas pelo plugin do SvelteKit
type KitOptions = NonNullable<Parameters<typeof sveltekit>[0]>;
type CspDirectives = NonNullable<NonNullable<KitOptions['csp']>['directives']>;

/**
 * Hash do atributo `style` do `#svelte-announcer`, a região que o SvelteKit
 * usa para anunciar a troca de página a leitores de tela. `src/csp.spec.ts`
 * falha se uma atualização do SvelteKit mudar esse estilo; se isso acontecer,
 * atualize o hash. Até lá, `app.css` mantém a região oculta.
 */
export const ANNOUNCER_STYLE_HASH: `sha256-${string}` =
	'sha256-S8qMpvofolR8Mpjy4kQvEm7m1q8clzU4dfDH0AmvZjo=';

export const CSP_DIRECTIVES = {
	'default-src': ['self'],
	'script-src': ['self'],
	// 'unsafe-hashes' libera só atributos `style` com o hash listado
	'style-src': ['self', 'unsafe-hashes', ANNOUNCER_STYLE_HASH],
	'img-src': ['self', 'data:', 'blob:'],
	'font-src': ['self'],
	'connect-src': ['self'],
	'object-src': ['none'],
	'base-uri': ['self'],
	'form-action': ['self']
} satisfies CspDirectives;
