#!/bin/sh
ansible-playbook grindstone.yml --private-key=./ssh_conf/id_rsa -K -u deployer -i ./hosts
