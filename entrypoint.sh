#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate head

echo "Seeding countries (idempotent)..."
python manage.py seed-countries

echo "Starting server..."
exec uvicorn web.app:app --host 0.0.0.0 --port 8000
