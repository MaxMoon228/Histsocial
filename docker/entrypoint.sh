#!/bin/sh
set -e

python scripts/wait_for_db.py
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_initial_sources
python manage.py create_admin_user
python manage.py create_default_staff
python manage.py seed_demo_content

exec "$@"
