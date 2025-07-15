#!/bin/bash

# run ansible playbook
ansible-playbook /ansible-workspace/playbooks/ping_check.yml -i /ansible-workspace/playbooks/templates/inventory.yml

#copy results to shared folder that can be access by prometheus
scp /tmp/ping_results/*.txt sam@192.168.122.1:/home/sam/Prometheus/router_metrics/txt_files
