# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DressMe is an async FastAPI backend (Python 3.13, managed with `uv`) backed by PostgreSQL via SQLAlchemy 2 async + asyncpg, with Alembic migrations. Code comments, log messages and GitHub issue templates are written in Portuguese.

## Commands

```bash
uv sync                              # install deps; dev+test groups are default-groups
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
  - `auth/` — `BcryptHasher`, `JWTService` (PyJWT; HMAC only, per-algorithm min key bytes, required `sub`/`iat`/`exp`; `verify_token` returns `None` on any invalid token). `get_token_service` returns a singleton built at import so bad JWT config fails at startup.
  - `web/` — FastAPI routers and request/response schemas (`web/schemas/`, separate from domain entities).
- `main.py` — creates the `FastAPI` app and includes routers.

Wiring uses FastAPI DI in `infrastructure/web/dependencies.py`: provider functions build the concrete repository/adapters and the use case, exposed as `Annotated[..., Depends(...)]` aliases (`SessionDep`, `CreateUserUseCaseDep`, ...). Routes take the use case as a parameter and return the domain entity, which FastAPI serializes through the `response_model` schema. Tests replace providers via `app.dependency_overrides`.

`PasswordHasher` is async: `BcryptHasher` runs bcrypt in a worker thread (`anyio.to_thread`) so it doesn't block the event loop. bcrypt rejects passwords over 72 bytes, so `UserCreate` validates the byte length (not characters).

When adding a new ORM model, export it from `infrastructure/persistence/models/__init__.py` (in `__all__`) so Alembic autogenerate sees it; importing it only for side effects elsewhere gets stripped by Ruff (F401).

Business errors are plain exceptions in `domain/exceptions/`, raised by use cases and mapped to HTTP responses by handlers in `infrastructure/web/handlers.py`, registered in `main.py`. A custom `RequestValidationError` handler strips `input` from 422 responses so passwords are never echoed back.

Email and username are unique case-insensitively. Email is lowercased (domain `normalize_email`, `UserCreate`) and enforced by `CHECK ck_users_email_lowercase`. Username keeps its original casing (`normalize_username` only strips); uniqueness is by `lower(username)` in the repository query and the `uq_users_username_lower` functional unique index (declared at module level in `user_model.py`). The engine uses `hide_parameters=True` so query values never reach logs.

Tests: `tests/conftest.py` sets `MODE=testing`, selecting the `[testing]` env in `settings.toml` (placeholder `DATABASE_URL` so unit tests import without a `.env`). `tests/unit/` uses in-memory fakes (`tests/fakes.py`) and the `anyio` pytest plugin (`pytestmark = pytest.mark.anyio`). `tests/integration/` (marker `integration`) runs against real Postgres at `TEST_DATABASE_URL` (default: `DATABASE_URL` with database `<name>_test`, auto-created); each test runs in a transaction rolled back at the end (`join_transaction_mode="create_savepoint"`), and `test_migrations.py` runs Alembic upgrade/downgrade/check in a separate `*_migrations` DB. Integration tests skip if Postgres is unreachable, but fail when `CI` is set.

`SECRET_KEY` is required (custom validator message so the value never appears in errors; `[testing]` in `settings.toml` provides a test key). Signup is rate limited with slowapi (`infrastructure/web/rate_limit.py`, per client IP, moving window, `RATE_LIMIT_*` settings); decorated endpoints need a `request: Request` param. The limiter is disabled in the testing env; `tests/unit/test_rate_limit.py` enables it per test and calls `limiter.reset()`. Behind a proxy, uvicorn needs `FORWARDED_ALLOW_IPS` to see real client IPs. Redis storage is supported (`limits[redis]`); `tests/integration/test_rate_limit_redis.py` runs when `TEST_REDIS_URL` is set (CI has a Redis service) and checks two limiter instances share counters. Production env vars and rollout checklist: `docs/deploy.md`.

Config is Dynaconf only (don't add python-dotenv): `.env` + env vars override `settings.toml`. `docker-compose.yml` requires `POSTGRES_*` from `.env` (template: `.env.example`) and binds ports to 127.0.0.1. The Dockerfile syncs with `--no-default-groups` so dev/test tools stay out of the image.

CI (`.github/workflows/ci.yml`): ruff, pytest with a Postgres service, `pip-audit` on prod deps (with documented `--ignore-vuln` entries tied to `docs/debito-tecnico.md`), and `docker build`. Actions are pinned by commit SHA.

Known tech debt lives in `docs/debito-tecnico.md`; update it when resolving or discovering items.

Architecture/scope decisions are ADRs in `docs/adr/` (accepted ADRs are never edited; supersede with a new one). The project is a **proof of concept of VirtualFit** (virtual clothing try-on) without AI (ADR-0001): manual try-on in the browser, a planned monorepo with a SvelteKit frontend (ADR-0002), and images on local disk served by nginx via `X-Accel-Redirect`, never public (ADR-0003). Check new work against these ADRs.
