#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_initial_sources
python manage.py create_admin_user
python manage.py create_default_staff
python manage.py seed_demo_content

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --access-logfile "-" \
  --error-logfile "-" \
  --capture-output \
  --log-level "${GUNICORN_LOG_LEVEL:-info}" \
  "$@"
