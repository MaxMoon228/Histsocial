#!/usr/bin/env bash
set -e

# Keep startup commands and gunicorn on the same Django settings module.
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

# DATABASE_URL can be provided directly (Render blueprint) or derived from
# DB_* variables in settings; do not hard-fail startup here.
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.prod" ] && [ -z "${DATABASE_URL:-}" ]; then
  if [ -n "${DB_HOST:-}" ] && [ "$DB_HOST" != "db" ] && [ -n "${DB_NAME:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ]; then
    export DATABASE_URL="postgres://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT:-5432}/${DB_NAME}"
    echo "WARN: DATABASE_URL was empty; built from DB_* variables." >&2
  else
    export DATABASE_URL="sqlite:///${PWD}/db.sqlite3"
    echo "WARN: DATABASE_URL and usable DB_* are missing; falling back to SQLite at ${PWD}/db.sqlite3." >&2
  fi
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
