#!/bin/bash

cd /ansible-workspace
git pull origin main

#write/overwrite crontab entry
echo "* * * * * /ansible-workspace/scripts/run_ping_check.sh >> /ansible-workspace/scripts/run_ping_check.log 2>&1" | crontab -
#start cron
service cron start

tail -f /ansible-workspace/scripts/run_ping_check.log

exec /bin/bash
