# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DressMe is an async FastAPI backend (Python 3.13, managed with `uv`) backed by PostgreSQL via SQLAlchemy 2 async + asyncpg, with Alembic migrations. Code comments, log messages and GitHub issue templates are written in Portuguese.

## Commands

```bash
uv sync --all-groups                 # install deps (incl. pytest and ruff)
docker compose up -d db              # start Postgres only (localhost:5432)
uv run fastapi dev main.py           # run the API locally with reload
docker compose up --build            # run db + app (entrypoint runs `alembic upgrade head`, then uvicorn on :8000)

uv run alembic upgrade head                              # apply migrations
uv run alembic revision --autogenerate -m "<message>"    # new migration

uv run pytest                                            # all tests
uv run pytest tests/unit/test_create_user.py::test_name  # single test

uv run ruff check --fix . && uv run ruff format .        # lint, sort imports, format
```

`DATABASE_URL` is **required at import time** (validated in `config/__init__.py`), so the app, Alembic and any test importing `infrastructure.persistence` fail without it. For local dev against the compose DB, put this in a `.env` (loaded by Dynaconf):

```
DATABASE_URL=postgresql+asyncpg://user_fastapi:password_fastapi@localhost:5432/app_db
```

Other settings: `MODE` (env switcher, default `development`; reads optional `settings.toml` environments) and `ECHO_SQL` (default `True`, SQL echo on the engine). Ruff is the linter, import sorter and formatter (config in `pyproject.toml`; rules E, W, F, I, UP, B, SIM). Keep code passing `ruff check` and `ruff format --check`. Alembic runs Ruff on new migrations via `post_write_hooks`. `# ty:ignore` comments indicate the `ty` type checker is used.

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

Wiring is done manually inside route handlers: the route gets an `AsyncSession` via `Depends(get_db_session)`, constructs the concrete repository/adapters, injects them into the use case, and returns the domain entity which FastAPI serializes through the `response_model` schema.

When adding a new ORM model, export it from `infrastructure/persistence/models/__init__.py` (in `__all__`) so Alembic autogenerate sees it; importing it only for side effects elsewhere gets stripped by Ruff (F401).

Business errors are plain exceptions in `domain/exceptions/`, raised by use cases and mapped to HTTP responses by handlers in `infrastructure/web/handlers.py`, registered in `main.py`. Unit tests use in-memory fakes for repository/ports and the `anyio` pytest plugin (bundled with FastAPI) for async tests.
