/** Resultado de uma chamada à API, sem exceções: a tela só decide o que mostrar */

export type FailureKind =
	| 'unauthenticated'
	| 'not_found'
	| 'too_large'
	| 'unsupported'
	| 'invalid'
	| 'rate_limited'
	| 'network_error'
	| 'unexpected';

export type Result<T> = { kind: 'ok'; data: T } | { kind: FailureKind };

export const FAILURE_MESSAGES: Record<FailureKind, string> = {
	unauthenticated: 'Sua sessão expirou. Entre de novo.',
	not_found: 'Esse item não existe mais.',
	too_large: 'A imagem passa de 10 MB. Escolha uma menor.',
	unsupported: 'Envie uma imagem JPEG ou PNG.',
	invalid: 'Não foi possível enviar. Confira os dados e tente de novo.',
	rate_limited: 'Muitos envios seguidos. Aguarde um minuto e tente de novo.',
	network_error: 'Não foi possível falar com o servidor. Verifique sua conexão e tente de novo.',
	unexpected: 'Não foi possível concluir agora. Tente de novo em instantes.'
};

export function failureFromStatus(status: number): FailureKind {
	switch (status) {
		case 401:
			return 'unauthenticated';
		case 404:
			return 'not_found';
		case 413:
			return 'too_large';
		case 415:
			return 'unsupported';
		case 422:
			return 'invalid';
		case 429:
			return 'rate_limited';
		default:
			return 'unexpected';
	}
}

/** Executa a chamada e traduz a resposta (ou a falta de conexão) em `Result` */
export async function request<T>(
	run: () => Promise<{ data?: T; response: Response }>
): Promise<Result<T>> {
	try {
		const { data, response } = await run();
		if (response.ok) return { kind: 'ok', data: data as T };
		return { kind: failureFromStatus(response.status) };
	} catch {
		return { kind: 'network_error' };
	}
}
