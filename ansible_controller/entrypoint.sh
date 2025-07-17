#!/bin/bash

#exit script if any command returns a non-zero exit code
set -e

cd /ansible-workspace
git pull origin main

# Write cron job to /etc/cron.d (system-wide, persistent)
echo "* * * * * root /ansible-workspace/scripts/run_ping_check.sh >> /ansible-workspace/scripts/run_ping_check.log 2>&1" > /etc/cron.d/ping_check
chmod 0644 /etc/cron.d/ping_check

#apply cron job to root's crontab
crontab /etc/cron.d/ping_check
service cron start

#tail the log so output is visible
touch /ansible_workspace/scripts/run_ping_check.log
tail -F /ansible-workspace/scripts/run_ping_check.log

