# Frontend

SvelteKit (Svelte 5, TypeScript), gerado como site estático. Veja o [README principal](../README.md) para rodar o projeto inteiro, e o [ADR-0004](../docs/adr/0004-frontend-estatico-com-api-em-api.md) para as decisões de build e de integração com a API.

```bash
npm install
npm run dev          # http://localhost:5173 (proxy de /api para http://localhost:8000)
npm run check        # tipos (svelte-check)
npm run lint         # Prettier + ESLint
npm test             # Vitest: unidade (Node) e componentes (Chromium)
npm run build        # gera build/ (HTML pré-renderizado + fallback 200.html)
npm run api:sync     # regenera src/lib/api/openapi.json e schema.ts a partir do backend
```

## Estrutura

```
src/
├── app.css                # tokens de design (paleta Gruvbox, tipografia, espaços)
├── lib/
│   ├── api/               # cliente tipado, schema gerado e tradução de erros da API
│   ├── components/        # componentes reutilizáveis (TextField, HangTag, ApiStatus)
│   └── signup/            # regras de validação e envio do cadastro
└── routes/                # páginas (/ e /cadastro)
```

## Convenções

- **Imports internos** usam `#lib/...` com a extensão explícita (`#lib/api/client.ts`), como pede o SvelteKit 3.
- **Regras do domínio fora dos componentes:** a validação e o envio ficam em `src/lib/signup/` e são testados sem interface. A página só decide o que mostrar.
- **Mensagens** em português, na voz da interface: dizem o que aconteceu e como resolver.
- **Acessibilidade (WCAG 2.1 AA):**
  - todo campo tem rótulo, e os erros ficam ligados ao campo por `aria-describedby`;
  - ao enviar com erro, o foco vai para o primeiro campo inválido;
  - os contrastes da paleta são verificados.
- **Arquivos gerados** (`src/lib/api/openapi.json` e `schema.ts`) não são editados à mão.
- **`overrides` do `openapi-typescript`:** o `package.json` força o uso do TypeScript do projeto, porque a versão 7 do gerador declara suporte só ao TypeScript 5. O gerador funciona com o 6, e o CI verifica o resultado.

## Testes de componente

Os testes `*.svelte.spec.ts` rodam no Chromium, via Playwright. Na primeira vez:

```bash
npx playwright install chromium
sudo npx playwright install-deps chromium   # bibliotecas do sistema (Linux/WSL)
```

Sem as bibliotecas do sistema, dá para rodar os testes dentro da imagem oficial do Playwright:

```bash
docker run --rm --ipc=host --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$PWD":/work -w /work mcr.microsoft.com/playwright:v1.64.1-noble npx vitest run
```
