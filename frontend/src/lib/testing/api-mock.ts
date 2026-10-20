/** Apoio aos testes de página: simula a API por rota (`"GET /api/photos/"`) */

import { vi } from 'vitest';

export const json = (status: number, body?: unknown) =>
	new Response(body === undefined ? null : JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});

export type Handler = (request: Request) => Response | Promise<Response>;

export function mockApi(routes: Record<string, Handler>) {
	const calls: Request[] = [];
	const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
		const request = (input as Request).clone();
		calls.push(request);
		const key = `${request.method} ${new URL(request.url).pathname}`;
		const handler = routes[key];
		if (!handler) throw new Error(`Rota sem simulação: ${key}`);
		return handler(request);
	});
	vi.stubGlobal('fetch', fetchMock);
	return {
		/** Chamadas feitas a uma rota, na ordem */
		to: (key: string) =>
			calls.filter((call) => `${call.method} ${new URL(call.url).pathname}` === key),
		all: calls
	};
}

export const USER = {
	uid: '00000000-0000-0000-0000-000000000001',
	username: 'joao',
	email: 'joao@example.com',
	created_at: '2026-10-19T12:00:00Z'
};

export const imageFile = (name = 'foto.jpg', type = 'image/jpeg', size = 2048) =>
	new File([new Uint8Array(size)], name, { type });
