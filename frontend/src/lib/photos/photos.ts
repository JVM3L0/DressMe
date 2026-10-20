import { api } from '#lib/api/client.ts';
import type { components } from '#lib/api/schema.ts';
import { request, type Result } from '#lib/media/request.ts';

export type Photo = components['schemas']['PhotoPublic'];

/** A imagem só é entregue ao dono, com o cookie da sessão (mesma origem) */
export const photoImageUrl = (uid: string) => `/api/photos/${uid}/image`;

/** Miniatura (até 480 px) para as grades; a imagem inteira é para o provador */
export const photoThumbnailUrl = (uid: string) => `/api/photos/${uid}/thumbnail`;

export const listPhotos = (): Promise<Result<Photo[]>> => request(() => api.GET('/photos/'));

export function uploadPhoto(file: File): Promise<Result<Photo>> {
	return request(() =>
		api.POST('/photos/', {
			// O campo é só para o tipo: o corpo real é o FormData do serializador
			body: { file: '' },
			bodySerializer: () => {
				const form = new FormData();
				form.append('file', file);
				return form;
			}
		})
	);
}

export const deletePhoto = (uid: string): Promise<Result<undefined>> =>
	request(() => api.DELETE('/photos/{uid}', { params: { path: { uid } } }));
