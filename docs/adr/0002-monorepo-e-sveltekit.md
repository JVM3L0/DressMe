# ADR-0002: Monorepo com frontend em SvelteKit

- **Status:** Aceito
- **Data:** 2026-10-19

## Contexto

O VirtualFit precisa de um frontend mobile-first que também funcione no desktop (RNF04 e RNF05), com acesso à câmera (RF04), compartilhamento de imagens (RF12) e carregamento inicial em menos de 3 s (RNF01). No futuro, ele também terá assinatura paga (RF10).

O projeto tem um único desenvolvedor, e as mudanças costumam envolver API e tela ao mesmo tempo.

## Decisão

1. **Um repositório só (monorepo)** para backend e frontend:
   ```
   backend/    # API FastAPI (hoje, a raiz do repositório)
   frontend/   # SvelteKit
   docs/
   ```
   Cada parte tem o próprio workflow de CI, disparado por filtro de caminho (`paths:`).
2. **Frontend em SvelteKit, como aplicação web (PWA) mobile-first**, não um app nativo:
   - o Svelte é compilado, então os bundles são pequenos, o que ajuda no tempo de carregamento em celulares mais fracos;
   - o SvelteKit permite escolher SSR, pré-renderização ou renderização só no cliente para cada rota;
   - o navegador do celular já dá acesso à câmera (`<input capture>`) e ao menu de compartilhamento nativo;
   - na web, a assinatura pode usar Stripe ou PagSeguro direto, sem a comissão das lojas de apps.
3. **Tipos do frontend gerados a partir do OpenAPI do FastAPI** (`openapi-typescript`), para que o contrato da API não saia de sincronia com o front.

## Consequências

- Antes do primeiro deploy, o backend precisa ser movido para `backend/`. Isso afeta:
  - os caminhos de `Dockerfile`, `pyproject.toml`, `alembic.ini`, `settings.toml` e `scripts/`;
  - o CI, que precisa de filtros de caminho;
  - o pre-commit e o Ruff, que passam a valer só para `backend/`.
- Se notificações push, presença nas lojas ou recursos nativos se tornarem essenciais, o mesmo código pode ser empacotado com Capacitor, sem reescrita.
- Uma mudança de API e a tela correspondente entram no mesmo PR.
