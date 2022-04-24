#!/bin/bash
curl -sL https://deb.nodesource.com/setup_14.x | bash -
apt update
apt upgrade -y
apt install -y nodejs libz-dev libpq-dev python3 \
               python3-dev python3-pip virtualenv \
               python python-dev libmemcached-dev
apt autoremove -y