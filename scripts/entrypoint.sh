#!/bin/bash

set -e

echo "Rodando migrações..."
alembic upgrade head

echo "Iniciando o servidor..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"