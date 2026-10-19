# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Monorepo: `backend/` (this API), `frontend/` (SvelteKit — see the Frontend section), `docs/` (ADRs, deploy, tech debt), `CHANGELOG.md`. Root holds `docker-compose.yml` (`db`, `app` from `./backend`, `web` = nginx + static frontend from `./frontend`), the shared `.env`/`.env.example` (Dynaconf in `backend/` finds the root `.env` by walking up), `.pre-commit-config.yaml` (Ruff limited to `^backend/`) and `.github/workflows/backend.yml` (path-filtered, `working-directory: backend`). **Run all `uv` commands from `backend/`; paths below are relative to `backend/` unless they start with `docs/`, `.github/` or name a root file.**

DressMe is an async FastAPI backend (Python 3.13, managed with `uv`) backed by PostgreSQL via SQLAlchemy 2 async + asyncpg, with Alembic migrations. Code comments, log messages and GitHub issue templates are written in Portuguese.

## Commands

```bash
uv sync                              # install deps; dev+test groups are default-groups
docker compose up -d db              # (repo root) start Postgres only (localhost:5432)
uv run fastapi dev main.py           # run the API locally with reload
docker compose up --build            # (repo root) full stack at http://localhost:8080 (WEB_PORT): web → app → db, gated by healthchecks; API docs at /api/docs

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

Config is Dynaconf only (don't add python-dotenv): `.env` + env vars override `settings.toml`. `docker-compose.yml` requires `POSTGRES_*` and `SECRET_KEY` from `.env` (template: `.env.example`) and binds ports to 127.0.0.1. In compose the API is **not published** (`expose: 8000`); only nginx reaches it, so `app` sets `FORWARDED_ALLOW_IPS=*` and `UVICORN_ROOT_PATH=/api` (for `/api/docs`). nginx (`frontend/nginx/default.conf`) strips `/api`, **overwrites** `X-Forwarded-For` with `$remote_addr` (anti-spoofing for rate limiting), serves prerendered pages via `try_files $uri $uri.html $uri/ /200.html`, caches `/_app/immutable/` for a year, and includes `nginx/security-headers.conf` in every `location` (a location-level `add_header` drops inherited ones). The Dockerfile syncs with `--no-default-groups` so dev/test tools stay out of the image.

CI (`.github/workflows/backend.yml`, runs only on changes to `backend/**`, the workflow, compose or pre-commit; concurrency group is per workflow): ruff, pytest with a Postgres service, `pip-audit` on prod deps (with documented `--ignore-vuln` entries tied to `docs/debito-tecnico.md`), and `docker build`. Actions are pinned by commit SHA.

Known tech debt lives in `docs/debito-tecnico.md`; update it when resolving or discovering items.

Architecture/scope decisions are ADRs in `docs/adr/` (accepted ADRs are never edited; supersede with a new one). The project is a **proof of concept of VirtualFit** (virtual clothing try-on) without AI (ADR-0001): manual try-on in the browser, a planned monorepo with a SvelteKit frontend (ADR-0002), and images on local disk served by nginx via `X-Accel-Redirect`, never public (ADR-0003). Check new work against these ADRs.

## Frontend

`frontend/`: SvelteKit 3 + Svelte 5 runes + TypeScript, `adapter-static` (all pages prerendered, `200.html` SPA fallback; ADR-0004). Node 24 LTS via `frontend/.node-version` (installed with fnm at `~/.local/share/fnm`; run `eval "$(~/.local/share/fnm/fnm env)"` in non-login shells). Run `npm` commands from `frontend/`:

```bash
npm run dev        # :5173; Vite proxies /api/* to the API (prefix stripped; API_PROXY_TARGET overrides)
npm run check      # svelte-check
npm run lint       # prettier --check + eslint
npm test           # vitest: "server" project (Node, *.spec.ts) + "client" project (Chromium, *.svelte.spec.ts)
npm run build
npm run api:sync   # backend → src/lib/api/openapi.json (scripts/export_openapi.py) → src/lib/api/schema.ts
```

- Internal imports use `#lib/...` **with explicit extensions** (`#lib/api/client.ts`); SvelteKit 3 maps `#lib/*` → `src/lib/*` with `allowImportingTsExtensions`. Use `resolve()` from `$app/paths` for internal `href`s (ESLint enforces it).
- API calls go through `api` (`src/lib/api/client.ts`, openapi-fetch typed by the generated `schema.ts`; same origin under `/api`, so no CORS). `fetch` is resolved per request so tests can `vi.stubGlobal('fetch', ...)`. Never edit `openapi.json`/`schema.ts` by hand; the frontend CI `contract` job fails if they're stale. `openapi-typescript` is pinned to the project's TS 6 via `overrides` (it only declares TS 5 as a peer).
- Keep logic out of components: `src/lib/signup/validation.ts` (rules mirroring backend `UserCreate`, pt-BR messages shared with API 422 mapping in `src/lib/api/errors.ts`) and `submit.ts` (maps HTTP outcomes to a discriminated `SignupResult`).
- Design system lives in `src/app.css` tokens: Gruvbox palette (light "hard" default, dark via `prefers-color-scheme`; text pairs checked ≥ 4.5:1), Bodoni Moda (display) + Figtree (body) self-hosted via `@fontsource-variable`, 1.25 type scale. `HangTag.svelte` (yellow clothing tag) is the single signature element; components read `--field-*`/`--button-*` custom properties so the tag can restyle them. UX rules: validate on blur (not per keystroke), error replaces hint, focus first invalid field on submit, `role="alert"` region stays in the DOM, 44px touch targets, visible focus.
- Theme: light/dark follows the system unless the user picks one (`src/lib/theme.ts`, `localStorage['theme']`, `data-theme` on `<html>`). Dark tokens in `app.css` are written twice on purpose (`@media` + `[data-theme='dark']`), because `light-dark()` would break Safari 16 (RNF05). An inline script in `src/app.html` applies the saved theme before first paint; keep it in sync with `theme.ts`. `ThemeToggle` reads the theme in `onMount`, because pages are prerendered and `document` doesn't exist at build time.
- Component tests need Chromium system libs; locally they can run in `mcr.microsoft.com/playwright:v<playwright version>-noble` (see `frontend/README.md`).

## Versioning

Each branch is the next product version, `<type>/<X.Y.Z>-<slug>` (ADR-0005): `feat` bumps minor, other types bump patch. Bump `backend/pyproject.toml` and `frontend/package.json` together (the API exposes the version from pyproject via `config.APP_VERSION`) and add a `CHANGELOG.md` entry.

