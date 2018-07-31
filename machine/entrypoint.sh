#!/bin/bash

set -e

/opt/vagrant/bin/vagrant up
lxc-attach -n machine
