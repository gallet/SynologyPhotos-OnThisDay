#!/bin/bash

#VARIOUS IMPORTANT FILES
CRON_FILE=/tmp/cron
ENV_FILE=/container.env
CRONTAB_BAK_FILE=/etc/crontab.bak
CRONTAB_FILE=/etc/crontab

CRON_STR=$(cat $CRON_FILE)

echo "=========="
echo "Welcome to run_crond.sh, a wrapper to $CRON_STR that loads the container environment variables into the cron shell"
echo "=========="
echo ""

echo "Exporting variables to $ENV_FILE"
echo ""
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > "$ENV_FILE"

if test -f "$CRONTAB_BAK_FILE"; then
  echo "Retrieving $CRONTAB_FILE from $CRONTAB_BAK_FILE"
  cp "$CRONTAB_BAK_FILE" "$CRONTAB_FILE"
else
  echo "Copying $CRONTAB_FILE to $CRONTAB_BAK_FILE"
  cp "$CRONTAB_FILE" "$CRONTAB_BAK_FILE"
fi
echo ""

echo "SHELL=/bin/bash"    >> "$CRONTAB_FILE" && \
echo "BASH_ENV=$ENV_FILE" >> "$CRONTAB_FILE" && \
echo "$CRON_STR"          >> "$CRONTAB_FILE"

echo "$CRONTAB_FILE ready:"
cat "$CRONTAB_FILE"
echo ""

## Run cron deamon
echo "starting cron deamon in the foreground"
cron -f
echo ""