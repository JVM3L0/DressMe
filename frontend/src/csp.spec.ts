import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

import { ANNOUNCER_STYLE_HASH, CSP_DIRECTIVES } from '../csp.config.ts';

const ROOT_COMPONENT = 'node_modules/@sveltejs/kit/src/runtime/components/root.svelte';

describe('CSP', () => {
	it('libera exatamente o estilo inline do anunciador de rotas do SvelteKit', () => {
		const source = readFileSync(ROOT_COMPONENT, 'utf8');
		const announcer = source.slice(source.indexOf('id="svelte-announcer"'));
		const style = announcer.match(/style="([^"]+)"/)?.[1];

		expect(style).toBeDefined();
		const hash = createHash('sha256').update(style!).digest('base64');
		expect(`sha256-${hash}`).toBe(ANNOUNCER_STYLE_HASH);
	});

	it('não libera scripts nem estilos inline arbitrários', () => {
		const sources: string[] = Object.values(CSP_DIRECTIVES).flat();
		const inline = sources.filter((source) => ['unsafe-inline', 'unsafe-eval'].includes(source));

		expect(inline).toEqual([]);
		expect(CSP_DIRECTIVES['script-src']).toEqual(['self']);
	});
});
