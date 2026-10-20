import { api } from '#lib/api/client.ts';
import type { components } from '#lib/api/schema.ts';
import { request, type Result } from '#lib/media/request.ts';

import type { GarmentCategory } from './categories.ts';

export type Garment = components['schemas']['GarmentPublic'];

export interface NewGarment {
	file: File;
	category: GarmentCategory;
	name?: string;
}

export const garmentImageUrl = (uid: string) => `/api/garments/${uid}/image`;

/** Miniatura (até 480 px) para as grades; a imagem inteira é para o provador */
export const garmentThumbnailUrl = (uid: string) => `/api/garments/${uid}/thumbnail`;

export const listGarments = (): Promise<Result<Garment[]>> => request(() => api.GET('/garments/'));

export function addGarment({ file, category, name }: NewGarment): Promise<Result<Garment>> {
	return request(() =>
		api.POST('/garments/', {
			body: { file: '', category },
			bodySerializer: () => {
				const form = new FormData();
				form.append('file', file);
				form.append('category', category);
				if (name?.trim()) form.append('name', name.trim());
				return form;
			}
		})
	);
}

export const deleteGarment = (uid: string): Promise<Result<undefined>> =>
	request(() => api.DELETE('/garments/{uid}', { params: { path: { uid } } }));
