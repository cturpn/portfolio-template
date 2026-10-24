#!/bin/sh
# Start the portfolio locally: creates .venv and .env if missing, installs deps, runs Flask.
# Usage: ./start.sh [--prod]   (--prod runs gunicorn instead of the dev server; set HOST/PORT to change the bind address)
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example; fill in your secrets."
fi

if [ "${1:-}" = "--prod" ]; then
    exec gunicorn wsgi:app --bind "${HOST:-127.0.0.1}:${PORT:-8000}"
else
    exec flask --app wsgi run --debug --port "${PORT:-5000}"
fi
