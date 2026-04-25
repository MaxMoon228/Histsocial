#!/usr/bin/env bash
set -e

# Keep startup commands and gunicorn on the same Django settings module.
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

# In production we must never silently boot without a real database URL,
# otherwise bootstrap runs against SQLite and requests fail at runtime.
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.prod" ] && [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set for production startup." >&2
  exit 1
fi

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
