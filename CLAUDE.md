# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DressMe is an async FastAPI backend (Python 3.13, managed with `uv`) backed by PostgreSQL via SQLAlchemy 2 async + asyncpg, with Alembic migrations. Code comments, log messages and GitHub issue templates are written in Portuguese.

## Commands

```bash
uv sync --all-groups                 # install deps (incl. pytest and ruff)
docker compose up -d db              # start Postgres only (localhost:5432)
uv run fastapi dev main.py           # run the API locally with reload
docker compose up --build            # run db + app (waits for db healthcheck; entrypoint runs `alembic upgrade head`, then uvicorn on :8000)

uv run alembic upgrade head                              # apply migrations
uv run alembic revision --autogenerate -m "<message>"    # new migration

uv run pytest                                            # all tests
uv run pytest -m "not integration"                       # unit only (no DB needed)
uv run pytest tests/unit/test_create_user.py::test_name  # single test

uv run ruff check --fix . && uv run ruff format .        # lint, sort imports, format
```

`DATABASE_URL` is **required at import time** (validated in `config/__init__.py`), so the app, Alembic and any test importing `infrastructure.persistence` fail without it. For local dev against the compose DB, put this in a `.env` (loaded by Dynaconf):

```
DATABASE_URL=postgresql+asyncpg://user_fastapi:password_fastapi@localhost:5432/app_db
```

Other settings: `MODE` (env switcher, default `development`; reads optional `settings.toml` environments) and `ECHO_SQL` (default `False`, SQL echo on the engine). Ruff is the linter, import sorter and formatter (config in `pyproject.toml`; rules E, W, F, I, UP, B, SIM). Keep code passing `ruff check` and `ruff format --check`. A `pre-commit` hook runs Ruff on commit (`uv run pre-commit install` once). Alembic runs Ruff on new migrations via `post_write_hooks`; `F401` is ignored in `alembic/versions/` so the template's `op`/`sa` imports survive in empty manual migrations. Autogenerate does not detect `server_default` changes — write those migrations by hand. `# ty:ignore` comments indicate the `ty` type checker is used.

## Architecture

Clean/hexagonal layering — dependencies point inward only:

- `domain/` — pure business core. Entities are **Pydantic models** (`domain/entities/`, with `UUIDMixin`/`LifeCycleMixin` giving `uid` and UTC `created_at`/`updated_at` via pendulum). `domain/ports/` holds `Protocol`s for external services (`PasswordHasher`, `TokenService`).
- `application/` — use cases (`application/use_cases/`, one class per use case with an async `execute`) and repository `Protocol`s (`application/interfaces/`). Depends only on `domain`.
- `infrastructure/` — adapters implementing the protocols:
  - `persistence/` — SQLAlchemy ORM models (`*Orm`, separate from domain entities, with parallel `SQLUUIDMixin`/`SQLLifeCycleMixin`), `Base` with a constraint naming convention, `DatabaseSessionManager` + `get_db_session` FastAPI dependency, and the Alembic env (`script_location` is `infrastructure/persistence/alembic`; URL comes from `settings`, not `alembic.ini`).
  - `repositories/` — SQLAlchemy implementations of repository protocols; responsible for mapping domain entity ↔ ORM model and committing.
  - `auth/` — `BcryptHasher`, `JWTService` (python-jose, HS256).
  - `web/` — FastAPI routers and request/response schemas (`web/schemas/`, separate from domain entities).
- `main.py` — creates the `FastAPI` app and includes routers.

Wiring uses FastAPI DI in `infrastructure/web/dependencies.py`: provider functions build the concrete repository/adapters and the use case, exposed as `Annotated[..., Depends(...)]` aliases (`SessionDep`, `CreateUserUseCaseDep`, ...). Routes take the use case as a parameter and return the domain entity, which FastAPI serializes through the `response_model` schema. Tests replace providers via `app.dependency_overrides`.

`PasswordHasher` is async: `BcryptHasher` runs bcrypt in a worker thread (`anyio.to_thread`) so it doesn't block the event loop. bcrypt rejects passwords over 72 bytes, so `UserCreate` validates the byte length (not characters).

When adding a new ORM model, export it from `infrastructure/persistence/models/__init__.py` (in `__all__`) so Alembic autogenerate sees it; importing it only for side effects elsewhere gets stripped by Ruff (F401).

Business errors are plain exceptions in `domain/exceptions/`, raised by use cases and mapped to HTTP responses by handlers in `infrastructure/web/handlers.py`, registered in `main.py`. A custom `RequestValidationError` handler strips `input` from 422 responses so passwords are never echoed back.

Email and username are case-insensitive: normalized to lowercase in the domain entity (`normalize_email`/`normalize_username`), in `UserCreate`, and enforced in the DB by `CHECK` constraints (`ck_users_*_lowercase`). The engine uses `hide_parameters=True` so query values never reach logs.

Tests: `tests/unit/` uses in-memory fakes (`tests/fakes.py`) and the `anyio` pytest plugin (`pytestmark = pytest.mark.anyio`). `tests/integration/` (marker `integration`) runs against real Postgres at `TEST_DATABASE_URL` (default `app_db_test` on the compose DB, auto-created); each test runs in a transaction rolled back at the end (`join_transaction_mode="create_savepoint"`), and `test_migrations.py` runs Alembic upgrade/downgrade/check in a separate `*_migrations` DB. Integration tests skip if Postgres is unreachable.

Known tech debt lives in `docs/debito-tecnico.md`; update it when resolving or discovering items.
