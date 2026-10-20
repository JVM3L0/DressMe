# DressMe

Prova de conceito do **VirtualFit**, uma plataforma de prova virtual de roupas (escopo em [ADR-0001](docs/adr/0001-escopo-prova-de-conceito.md)). Monorepo com:

| Pasta | Conteúdo |
| --- | --- |
| [`backend/`](backend/) | API em **FastAPI** e **PostgreSQL**, com arquitetura em camadas (Clean Architecture / Hexagonal) |
| [`frontend/`](frontend/) | Web app em **SvelteKit**, mobile-first, gerado como site estático ([ADR-0004](docs/adr/0004-frontend-estatico-com-api-em-api.md)) |
| [`docs/`](docs/) | Decisões (ADRs), deploy e débito técnico |

Na raiz ficam o `docker-compose.yml`, o `.env` (compartilhado pelo compose e pelo backend), o [`CHANGELOG.md`](CHANGELOG.md), o CI e o pre-commit. **Os comandos `uv` rodam dentro de `backend/`, e os `npm`, dentro de `frontend/`.**

## Sumário

- [Stack](#stack)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Executando](#executando)
- [Frontend](#frontend)
- [Migrações](#migrações)
- [Testes](#testes)
- [Lint e formatação](#lint-e-formatação)
- [Endpoints](#endpoints)
- [Arquitetura](#arquitetura)
- [Contribuindo](#contribuindo)

## Stack

| Camada        | Tecnologia                                   |
| ------------- | -------------------------------------------- |
| Linguagem     | Python 3.13                                  |
| Web           | FastAPI + Uvicorn                            |
| Banco         | PostgreSQL 16                                |
| ORM           | SQLAlchemy 2 (async) + asyncpg               |
| Migrações     | Alembic                                      |
| Configuração  | Dynaconf (`.env` / variáveis de ambiente)    |
| Autenticação  | bcrypt (hash de senha), PyJWT (JWT)          |
| Rate limiting | slowapi                                      |
| Dependências  | [uv](https://docs.astral.sh/uv/)             |
| Lint/format   | [Ruff](https://docs.astral.sh/ruff/)         |

| Frontend      | Tecnologia                                   |
| ------------- | -------------------------------------------- |
| Framework     | SvelteKit 3 + Svelte 5 (TypeScript), `adapter-static` |
| Cliente da API | `openapi-fetch`, tipos gerados com `openapi-typescript` |
| Testes        | Vitest (Node e Chromium via Playwright)      |
| Lint/format   | ESLint + Prettier                            |
| Node          | 24 LTS (`frontend/.node-version`)            |

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (instala o Python 3.13 automaticamente, se necessário)
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- [Node.js 24 LTS](https://nodejs.org/), de preferência por um gerenciador de versões como o [fnm](https://github.com/Schniz/fnm), que lê o `frontend/.node-version`

## Configuração

1. Clone o repositório e instale as dependências:

   ```bash
   git clone git@github.com:JVM3L0/DressMe.git
   cd DressMe/backend
   uv sync                     # inclui as ferramentas de dev e testes
   uv run pre-commit install   # roda o Ruff antes de cada commit (vale para o repositório todo)
   cd ../frontend
   npm install
   ```

2. Na **raiz** do repositório, crie o `.env` a partir do exemplo e troque a senha (o `.env` é ignorado pelo Git):

   ```bash
   cp .env.example .env
   ```

   As credenciais `POSTGRES_*` são aplicadas quando o volume do banco é criado. Se você já tem um volume, use as credenciais com que ele foi criado.

### Variáveis de ambiente

| Variável       | Obrigatória | Padrão        | Descrição                                              |
| -------------- | ----------- | ------------- | ------------------------------------------------------ |
| `DATABASE_URL` | Sim         | —             | URL de conexão async (`postgresql+asyncpg://...`)      |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Sim (compose) | — | Credenciais do Postgres do `docker compose` |
| `POSTGRES_PORT` | Não        | `5432`        | Porta local do Postgres no compose                     |
| `MODE`         | Não         | `development` | Ambiente ativo do Dynaconf (`development`, `testing`, `production`) |
| `ECHO_SQL`     | Não         | `False`       | Exibe no log as queries SQL executadas                 |
| `TEST_DATABASE_URL` | Não    | `<DATABASE_URL>_test` | Banco dos testes de integração                 |
| `SECRET_KEY`   | Sim         | —             | Chave dos tokens JWT (mínimo 32 bytes; 48 para HS384, 64 para HS512) |
| `JWT_ALGORITHM` | Não        | `HS256`       | `HS256`, `HS384` ou `HS512`                            |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | `10080` | Validade da sessão (uma semana)                       |
| `AUTH_COOKIE_SECURE` | Não   | `true`        | Cookie da sessão só por HTTPS (`false` em `development` e `testing`) |
| `RATE_LIMIT_ENABLED` | Não   | `true`        | Liga o limite de requisições                           |
| `RATE_LIMIT_SIGNUP` | Não    | `5/minute`    | Limite de cadastros por IP                             |
| `RATE_LIMIT_LOGIN` | Não     | `10/minute`   | Limite de tentativas de login por IP                   |
| `RATE_LIMIT_UPLOAD` | Não    | `30/minute`   | Limite de envios de fotos e peças por IP               |
| `MEDIA_ROOT`   | Não         | `media`       | Pasta das imagens enviadas (no compose, o volume `media` em `/media`) |
| `MEDIA_ACCEL_REDIRECT` | Não | `false`       | `true` atrás do nginx: a API só autoriza e o nginx entrega o arquivo |
| `RATE_LIMIT_STORAGE_URI` | Não | `memory://` | Armazenamento dos contadores (`redis://...` com várias instâncias) |
| `FORWARDED_ALLOW_IPS` | Deploy | `127.0.0.1` | IPs de proxy confiáveis para o uvicorn (IP real do cliente) |
| `TEST_REDIS_URL` | Não | — | Redis para o teste de rate limiting compartilhado (pulado sem ele) |
| `WEB_PORT` | Não | `8080` | Porta local do nginx no `docker compose` |
| `WEB_HOST` | Não | `127.0.0.1` | Interface do nginx no compose (`0.0.0.0` para acessar pela rede local) |

A configuração usa o [Dynaconf](https://www.dynaconf.com/): valores por ambiente ficam em `settings.toml` e são sobrescritos pelo `.env` e pelas variáveis de ambiente. `DATABASE_URL` é validada na importação da aplicação: sem ela, a API e o Alembic não sobem.

## Executando

### Desenvolvimento local (as duas stacks)

Use três terminais, todos a partir da raiz do repositório:

```bash
# 1. Banco
docker compose up -d db

# 2. API, com recarga automática: http://localhost:8000 (documentação em /docs)
cd backend
uv run alembic upgrade head
uv run fastapi dev main.py

# 3. Frontend, com recarga automática: http://localhost:5173
cd frontend
npm run dev
```

Abra <http://localhost:5173>. O frontend chama a API em `/api`, e o Vite repassa para `http://localhost:8000` (para outro endereço, use `API_PROXY_TARGET`). O rodapé mostra "API x.y.z conectada" quando a integração está funcionando.

### Ambiente completo via Docker (igual a produção)

```bash
docker compose up --build    # na raiz
```

Abra <http://localhost:8080> (para mudar a porta, use `WEB_PORT`). A documentação da API fica em <http://localhost:8080/api/docs>.

| Serviço | Imagem | Papel |
| --- | --- | --- |
| `web` | `frontend/Dockerfile`: build do SvelteKit + `nginx:1.30-alpine` | Entrada única: serve o site estático em `/` e repassa `/api/*` para a API |
| `app` | `backend/Dockerfile` | API FastAPI. Roda as migrações ao iniciar, e só é acessível pelo nginx |
| `db` | `postgres:16-alpine` | Banco, publicado em `127.0.0.1:5432` para o desenvolvimento local |
| volume `media` | — | Fotos e peças enviadas. A API grava, o nginx lê (somente leitura) e entrega depois que a API autoriza |

A ordem de subida respeita os healthchecks: `db` → `app` → `web`. O nginx também define os cabeçalhos de segurança, o cache dos arquivos estáticos e o IP real do cliente para o rate limiting. A configuração fica em `frontend/nginx/`.

#### Testando no celular

1. No `.env`, defina `WEB_HOST=0.0.0.0` e rode `docker compose up -d web`.
2. No WSL2 com rede NAT (o padrão), repasse a porta do Windows para o WSL. No PowerShell, como administrador:
   ```powershell
   $wsl = (wsl hostname -I).Split(' ')[0]
   netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8080 connectaddress=$wsl connectport=8080
   New-NetFirewallRule -DisplayName "VirtualFit 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
   ```
   O IP do WSL muda quando o Windows reinicia: refaça o `portproxy` (ou use `networkingMode=mirrored` no `.wslconfig`).
3. No celular, na mesma rede, abra `http://<IP do computador>:8080` (no Windows: `ipconfig`).

O login funciona por HTTP só porque o compose roda em `MODE=development` (`AUTH_COOKIE_SECURE=false`). Não exponha esse modo fora da rede local.

Use esse modo para validar o sistema completo antes de abrir um PR. Para desenvolver, os servidores locais com recarga automática (acima) são mais rápidos. Se for alternar, rode `docker compose stop app web` antes de iniciar a API local, para liberar o banco só para ela.

## Frontend

Comandos, estrutura e convenções estão em [frontend/README.md](frontend/README.md). Os principais:

```bash
cd frontend
npm run check      # tipos
npm run lint       # Prettier + ESLint
npm test           # unidade e componentes (os de componente precisam do Chromium)
npm run build      # site estático em build/
npm run api:sync   # atualiza os tipos da API depois de mudar o backend
```

## Migrações

```bash
# Aplicar todas as migrações pendentes
uv run alembic upgrade head

# Gerar uma nova migração a partir dos models
uv run alembic revision --autogenerate -m "descrição da mudança"

# Reverter a última migração
uv run alembic downgrade -1
```

Ao criar um novo model ORM, exporte-o em `infrastructure/persistence/models/__init__.py` para que o autogenerate o detecte.

## Testes

```bash
# Todos os testes (unitários + integração)
uv run pytest

# Apenas unitários (não precisam de banco)
uv run pytest -m "not integration"

# Um arquivo ou teste específico
uv run pytest tests/unit/test_create_user.py
uv run pytest tests/unit/test_create_user.py::nome_do_teste
```

- `tests/unit/`: domínio, schemas, hasher, casos de uso e API, com fakes em memória (`tests/fakes.py`).
- `tests/integration/`: repositório, API completa e migrações no Postgres. Precisam do banco no ar (`docker compose up -d db`) e são **pulados** se ele não estiver disponível.

Os testes rodam no ambiente `testing` do Dynaconf. Os de integração usam o servidor do `DATABASE_URL` e criam automaticamente os bancos `<nome>_test` e `<nome>_test_migrations`; cada teste é desfeito ao final (nada fica gravado). Para usar outro banco, defina `TEST_DATABASE_URL`. No CI (`CI=true`), a falta do banco faz os testes falharem em vez de serem pulados.

## Lint e formatação

O projeto usa o [Ruff](https://docs.astral.sh/ruff/) para lint, ordenação de imports e formatação (configuração em `pyproject.toml`).

```bash
uv run ruff check .          # lint + imports
uv run ruff check --fix .    # aplica correções automáticas
uv run ruff format .         # formata o código
```

O hook do `pre-commit` executa o Ruff automaticamente em cada commit (`uv run pre-commit run --all-files` para rodar manualmente). Migrações geradas pelo Alembic também são formatadas pelo Ruff (`post_write_hooks` em `alembic.ini`).

## Endpoints

| Método | Rota            | Descrição                |
| ------ | --------------- | ------------------------ |
| GET    | `/healthcheck/` | Verifica se a API está no ar |
| POST   | `/users/`       | Cria um novo usuário (`201`; `409` se e-mail ou username já existir; `422` se os dados forem inválidos) |
| POST   | `/auth/login`   | Inicia a sessão com e-mail e senha (`200` com o cookie `virtualfit_session`; `401` se as credenciais estiverem erradas) |
| POST   | `/auth/logout`  | Encerra a sessão neste navegador (`204`) |
| GET    | `/users/me`     | Usuário da sessão atual (`401` sem sessão) |
| GET, POST | `/photos/` | Lista as fotos do usuário (mais recentes primeiro) e envia uma nova (`multipart/form-data`, campo `file`; `201`, `413` acima de 10 MB, `415` se não for JPEG ou PNG) |
| GET, DELETE | `/photos/{id}/image`, `/photos/{id}/thumbnail`, `/photos/{id}` | Imagem (até 2.048 px), miniatura (até 480 px) e exclusão (`404` se não existir ou for de outro usuário) |
| GET, POST | `/garments/` | Lista as peças (`?category=` filtra) e adiciona uma (`file`, `category` e `name` opcional) |
| GET, DELETE | `/garments/{id}/image`, `/garments/{id}/thumbnail`, `/garments/{id}` | Imagem, miniatura e exclusão |

| GET, POST | `/outfits/` | Lista os conjuntos do usuário e salva um novo (`name` e `garment_ids`; `422` se a composição não valer) |
| PUT, DELETE | `/outfits/{id}` | Troca o nome e as peças do conjunto, ou o exclui (as peças ficam) |

Categorias das peças: `top`, `outerwear`, `bottom`, `one_piece`, `footwear` e `accessory` ([ADR-0007](docs/adr/0007-categorias-de-pecas-e-entrega-das-imagens.md)). Um conjunto tem no máximo uma peça por categoria (até 4 acessórios), e uma peça única não combina com parte de cima ou de baixo ([ADR-0008](docs/adr/0008-conjuntos-e-ponte-para-ia-externa.md)). Todas as rotas de fotos, peças e conjuntos exigem sessão.

Regras do cadastro:

- **username:** 3 a 255 caracteres; letras, números, `_`, `.` ou `-`. A grafia é preservada.
- **email:** e-mail válido.
- **password:** mínimo de 8 caracteres e máximo de 72 bytes (limite do bcrypt). Senhas comuns (lista de vazamentos do NCSC) e senhas que contêm o username ou o e-mail são recusadas, sem regras de composição (NIST SP 800-63B).

E-mail e username não diferenciam maiúsculas na verificação de duplicados. O e-mail é salvo em minúsculas (constraint `CHECK`); o username mantém a grafia original e é único por `lower(username)` (índice único).

Exemplo de criação de usuário:

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "joao", "email": "joao@example.com", "password": "senha-segura"}'
```

A sessão dura uma semana e fica num cookie `HttpOnly` (o JavaScript da página não lê o token). Login e consulta do usuário com `curl`:

```bash
curl -c cookies.txt -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@example.com", "password": "senha-segura"}'
curl -b cookies.txt http://localhost:8000/users/me
```

## Arquitetura

O backend é dividido em camadas, e as dependências sempre apontam para dentro (`infrastructure` → `application` → `domain`):

```
backend/
├── domain/            # Núcleo de negócio: entidades (Pydantic) e ports (Protocols)
├── application/       # Casos de uso e interfaces de repositório
├── infrastructure/    # Adaptadores concretos
│   ├── auth/          # bcrypt e JWT
│   ├── persistence/   # Models SQLAlchemy, sessão do banco e Alembic
│   ├── repositories/  # Implementações dos repositórios
│   └── web/           # Rotas, schemas, dependências (DI) e handlers de erro
├── config/            # Configurações (Dynaconf) + settings.toml
├── scripts/           # Entrypoint do container
├── tests/             # unit/ e integration/
├── main.py            # Criação da aplicação FastAPI
├── pyproject.toml     # Dependências, Ruff e pytest
└── Dockerfile
```

- **Entidades de domínio**, **models ORM** e **schemas web** são classes separadas; os repositórios fazem o mapeamento entre domínio e ORM.
- Os **casos de uso** recebem suas dependências (repositório, hasher etc.) pelo construtor e expõem um método `async execute(...)`.
- As **rotas** recebem o caso de uso pronto via injeção de dependências do FastAPI (`infrastructure/web/dependencies.py`), o que permite substituí-lo nos testes com `app.dependency_overrides`.
- **Erros de negócio** são exceções em `domain/exceptions/`, convertidas em respostas HTTP pelos handlers de `infrastructure/web/handlers.py`.

## Segurança

- Senhas são armazenadas apenas como hash bcrypt (custo 12), calculado fora do event loop.
- Os valores das queries não aparecem em logs nem em mensagens de erro (`hide_parameters=True`).
- Erros de validação (`422`) não devolvem o valor enviado, para não expor senhas.
- Tokens JWT com PyJWT: apenas HMAC (`HS256`/`HS384`/`HS512`), claims `sub`, `iat` e `exp` obrigatórias, e chave validada na inicialização. Configuração inválida impede a API de subir.
- Cadastro limitado a 5 requisições por minuto por IP (`429` com `Retry-After`).

### Deploy

Veja o checklist em [docs/deploy.md](docs/deploy.md): variáveis obrigatórias, geração da `SECRET_KEY`, `FORWARDED_ALLOW_IPS` atrás de proxy e quando usar Redis no rate limiting.

Pendências conhecidas estão em [docs/debito-tecnico.md](docs/debito-tecnico.md).

## Decisões

Decisões de arquitetura e escopo estão registradas em [docs/adr/](docs/adr/README.md), incluindo o escopo atual da prova de conceito (sem IA).

## CI

Os workflows rodam em PRs e pushes para `develop`, `staging` e `main`, conforme as pastas alteradas.

[`backend.yml`](.github/workflows/backend.yml) roda quando muda `backend/`, o próprio workflow, o compose ou o pre-commit:

- **Lint e formatação:** `ruff check` e `ruff format --check`;
- **Testes:** suíte completa com Postgres e Redis de serviço (os testes de integração não são pulados);
- **Auditoria:** `pip-audit` nas dependências de produção;
- **Build da imagem:** `docker build`.

[`frontend.yml`](.github/workflows/frontend.yml) roda quando muda `frontend/` ou `backend/`:

- **Qualidade:** lint, tipos e build;
- **Testes:** unidade e componentes no Chromium;
- **Contrato da API:** falha se os tipos gerados do OpenAPI estiverem desatualizados em relação ao backend;
- **Auditoria:** `npm audit` nas dependências de produção.

## Contribuindo

1. Crie uma branch a partir da `develop` com o nome da **próxima versão** ([ADR-0005](docs/adr/0005-versionamento-semantico-por-branch.md)): `<tipo>/<X.Y.Z>-<descrição>`. `feat` sobe o minor e os demais tipos sobem o patch (ex.: de `0.2.0`, `feat/0.3.0-guarda-roupa` ou `fix/0.2.1-...`).
2. Atualize a versão em `backend/pyproject.toml` e `frontend/package.json`, e adicione a entrada no [`CHANGELOG.md`](CHANGELOG.md).
3. Use mensagens de commit no padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat:`, `fix:`, `chore:` ...).
4. Garanta que o lint e os testes passam nas pastas alteradas, e abra um Pull Request para a `develop`. Depois do merge, a versão recebe a tag `vX.Y.Z`.
