#!/bin/bash
set -e

mkdir -p /run/uwsgi
chown www-data:www-data /run/uwsgi

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Running collect static..."
python manage.py collectstatic --noinput

exec "$@"