#!/usr/bin/env sh
set -e

# Roda migrations e sobe o servidor. PORT é injetado pelo Render (10000);
# no Docker local cai no 8000.
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
