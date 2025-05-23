#!/bin/bash


echo "$1 $2"
echo "192.168.100.$1" > inventory 
ansible-playbook /app/ansible/init_vm.yml -i inventory -e "ssh_user=root" -e "ssh_key='$2'" --private-key /root/.ssh/id_ed25519