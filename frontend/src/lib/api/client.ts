import createClient from 'openapi-fetch';

import type { paths } from './schema.ts';

/**
 * Cliente HTTP tipado a partir do OpenAPI do backend (`npm run api:types`).
 *
 * A API fica na mesma origem, em `/api` (proxy do Vite em desenvolvimento e
 * nginx em produção). O `fetch` é resolvido a cada requisição, e não na
 * criação do cliente, para que os testes possam substituí-lo.
 */
export const api = createClient<paths>({
	baseUrl: '/api',
	fetch: (request) => globalThis.fetch(request)
});
