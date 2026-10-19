# Changelog

As mudanças de cada versão do VirtualFit ficam registradas aqui. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e as versões seguem o [Versionamento Semântico](https://semver.org/lang/pt-BR/) (veja o [ADR-0005](docs/adr/0005-versionamento-semantico-por-branch.md)).

## [0.2.0] - 2026-10-19

### Adicionado

- Frontend em SvelteKit (`frontend/`), mobile-first, com identidade visual própria: paleta Gruvbox, títulos em Bodoni Moda e a etiqueta de roupa como elemento de destaque.
- Página inicial explicando o fluxo do produto e página de cadastro, com validação no navegador, mensagens de erro em português, foco no primeiro erro e opção de mostrar a senha.
- Cliente HTTP tipado (`openapi-fetch`), com os tipos gerados a partir do OpenAPI do backend (`npm run api:sync`).
- A API informa a própria versão no OpenAPI (`/docs`) e no `GET /healthcheck/`.
- Workflow de CI do frontend: lint, checagem de tipos, build, testes (unidade e componentes no Chromium), auditoria, verificação do contrato da API e build da imagem.
- Serviço `web` no `docker compose`, com o nginx servindo o frontend e repassando `/api` para a API. É a entrada única em <http://localhost:8080>, com cabeçalhos de segurança, cache de arquivos estáticos e gzip.

### Alterado

- A versão do produto passa a ser única para o monorepo (`backend/pyproject.toml` e `frontend/package.json`).
- No compose, a API deixa de ser publicada no host e ganha um healthcheck. Ela confia no `X-Forwarded-For` definido pelo nginx, então o rate limiting usa o IP real do cliente e não aceita IP forjado. A documentação fica em `/api/docs`.

## [0.1.0] - 2026-10-19

Primeira versão da API, consolidando o trabalho até a reorganização em monorepo.

### Adicionado

- Cadastro de usuários (`POST /users/`):
  - senha com hash bcrypt, calculado fora do event loop;
  - e-mail e username únicos sem diferenciar maiúsculas, e o username preserva a grafia;
  - limite de 5 cadastros por minuto por IP.
- Serviço de tokens JWT (PyJWT) e configuração obrigatória de `SECRET_KEY`.
- Testes unitários e de integração com Postgres, incluindo as migrações.
- CI com Ruff, testes, `pip-audit` e build da imagem Docker.
- Documentação de deploy, débito técnico e decisões (ADRs 0001 a 0003).

### Segurança

- Valores das queries ocultos nos logs, e erros 422 sem ecoar a entrada (para não expor senhas).
- Postgres e API acessíveis apenas por `127.0.0.1` no compose, e credenciais no `.env`.

[0.2.0]: https://github.com/JVM3L0/DressMe/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/JVM3L0/DressMe/releases/tag/v0.1.0
