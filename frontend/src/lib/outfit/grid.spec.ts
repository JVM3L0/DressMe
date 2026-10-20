import { describe, expect, it } from 'vitest';

import { cellRect, fitInCell, gridFor } from './grid.ts';

describe('gridFor', () => {
	it.each([
		[1, 1, 1],
		[2, 2, 1],
		[3, 2, 2],
		[4, 2, 2],
		[5, 3, 2],
		[6, 3, 2],
		[7, 3, 3],
		[8, 3, 3]
	])('%i peças -> %i colunas x %i linhas', (count, columns, rows) => {
		expect(gridFor(count)).toEqual({ columns, rows });
	});

	it('sempre tem lugar para todas as peças, sem sobrar linha', () => {
		for (let count = 1; count <= 8; count++) {
			const { columns, rows } = gridFor(count);
			expect(columns * rows).toBeGreaterThanOrEqual(count);
			// Sem linha sobrando: a última linha tem ao menos uma peça
			expect(columns * (rows - 1)).toBeLessThan(count);
		}
	});

	it('trata zero como uma célula, para não gerar uma imagem vazia', () => {
		expect(gridFor(0)).toEqual({ columns: 1, rows: 1 });
	});
});

describe('cellRect', () => {
	it('numera da esquerda para a direita, de cima para baixo', () => {
		expect(cellRect(0, 3, 100)).toEqual({ x: 0, y: 0, width: 100, height: 100 });
		expect(cellRect(2, 3, 100)).toEqual({ x: 200, y: 0, width: 100, height: 100 });
		expect(cellRect(3, 3, 100)).toEqual({ x: 0, y: 100, width: 100, height: 100 });
		expect(cellRect(4, 3, 100)).toEqual({ x: 100, y: 100, width: 100, height: 100 });
	});
});

describe('fitInCell', () => {
	const cell = { x: 512, y: 0, width: 512, height: 512 };

	it('cabe uma imagem larga pela largura, centralizada na vertical', () => {
		expect(fitInCell(1000, 500, cell, 24)).toEqual({ x: 536, y: 140, width: 464, height: 232 });
	});

	it('cabe uma imagem alta pela altura, centralizada na horizontal', () => {
		expect(fitInCell(500, 1000, cell, 24)).toEqual({ x: 652, y: 24, width: 232, height: 464 });
	});

	it('amplia uma imagem pequena até preencher o espaço (peças recortadas pequenas)', () => {
		const target = fitInCell(100, 100, cell, 24);

		expect(target).toEqual({ x: 536, y: 24, width: 464, height: 464 });
	});

	it('mantém a proporção e fica dentro da margem', () => {
		const target = fitInCell(333, 777, cell, 24);

		expect(target.width / target.height).toBeCloseTo(333 / 777, 1);
		expect(target.x).toBeGreaterThanOrEqual(cell.x + 24);
		expect(target.y).toBeGreaterThanOrEqual(cell.y + 24);
		expect(target.x + target.width).toBeLessThanOrEqual(cell.x + cell.width - 24);
		expect(target.y + target.height).toBeLessThanOrEqual(cell.y + cell.height - 24);
	});
});
