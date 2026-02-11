#!/bin/bash
set -e

./wait-for-it.sh db:5432 -t 30

if ["$ROLE" = "web"]; then
	mkdir -p /run/uwsgi
	chown www-data:www-data /run/uwsgi
	echo "Running database migrations..."
	uv run --no-sync python manage.py migrate --noinput
	echo "Running collect static..."
	uv run --no-sync python manage.py collectstatic --noinput
fi

exec "$@"