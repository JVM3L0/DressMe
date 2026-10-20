import { describe, expect, it } from 'vitest';

import { failureFromStatus, request } from './request.ts';

const respond = (status: number, data?: unknown) => async () => ({
	data,
	response: new Response(null, { status })
});

describe('failureFromStatus', () => {
	it.each([
		[401, 'unauthenticated'],
		[404, 'not_found'],
		[413, 'too_large'],
		[415, 'unsupported'],
		[422, 'invalid'],
		[429, 'rate_limited'],
		[500, 'unexpected'],
		[502, 'unexpected']
	])('%i -> %s', (status, kind) => {
		expect(failureFromStatus(status)).toBe(kind);
	});
});

describe('request', () => {
	it('devolve os dados quando a resposta é de sucesso', async () => {
		expect(await request(respond(200, { ok: 1 }))).toEqual({ kind: 'ok', data: { ok: 1 } });
	});

	it('trata o 204 (sem corpo) como sucesso', async () => {
		expect(await request(respond(204))).toEqual({ kind: 'ok', data: undefined });
	});

	it('traduz o status de erro', async () => {
		expect(await request(respond(413))).toEqual({ kind: 'too_large' });
	});

	it('avisa quando não há conexão', async () => {
		const result = await request(async () => {
			throw new TypeError('Failed to fetch');
		});

		expect(result).toEqual({ kind: 'network_error' });
	});
});
