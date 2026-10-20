/** Grade da imagem das roupas: quantas colunas e linhas para `count` peças */
export function gridFor(count: number): { columns: number; rows: number } {
	if (count <= 1) return { columns: 1, rows: 1 };
	if (count === 2) return { columns: 2, rows: 1 };
	if (count <= 4) return { columns: 2, rows: 2 };
	if (count <= 6) return { columns: 3, rows: 2 };
	// Até 8 peças: 4 acessórios, agasalho, parte de cima, parte de baixo e calçado
	return { columns: 3, rows: 3 };
}

export interface Rect {
	x: number;
	y: number;
	width: number;
	height: number;
}

/**
 * Onde desenhar uma imagem de `width` x `height` dentro de uma célula, sem
 * cortar nem ampliar além do espaço: ela cabe inteira (como `object-fit:
 * contain`), centralizada, com uma margem.
 */
export function fitInCell(width: number, height: number, cell: Rect, padding: number): Rect {
	const innerWidth = cell.width - 2 * padding;
	const innerHeight = cell.height - 2 * padding;
	const scale = Math.min(innerWidth / width, innerHeight / height);
	const drawWidth = Math.round(width * scale);
	const drawHeight = Math.round(height * scale);
	return {
		x: cell.x + Math.round((cell.width - drawWidth) / 2),
		y: cell.y + Math.round((cell.height - drawHeight) / 2),
		width: drawWidth,
		height: drawHeight
	};
}

/** Retângulo da célula `index` (da esquerda para a direita, de cima para baixo) */
export function cellRect(index: number, columns: number, size: number): Rect {
	return {
		x: (index % columns) * size,
		y: Math.floor(index / columns) * size,
		width: size,
		height: size
	};
}
