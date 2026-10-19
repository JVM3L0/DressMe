# ADR-0004: Frontend estático, com a API na mesma origem em `/api`

- **Status:** Aceito
- **Data:** 2026-10-19

## Contexto

O [ADR-0002](0002-monorepo-e-sveltekit.md) definiu SvelteKit como frontend. Faltava decidir:

- **como ele roda em produção:** um servidor Node com SSR ou arquivos estáticos;
- **como o navegador fala com a API:** outra origem com CORS, ou a mesma origem.

O [ADR-0003](0003-armazenamento-local-de-imagens-com-nginx.md) já coloca o nginx como porta de entrada, com o front em `/` e o FastAPI em `/api/`.

## Decisão

1. **Build estático** com `@sveltejs/adapter-static`:
   - as páginas são pré-renderizadas em HTML (`prerender = true` no layout raiz), o que deixa a primeira visita rápida, como pede o RNF01;
   - os dados da API são buscados no navegador;
   - rotas não pré-renderizadas caem no `200.html` (modo SPA).

   Não há servidor Node em produção: o nginx serve a pasta `build/`.
2. **API na mesma origem, sob `/api`.** O prefixo é removido antes de chegar ao FastAPI, então as rotas do backend continuam como `/users/`:
   - em desenvolvimento, o proxy do Vite faz isso (`vite.config.ts`);
   - em produção, o nginx fará o mesmo.

   Por ser a mesma origem, **não é preciso configurar CORS**.
3. **Contrato tipado:**
   - o backend exporta o OpenAPI (`backend/scripts/export_openapi.py`);
   - o frontend gera `src/lib/api/schema.ts` com `openapi-typescript` e usa `openapi-fetch`;
   - os dois arquivos são versionados, e o CI falha se estiverem desatualizados em relação ao backend.

## Consequências

- Deploy simples e barato: arquivos estáticos no mesmo nginx que vai servir as imagens.
- Sem SSR por requisição. Páginas que precisarem de dados no HTML inicial (SEO de conteúdo dinâmico) exigiriam trocar o adapter. Para a PoC, isso não é necessário.
- Quando a autenticação existir, o token será enviado pelo navegador para a mesma origem. Os cookies podem ser `SameSite=Strict`, sem CORS.
- Mudanças no schema da API exigem rodar `npm run api:sync` no frontend e versionar o resultado.
