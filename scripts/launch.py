#!/usr/bin/env python3

import signal
import os
import importlib
import shutil
from lxcutil import *
from time import sleep

rootfs="/data/rootfs"
rootfs_tmp="/data/rootfs.tmp"

if not os.path.isdir(rootfs):
    distribution=os.environ.get("DISTRIBUTION",None).lower()
    if (distribution):
        try:
            distribution_script = importlib.import_module('distribution_%s'%distribution)
        except ModuleNotFoundError:
            print("Unsupported DISTRIBUTION: %s"%distribution)
            quit(1)
        # cleanup
        if os.path.isdir(rootfs_tmp):
            print("Removing old temporary rootfs")
            shutil.rmtree(rootfs_tmp)
        # setup
        os.mkdir(rootfs_tmp)
        distribution_script.install_to(rootfs_tmp)
        os.rename(rootfs_tmp,rootfs)
    else:
        print("Please set DISTRIBUTION or provide your own root filesystem at /data/rootfs")
        quit(1)

if bool(os.environ.get("COPY_RESOLV_CONF","true")):
    print("Copy resolv.conf to machine")
    run("cat /etc/resolv.conf > /data/rootfs/etc/resolv.conf")

if os.environ.get("INITIAL_SSH_KEY",None) is not None and not os.path.exists("/data/rootfs/root/.ssh/authorized_keys"):
    print("Adding initial ssh key for root")
    os.makedirs("/data/rootfs/root/.ssh", exist_ok=True)
    writefile("/data/rootfs/root/.ssh","authorized_keys",os.environ.get("INITIAL_SSH_KEY")+"\n")


run("mkdir -p /var/lib/lxcfs")

if bool(os.environ.get("USE_LXCFS","true")):
    print("Mounting lxcfs")
    subprocess.Popen(["lxcfs","-s","-o","allow_other","/var/lib/lxcfs"])
    waitcount=0
    while not os.path.exists("/var/lib/lxcfs/proc/uptime"):
        waitcount+=1
        if waitcount>10:
            print("Timeout waiting for lxcfs")
            quit(1)
        sleep(1)

run("mkdir -p /data/machine")
run("cp /scripts/lxc-config /data/machine/config")

def shutdown_handler(signum, frame):
    print("Shutdown signal received")
    subprocess.call([
        "/usr/bin/lxc-stop",
        "machine"
    ])

signal.signal(signal.SIGTERM, shutdown_handler)

print("Starting machine")
returncode=subprocess.call([
    "/usr/bin/lxc-start",
    "--name","machine",
    "--foreground",
    "-l","DEBUG"
])
if returncode==0:
    print("Machine stoped.")
else:
    print("Machine failed with exit code %s"%returncode)

quit(returncode)
