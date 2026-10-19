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
| Autenticação  | bcrypt (hash de senha), python-jose (JWT)    |
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
   uv sync --all-groups
   uv run pre-commit install   # roda o Ruff antes de cada commit
   ```

2. Crie um arquivo `.env` na raiz do projeto (já ignorado pelo Git):

   ```env
   DATABASE_URL=postgresql+asyncpg://user_fastapi:password_fastapi@localhost:5432/app_db
   ```

### Variáveis de ambiente

| Variável       | Obrigatória | Padrão        | Descrição                                              |
| -------------- | ----------- | ------------- | ------------------------------------------------------ |
| `DATABASE_URL` | Sim         | —             | URL de conexão async (`postgresql+asyncpg://...`)      |
| `MODE`         | Não         | `development` | Ambiente ativo do Dynaconf                             |
| `ECHO_SQL`     | Não         | `False`       | Exibe no log as queries SQL executadas                 |

> `DATABASE_URL` é validada na importação da aplicação: sem ela, a API, o Alembic e os testes não sobem.

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

O container da aplicação aguarda o Postgres ficar saudável (healthcheck), executa `alembic upgrade head` e inicia o servidor na porta `8000`.

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
# Todos os testes
uv run pytest

# Um arquivo ou teste específico
uv run pytest tests/unit/test_create_user.py
uv run pytest tests/unit/test_create_user.py::nome_do_teste
```

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
| POST   | `/users/`       | Cria um novo usuário (`201`; `409` se e-mail ou username já existir) |

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
│   └── web/           # Rotas FastAPI e schemas de request/response
├── config/            # Configurações (Dynaconf)
├── scripts/           # Entrypoint do container
├── tests/
└── main.py            # Criação da aplicação FastAPI
```

- **Entidades de domínio**, **models ORM** e **schemas web** são classes separadas; os repositórios fazem o mapeamento entre domínio e ORM.
- Os **casos de uso** recebem suas dependências (repositório, hasher etc.) pelo construtor e expõem um método `async execute(...)`.
- As **rotas** montam as dependências concretas e invocam o caso de uso.

## Contribuindo

1. Abra uma issue usando o template **🚀 Nova Task** (`.github/ISSUE_TEMPLATE/feature_request.md`).
2. Crie uma branch a partir da `main`.
3. Use mensagens de commit no padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat:`, `fix:`, `chore:` ...).
4. Garanta que `uv run ruff check .`, `uv run ruff format --check .` e `uv run pytest` passam, e abra um Pull Request.
