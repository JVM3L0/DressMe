/**
 * Sessão do usuário no navegador. O token fica num cookie `HttpOnly` que o
 * JavaScript não lê (ADR-0006), então a sessão é descoberta perguntando à
 * API (`GET /users/me`). O estado é compartilhado por todas as páginas.
 */

import { api } from '#lib/api/client.ts';
import type { components } from '#lib/api/schema.ts';

export type CurrentUser = components['schemas']['UserPublic'];

export type Session =
	{ status: 'unknown' } | { status: 'anonymous' } | { status: 'authenticated'; user: CurrentUser };

let current: Session = $state({ status: 'unknown' });

export const session = {
	get current(): Session {
		return current;
	}
};

export function signIn(user: CurrentUser): void {
	current = { status: 'authenticated', user };
}

/** Consulta a API. Sem resposta (rede, API fora), a sessão fica como anônima */
export async function loadSession(): Promise<Session> {
	try {
		const { data } = await api.GET('/users/me');
		current = data ? { status: 'authenticated', user: data } : { status: 'anonymous' };
	} catch {
		current = { status: 'anonymous' };
	}
	return current;
}

/** Encerra a sessão. Retorna `false` se a API não confirmou (o cookie continua) */
export async function signOut(): Promise<boolean> {
	try {
		const { response } = await api.POST('/auth/logout');
		if (!response.ok) return false;
	} catch {
		return false;
	}
	current = { status: 'anonymous' };
	return true;
}
