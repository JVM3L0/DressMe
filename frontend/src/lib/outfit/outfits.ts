import { api } from '#lib/api/client.ts';
import type { components } from '#lib/api/schema.ts';
import { FAILURE_MESSAGES, request, type FailureKind, type Result } from '#lib/media/request.ts';

export type Outfit = components['schemas']['OutfitPublic'];

export const listOutfits = (): Promise<Result<Outfit[]>> => request(() => api.GET('/outfits/'));

export const saveOutfit = (name: string, garmentIds: string[]): Promise<Result<Outfit>> =>
	request(() => api.POST('/outfits/', { body: { name: name.trim(), garment_ids: garmentIds } }));

export const updateOutfit = (
	uid: string,
	name: string,
	garmentIds: string[]
): Promise<Result<Outfit>> =>
	request(() =>
		api.PUT('/outfits/{uid}', {
			params: { path: { uid } },
			body: { name: name.trim(), garment_ids: garmentIds }
		})
	);

export const deleteOutfit = (uid: string): Promise<Result<undefined>> =>
	request(() => api.DELETE('/outfits/{uid}', { params: { path: { uid } } }));

/** Mensagens dos conjuntos: o 422 aqui quase sempre é uma peça que sumiu do guarda-roupa */
export const outfitFailureMessage = (kind: FailureKind): string =>
	kind === 'invalid'
		? 'Alguma peça do conjunto não está mais no guarda-roupa. Atualize a página e tente de novo.'
		: FAILURE_MESSAGES[kind];

export const OUTFIT_NAME_MAX = 60;
