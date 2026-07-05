#!/bin/sh
set -e

: "${CRON_SCHEDULE:=0 9 * * 1-5}"

echo "Installing cron schedule: ${CRON_SCHEDULE}"
echo "${CRON_SCHEDULE} cd /app && CREDS_PATH=/app/creds.json /usr/local/bin/python /app/shioaji_sync.py >> /proc/1/fd/1 2>> /proc/1/fd/2" | crontab -

exec cron -f
