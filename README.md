# DressMe

API backend do DressMe, construída com **FastAPI** e **PostgreSQL**, seguindo uma arquitetura em camadas (Clean Architecture / Hexagonal).

## Sumário

- [Stack](#stack)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Executando](#executando)
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

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (instala o Python 3.13 automaticamente, se necessário)
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose

## Configuração

1. Clone o repositório e instale as dependências:

   ```bash
   git clone git@github.com:JVM3L0/DressMe.git
   cd DressMe
   uv sync                     # inclui as ferramentas de dev e testes
   uv run pre-commit install   # roda o Ruff antes de cada commit
   ```

2. Crie o `.env` a partir do exemplo e troque a senha (o `.env` é ignorado pelo Git):

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
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | `15`   | Validade do token de acesso                            |
| `RATE_LIMIT_ENABLED` | Não   | `true`        | Liga o limite de requisições                           |
| `RATE_LIMIT_SIGNUP` | Não    | `5/minute`    | Limite de cadastros por IP                             |
| `RATE_LIMIT_STORAGE_URI` | Não | `memory://` | Armazenamento dos contadores (`redis://...` com várias instâncias) |
| `FORWARDED_ALLOW_IPS` | Deploy | `127.0.0.1` | IPs de proxy confiáveis para o uvicorn (IP real do cliente) |

A configuração usa o [Dynaconf](https://www.dynaconf.com/): valores por ambiente ficam em `settings.toml` e são sobrescritos pelo `.env` e pelas variáveis de ambiente. `DATABASE_URL` é validada na importação da aplicação: sem ela, a API e o Alembic não sobem.

## Executando

### Desenvolvimento local

Suba apenas o banco com Docker e rode a API localmente com hot reload:

```bash
docker compose up -d db
uv run alembic upgrade head
uv run fastapi dev main.py
```

A API fica disponível em <http://localhost:8000> e a documentação interativa em <http://localhost:8000/docs>.

### Tudo via Docker

```bash
docker compose up --build
```

O container da aplicação aguarda o Postgres ficar saudável (healthcheck), executa `alembic upgrade head` e inicia o servidor na porta `8000`. As portas do banco e da API ficam acessíveis apenas pela própria máquina (`127.0.0.1`).

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

Regras do cadastro:

- **username:** 3 a 255 caracteres; letras, números, `_`, `.` ou `-`. A grafia é preservada.
- **email:** e-mail válido.
- **password:** mínimo de 8 caracteres e máximo de 72 bytes (limite do bcrypt).

E-mail e username não diferenciam maiúsculas na verificação de duplicados. O e-mail é salvo em minúsculas (constraint `CHECK`); o username mantém a grafia original e é único por `lower(username)` (índice único).

Exemplo de criação de usuário:

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "joao", "email": "joao@example.com", "password": "senha-segura"}'
```

## Arquitetura

O projeto é dividido em camadas, e as dependências sempre apontam para dentro (`infrastructure` → `application` → `domain`):

```
.
├── domain/            # Núcleo de negócio: entidades (Pydantic) e ports (Protocols)
├── application/       # Casos de uso e interfaces de repositório
├── infrastructure/    # Adaptadores concretos
│   ├── auth/          # bcrypt e JWT
│   ├── persistence/   # Models SQLAlchemy, sessão do banco e Alembic
│   ├── repositories/  # Implementações dos repositórios
│   └── web/           # Rotas, schemas, dependências (DI) e handlers de erro
├── config/            # Configurações (Dynaconf)
├── docs/              # Documentação do projeto (ex.: débito técnico)
├── scripts/           # Entrypoint do container
├── tests/             # unit/ e integration/
└── main.py            # Criação da aplicação FastAPI
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

### Deploy atrás de proxy

O limite usa o IP do cliente. Atrás de um proxy ou plataforma de deploy, defina `FORWARDED_ALLOW_IPS` com os IPs do proxy (ou `*`, se a API só for acessível por ele) para o uvicorn usar o `X-Forwarded-For`. Sem isso, todos os clientes compartilham o limite do IP do proxy. Com mais de uma instância, use um `RATE_LIMIT_STORAGE_URI` compartilhado (ex.: Redis).

Pendências conhecidas estão em [docs/debito-tecnico.md](docs/debito-tecnico.md).

## CI

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em PRs e pushes para `develop`, `staging` e `main`:

- **Lint e formatação:** `ruff check` e `ruff format --check`;
- **Testes:** suíte completa com um Postgres de serviço (os testes de integração não são pulados);
- **Auditoria:** `pip-audit` nas dependências de produção;
- **Build da imagem:** `docker build`.

## Contribuindo

1. Abra uma issue usando o template **🚀 Nova Task** (`.github/ISSUE_TEMPLATE/feature_request.md`).
2. Crie uma branch a partir da `main`.
3. Use mensagens de commit no padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat:`, `fix:`, `chore:` ...).
4. Garanta que `uv run ruff check .`, `uv run ruff format --check .` e `uv run pytest` passam, e abra um Pull Request.
