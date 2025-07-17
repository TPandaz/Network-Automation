#!/bin/bash

#exit script if any command returns a non-zero exit code
set -e

cd /ansible-workspace
git pull origin main

chmod +x /ansible-workspace/scripts/run_ping_check.sh
touch /ansible-workspace/scripts/run_ping_check.log

#creat ssh config to disbale host verification
mkdir -p ~/.ssh
echo "StrictHostKeyChecking no" > ~/.ssh/config
echo "UserKnownHostsFile /dev/null" >> ~/.ssh/config
chmod 600 ~/.ssh/config

#set PATH for cron
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" > /etc/cron.d/ping_check
echo "* * * * * root /ansible-workspace/scripts/run_ping_check.sh >> /ansible-workspace/scripts/run_ping_check.log 2>&1" >> /etc/cron.d/ping_check
chmod 0644 /etc/cron.d/ping_check
#start cron
cron 

#tail the log so output is visible
#tail -F /ansible-workspace/scripts/run_ping_check.log

#start shell environment
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
exec /bin/bash
