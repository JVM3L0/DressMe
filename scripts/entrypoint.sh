#!/bin/bash

echo "Aguardando o banco de dados..."

echo "Rodando migrações..."
alembic upgrade head

echo "Iniciando o servidor..."
exec uvicorn main:app --host 0.0.0.0 --port 8000