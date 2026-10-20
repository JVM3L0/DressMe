/**
 * Teste de ponta a ponta (DT-13): o fluxo principal num navegador real, contra
 * o ambiente completo (nginx, API e banco), como em produção.
 *
 *   docker compose up -d --build --wait   # na raiz
 *   npm run e2e                           # BASE_URL=http://localhost:8080 por padrão
 *
 * Cria um usuário novo a cada execução (a API ainda não exclui contas) e
 * apaga as fotos e peças que enviou. Falha com qualquer erro de JavaScript, de
 * CSP ou de rede inesperado no console, que os testes de unidade e de
 * componente (com a API simulada) não enxergam.
 */
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

import { chromium } from 'playwright';

const BASE_URL = (process.env.BASE_URL ?? 'http://localhost:8080').replace(/\/$/, '');
const fixture = (name) => fileURLToPath(new URL(`./fixtures/${name}`, import.meta.url));
const ARTIFACTS = fileURLToPath(new URL('./artifacts/', import.meta.url));

const unique = Date.now().toString(36);
const USERNAME = `e2e${unique}`;
const EMAIL = `${USERNAME}@example.com`;
const PASSWORD = 'roupa-de-domingo-azul';

// Respostas de erro que o fluxo provoca de propósito: sessão ausente (401) e
// dados recusados (422). O navegador as registra no console como erro de rede.
const EXPECTED_CONSOLE = /status of (401|422)\b/;

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
// A área de transferência só funciona em contexto seguro: localhost é, e o
// navegador pede permissão de leitura para o teste conferir o que foi copiado
await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: BASE_URL });
const page = await context.newPage();
page.setDefaultTimeout(15_000);

const consoleProblems = [];
page.on('console', (message) => {
	if (message.type() === 'error' && !EXPECTED_CONSOLE.test(message.text())) {
		consoleProblems.push(message.text());
	}
});
page.on('pageerror', (error) => consoleProblems.push(`pageerror: ${error.message}`));

async function step(name, run) {
	await run();
	console.log(`✓ ${name}`);
}

/** O link do cabeçalho só aparece depois que a página hidratou e consultou a sessão */
const ready = async () => {
	await page.waitForLoadState('networkidle');
	await page.locator('.site-nav').waitFor();
};

const imageLoaded = (selector) =>
	page.waitForFunction((sel) => {
		const image = document.querySelector(sel);
		return image && image.complete && image.naturalWidth > 0;
	}, selector);

try {
	await step('a página inicial abre, com a CSP e o tema', async () => {
		await page.goto(`${BASE_URL}/`);
		await ready();
		await page.getByRole('link', { name: 'Entrar' }).first().waitFor();
		const csp = await page
			.locator('meta[http-equiv="content-security-policy"]')
			.getAttribute('content');
		assert.match(csp, /script-src 'self'/);
	});

	await step('o cadastro recusa uma senha comum (política da API)', async () => {
		await page.goto(`${BASE_URL}/cadastro`);
		await ready();
		await page.getByLabel('Nome de usuário').fill(USERNAME);
		await page.getByLabel('E-mail').fill(EMAIL);
		await page.getByLabel('Senha', { exact: true }).fill('senha123');
		await page.getByRole('button', { name: 'Criar conta' }).click();
		await page.getByText('Essa senha é muito comum').waitFor();
	});

	await step('o cadastro cria a conta', async () => {
		await page.getByLabel('Senha', { exact: true }).fill(PASSWORD);
		await page.getByRole('button', { name: 'Criar conta' }).click();
		await page.getByRole('heading', { name: 'Conta criada' }).waitFor();
	});

	await step('o login recusa a senha errada e aceita a certa, com cookie HttpOnly', async () => {
		await page.getByRole('link', { name: 'Entrar' }).last().click();
		await page.waitForURL('**/entrar');
		await page.getByLabel('E-mail').fill(EMAIL);
		await page.getByLabel('Senha', { exact: true }).fill('senha-errada-123');
		await page.getByRole('button', { name: 'Entrar', exact: true }).click();
		await page.getByText('E-mail ou senha incorretos').waitFor();

		await page.getByLabel('Senha', { exact: true }).fill(PASSWORD);
		await page.getByRole('button', { name: 'Entrar', exact: true }).click();
		await page.waitForURL('**/conta');
		await page.getByRole('heading', { name: USERNAME }).waitFor();

		const cookie = (await context.cookies()).find((item) => item.name === 'virtualfit_session');
		assert.ok(cookie?.httpOnly, 'o cookie da sessão deve ser HttpOnly');
		assert.equal(cookie.sameSite, 'Strict');
		assert.equal(
			await page.evaluate(() => document.cookie.includes('virtualfit_session')),
			false,
			'o JavaScript da página não pode ler o cookie'
		);
	});

	let photoId;
	await step('envia uma foto: a miniatura aparece e a original sai sem EXIF', async () => {
		await page.getByRole('link', { name: 'Fotos' }).click();
		await page.getByText('ainda não enviou nenhuma foto').waitFor();
		await page.locator('input[type=file]').setInputFiles(fixture('photo-with-gps.jpg'));
		await page.getByAltText('Pré-visualização da imagem escolhida').waitFor();
		await page.getByRole('button', { name: 'Enviar foto' }).click();
		await page.getByText('Foto enviada.').waitFor();
		await imageLoaded('.card img');

		const thumbnail = await page.locator('.card img').getAttribute('src');
		assert.match(thumbnail, /^\/api\/photos\/[\w-]+\/thumbnail$/);
		photoId = thumbnail.split('/')[3];

		const full = await context.request.get(`${BASE_URL}/api/photos/${photoId}/image`);
		assert.equal(full.status(), 200);
		assert.equal(full.headers()['content-type'], 'image/jpeg');
		assert.match(full.headers()['cache-control'], /private/);
		assert.equal(full.headers()['x-accel-redirect'], undefined, 'o cabeçalho interno não vaza');
		const body = await full.body();
		// A foto original tinha EXIF com GPS; a entregue não tem metadado algum
		assert.equal(body.includes(Buffer.from('Exif\0\0')), false, 'o EXIF foi removido');
		assert.equal(body.includes(Buffer.from('Celular de Teste')), false);
	});

	await step('a imagem não é pública: sem sessão e direto no /_media/', async () => {
		const stranger = await browser.newContext();
		const noSession = await stranger.request.get(`${BASE_URL}/api/photos/${photoId}/image`);
		assert.equal(noSession.status(), 401);
		await stranger.close();

		// A pasta existe (a foto acabou de ser gravada nela): sem o `internal` do
		// nginx, o pedido daria 403 (pasta) em vez de 404
		const direct = await context.request.get(`${BASE_URL}/_media/photos/`);
		assert.equal(direct.status(), 404, '/_media/ deve ser interno ao nginx');
	});

	await step('adiciona peças e filtra por categoria', async () => {
		await page.getByRole('link', { name: 'Guarda-roupa' }).click();
		await page.getByText('guarda-roupa está vazio').waitFor();

		const add = async (file, category, name) => {
			await page.locator('input[type=file]').setInputFiles(fixture(file));
			await page.getByLabel('Categoria', { exact: true }).selectOption(category);
			await page.getByLabel('Nome (opcional)').fill(name);
			await page.getByRole('button', { name: 'Adicionar peça' }).click();
			await page.getByText('Peça adicionada.').waitFor();
		};
		await add('shirt.png', 'top', 'Camisa azul');
		await add('pants.png', 'bottom', 'Calça preta');
		await page.waitForFunction(() => document.querySelectorAll('.card').length === 2);

		await page.getByRole('button', { name: /^Parte de baixo/ }).click();
		assert.equal(await page.locator('.card').count(), 1);
		await page.getByRole('button', { name: /^Tudo/ }).click();
		await imageLoaded('.card img');
	});

	await step('o provador monta o conjunto e copia foto, roupas e texto de verdade', async () => {
		await page.getByRole('link', { name: 'Provador' }).click();
		await page.getByRole('button', { name: 'Escolher Parte de cima' }).waitFor();
		const pick = async (slot, piece) => {
			await page.getByRole('button', { name: `Escolher ${slot}` }).click();
			await page.getByRole('dialog').getByRole('button', { name: piece }).click();
		};
		await pick('Parte de baixo', 'Calça preta');
		await pick('Parte de cima', 'Camisa azul');

		const prompt = await page.getByLabel('Texto para colar na IA').inputValue();
		assert.match(prompt, /1\. Top: "Camisa azul"/);
		assert.match(prompt, /2\. Bottom: "Calça preta"/);

		// Botões padronizados: em cada grupo, todos têm a mesma largura e altura (por linha),
		// e nenhum é menor que o alvo de toque de 44px
		const groups = await page.locator('.button-group').evaluateAll((items) =>
			items.map((group) =>
				[...group.querySelectorAll('.button')]
					// Só os visíveis: a janela de escolha da peça, fechada, também tem botões
					.filter((button) => button.getClientRects().length > 0)
					.map((button) => {
						const box = button.getBoundingClientRect();
						return {
							row: Math.round(box.y),
							width: Math.round(box.width),
							height: Math.round(box.height)
						};
					})
			)
		);
		assert.ok(groups.length >= 3, 'o provador tem grupos de botões');
		for (const buttons of groups) {
			for (const button of buttons) assert.ok(button.height >= 44, 'alvo de toque de 44px');
			const rows = Map.groupBy(buttons, (button) => button.row);
			for (const row of rows.values()) {
				assert.equal(
					new Set(row.map((b) => b.width)).size,
					1,
					`larguras iguais: ${JSON.stringify(row)}`
				);
				assert.equal(
					new Set(row.map((b) => b.height)).size,
					1,
					`alturas iguais: ${JSON.stringify(row)}`
				);
			}
		}

		const clipboardImage = () =>
			page.evaluate(async () => {
				const [item] = await navigator.clipboard.read();
				const blob = await item.getType('image/png');
				const bitmap = await createImageBitmap(blob);
				const signature = [...new Uint8Array(await blob.slice(0, 8).arrayBuffer())];
				return { size: [bitmap.width, bitmap.height], signature };
			});
		const PNG_SIGNATURE = [137, 80, 78, 71, 13, 10, 26, 10];

		await page.getByRole('button', { name: 'Copiar foto' }).click();
		await page.getByText('Foto copiada').waitFor();
		const photo = await clipboardImage();
		assert.deepEqual(
			photo.signature,
			PNG_SIGNATURE,
			'a foto vai como PNG para a área de transferência'
		);
		assert.deepEqual(photo.size, [600, 400], 'a foto sai girada e sem o EXIF');

		await page.getByRole('button', { name: 'Copiar roupas' }).click();
		await page.getByText('Roupas copiadas').waitFor();
		const clothes = await clipboardImage();
		assert.deepEqual(clothes.signature, PNG_SIGNATURE);
		assert.deepEqual(clothes.size, [1024, 512], 'duas peças: duas células quadradas lado a lado');

		await page.getByRole('button', { name: 'Copiar texto' }).click();
		await page.getByText('Texto copiado').waitFor();
		assert.equal(await page.evaluate(() => navigator.clipboard.readText()), prompt);
	});

	await step('salva o conjunto, que continua lá depois de recarregar, e o exclui', async () => {
		await page.getByLabel('Nome do conjunto').fill('Look e2e');
		await page.getByRole('button', { name: 'Salvar conjunto' }).click();
		await page.getByText('Conjunto salvo.').waitFor();

		await page.reload();
		await ready();
		await page.getByRole('button', { name: 'Usar o conjunto Look e2e' }).click();
		await page.getByRole('button', { name: 'Trocar Parte de cima: Camisa azul' }).waitFor();
		await page.getByRole('button', { name: 'Trocar Parte de baixo: Calça preta' }).waitFor();

		await page.getByRole('button', { name: 'Excluir o conjunto Look e2e' }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		await page.getByText('Conjunto excluído.').waitFor();
	});

	await step('exclui as peças', async () => {
		await page.getByRole('link', { name: 'Guarda-roupa' }).click();
		await imageLoaded('.card img');
		await page.getByRole('button', { name: 'Excluir Camisa azul' }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		await page.getByText('Peça excluída.').waitFor();
		await page.getByRole('button', { name: 'Excluir Calça preta' }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		await page.getByText('guarda-roupa está vazio').waitFor();
	});

	await step('exclui a foto', async () => {
		await page.getByRole('link', { name: 'Fotos' }).click();
		await page.getByRole('button', { name: 'Excluir foto' }).click();
		await page.getByRole('button', { name: 'Excluir mesmo' }).click();
		await page.getByText('ainda não enviou nenhuma foto').waitFor();
		const gone = await context.request.get(`${BASE_URL}/api/photos/${photoId}/image`);
		assert.equal(gone.status(), 404);
	});

	await step(
		'no celular o menu é uma barra fixa embaixo, e no computador fica no cabeçalho',
		async () => {
			await page.goto(`${BASE_URL}/conta`);
			await ready();
			const bar = page.locator('.site-nav.bar');
			await bar.waitFor();
			const viewport = page.viewportSize();
			const box = await bar.boundingBox();
			assert.equal(
				Math.round(box.y + box.height),
				viewport.height,
				'a barra fica colada embaixo da tela'
			);
			assert.equal(await bar.evaluate((el) => getComputedStyle(el).position), 'fixed');
			const links = await bar.locator('a').evaluateAll((items) =>
				items.map((item) => ({
					...item.getBoundingClientRect().toJSON(),
					name: item.textContent.trim()
				}))
			);
			assert.deepEqual(
				links.map((link) => link.name),
				['Fotos', 'Guarda-roupa', 'Provador', 'Sua conta']
			);
			assert.ok(
				links.every((link) => link.height >= 44 && link.width >= 44),
				'alvos de toque de 44px'
			);

			// O rodapé fica acima da barra quando a página é rolada até o fim
			await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
			const footer = await page.locator('.site-footer').boundingBox();
			assert.ok(footer.y + footer.height <= box.y + 1, 'a barra não cobre o rodapé');

			await page.setViewportSize({ width: 1280, height: 800 });
			assert.equal(await bar.evaluate((el) => getComputedStyle(el).position), 'static');
			assert.ok((await bar.boundingBox()).y < 100, 'no computador, o menu fica no cabeçalho');
			await page.setViewportSize({ width: 390, height: 844 });
		}
	);

	await step('o tema escuro vale após recarregar, e a sessão continua', async () => {
		await page.getByRole('button', { name: 'Usar tema escuro' }).click();
		await page.reload();
		await ready();
		assert.equal(await page.evaluate(() => document.documentElement.dataset.theme), 'dark');
		await page.getByRole('link', { name: 'Sua conta' }).waitFor();
	});

	await step('sair encerra a sessão, e as páginas protegidas voltam ao login', async () => {
		await page.getByRole('link', { name: 'Sua conta' }).click();
		await page.getByRole('button', { name: 'Sair' }).click();
		await page.waitForURL(`${BASE_URL}/`);
		await page.goto(`${BASE_URL}/fotos`);
		await page.waitForURL('**/entrar');
	});

	assert.deepEqual(consoleProblems, [], 'o console não pode ter erros (JavaScript, CSP ou rede)');
	console.log('\nTudo certo.');
} catch (error) {
	await mkdir(ARTIFACTS, { recursive: true });
	await page.screenshot({ path: `${ARTIFACTS}failure.png`, fullPage: true }).catch(() => {});
	console.error('\n✗ Falhou:', error.message);
	if (consoleProblems.length) console.error('Console:', consoleProblems);
	process.exitCode = 1;
} finally {
	await browser.close();
}
