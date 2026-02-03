#!/bin/bash
set -e

mkdir -p /run/uwsgi
chown www-data:www-data /run/uwsgi

echo "Running database migrations..."
uv run python manage.py migrate --noinput

echo "Running collect static..."
uv run python manage.py collectstatic --noinput

exec "$@"