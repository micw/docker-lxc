#!/bin/bash

if [ -z $LXC_ROOTFS_PATH ]; then
  echo "Error: LXC_ROOTFS_PATH not set"
  exit 1
fi

# remove 'dir:' prefix from root path
LXC_ROOTFS_PATH=${LXC_ROOTFS_PATH#'dir:'}

if [ ! -f ${LXC_ROOTFS_PATH}/etc/network/interfaces ]; then
  echo "No debian-like network config found - skipping"
  exit 0
fi

set -e

PATH="/bin:/usr/bin:$PATH"
# remove network settings
echo '' > ${LXC_ROOTFS_PATH}/etc/network/interfaces

# copy resolv.conf
cat /etc/resolv.conf > ${LXC_ROOTFS_PATH}/etc/resolv.conf

exit 0
