#!/bin/bash

# run ansible playbook
ansible-playbookk /ansible-workspace/playbooks/ping_check.yml

#copy results to shared folder that can be access by prometheus
scp /tmp/ping_results/*.txt sam@ 192.168.122.1:/home/sam/Prometheus/router_metrics/
