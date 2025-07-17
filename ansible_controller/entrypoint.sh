#!/bin/bash

#exit script if any command returns a non-zero exit code
set -e

cd /ansible-workspace
git pull origin main

chmod +x /ansible-workspace/scripts/run_ping_check.sh
touch /ansible-workspace/scripts/run_ping_check.log

# Write cron job to /etc/cron.d (system-wide, persistent)
echo "* * * * * root /ansible-workspace/scripts/run_ping_check.sh >> /ansible-workspace/scripts/run_ping_check.log 2>&1" > /etc/cron.d/ping_check
chmod 0644 /etc/cron.d/ping_check

#apply cron job to root's crontab
cron -f &

#tail the log so output is visible
tail -F /ansible-workspace/scripts/run_ping_check.log

