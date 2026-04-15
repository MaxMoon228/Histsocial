#!/bin/sh
set -e

python scripts/wait_for_db.py

SYNC_ARGS="--pages ${HISTORY_CALENDAR_DEFAULT_PAGES:-3} --from-page ${HISTORY_CALENDAR_FROM_PAGE:-1}"
if [ "${HISTORY_CALENDAR_WITH_DETAILS:-1}" = "1" ]; then
  SYNC_ARGS="$SYNC_ARGS --with-details"
fi

CRON_EXPR="${HISTORY_CALENDAR_CRON:-0 3 * * *}"
echo "${CRON_EXPR} cd /app && python manage.py sync_history_calendar ${SYNC_ARGS} >> /proc/1/fd/1 2>> /proc/1/fd/2" > /etc/cron.d/history-calendar
chmod 0644 /etc/cron.d/history-calendar
crontab /etc/cron.d/history-calendar

# First import immediately on container start for fast warmup.
python manage.py sync_history_calendar $SYNC_ARGS || true

cron -f
