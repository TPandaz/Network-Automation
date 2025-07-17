#!/bin/bash

export ANSIBLE_HOST_KEY_CHECKING=False

SSH_USER=sam
SSH_PASS=sam

#list of router IPs
ROUTER_IPS=(
    192.168.122.101
    192.168.122.102
    192.168.122.103
    192.168.122.104
    192.168.122.105
    192.168.122.106
)

SSH_USER=sam
#create ~/.ssh directory
mkdir -p ~/.ssh
touch ~/.ssh/known_hosts
chmod 600 ~/.ssh/known_hosts

for ip in "${ROUTER_IPS[@]}"; do
    echo "Establishing SSH trust with $ip..."

    sshpass -p "$SSH_PASS" ssh -oStrictHostKeyChecking=no \
        -oUserKnownHostsFile=/dev/null \
        -oHostKeyAlgorithms=+ssh-rsa \
        -oKexAlgorithms=+diffie-hellman-group14-sha1 \
        -oCiphers=+aes128-cbc \
        "$SSH_USER@$ip" "exit"
done


#run ansible playbook
ansible-playbook /ansible-workspace/playbooks/ping_check.yml -i /ansible-workspace/playbooks/templates/inventory.yml

#export env variables
set -a
#load host password from .env
source /ansible-workspace/.env
set +a

# Delete existing files on host
sshpass -p "$SSH_PASSWORD" \
  ssh -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  sam@192.168.122.1 \
  "rm -f /home/sam/Prometheus/router_metrics/*.txt"

# Copy new results to host
sshpass -p "$SSH_PASSWORD" \
  scp -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  /tmp/ping_results/*.txt \
  sam@192.168.122.1:/home/sam/Prometheus/router_metrics/
