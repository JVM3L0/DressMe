# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,id=s/00dbd04b-7f2d-4ca2-aa81-56fe156635d1-uv-cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

ADD . /app

RUN --mount=type=cache,id=s/00dbd04b-7f2d-4ca2-aa81-56fe156635d1-uv-cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["scripts/entrypoint.sh"]
