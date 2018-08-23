#!/bin/bash

set -e

if [ -z "${LXC_BOX}" ]; then
  echo "Please set the LXC_BOX variable"
  exit 1
fi

# Replace the box name/url
sed -i "s|__BOX__|${LXC_BOX}|" Vagrantfile

mkdir -p /data/.vagrant /data/rootfs /var/lib/lxc/machine/rootfs
ln -sf /data/.vagrant /opt/machine/.vagrant
ln -sf /data/lxc-config /var/lib/lxc/machine/config
mount -o bind /data/rootfs /var/lib/lxc/machine/rootfs

function shut_down() {
    set +e
    echo "Got signal $1 - shutting down"
    /opt/vagrant/bin/vagrant halt
    exit 0
}

/opt/vagrant/bin/vagrant up --no-provision

for sig in SIGKILL SIGTERM SIGHUP SIGINT SIGQUIT EXIT; do
  trap "shut_down $sig" $sig
done

if [ -e /data/playbook.yml ]; then
  if [ ! -f /data/.is_provisioned ]; then
    /opt/vagrant/bin/vagrant provision
    touch /data/.is_provisioned
  fi
fi

while true; do
  lxc-info --name machine | grep -e "RUNNING" > /dev/null
  sleep 1
done

shut_down()
