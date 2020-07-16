#!/usr/bin/env python3

import os
import subprocess
import requests
import yaml
from urllib.request import urlopen
from lxcutil import *

def run_chroot(dir,cmd):
    run("arch-chroot %s %s"%(dir,cmd))

def install_to(dir):

    arch=os.environ.get("ALPINE_ARCH","x86_64")
    version=os.environ.get("ALPINE_VERSION","latest-stable")
    extra_packages=os.environ.get("ALPINE_EXTRA_PACKAGES","")
    releases_url="http://dl-cdn.alpinelinux.org/alpine/%s/releases/%s/latest-releases.yaml"%(version,arch)
    print("Fetching releases at %s"%releases_url)
    releases=requests.get(releases_url)
    if releases.status_code!=200:
        print("Alpine version %s with arch %s not found"%(version,arch))
        quit(1)
    releases=yaml.load(releases.text,Loader=yaml.SafeLoader)
    latest_miniroot=next((r['file'] for r in releases if r['flavor'] == "alpine-minirootfs"), None)
    if latest_miniroot is None:
        print("Did not find alpine-minirootfs in releases yaml")
        quit(1)
    rootfs_url="http://dl-cdn.alpinelinux.org/alpine/%s/releases/%s/%s"%(version,arch,latest_miniroot)
    print("Downloading and extracting %s"%rootfs_url)
    run("curl -s %s | tar xfz - -C %s"%(rootfs_url,dir))
    
    print("Praparing rootfs")
    # copy resolv.conf
    run("cat /etc/resolv.conf > %s/etc/resolv.conf"%dir)

    # install some tools
    run_chroot(dir,"apk update")
    run_chroot(dir,"apk add alpine-base openssh-client openssh-server procps bash nano")

    if extra_packages!="":
        run_chroot(dir,"apk add %s"%extra_packages)

    # uninstall "nanddump" and "nandwrite" because it's not used in most cases and conflicts with auto-complete for "nano"
    run_chroot(dir,"apk del mtd-utils-nand")

    # install sshd, enable root login via key
    run_chroot(dir,"rc-update add sshd")
    run_chroot(dir,"sed -i 's/#PermitRootLogin .*/PermitRootLogin without-password/g' /etc/ssh/sshd_config")
    # https://github.com/alpinelinux/docker-alpine/issues/28
    run_chroot(dir,"sed -i -e 's/^root:!:/root:*:/' /etc/shadow")

    # enable minimal syslog
    run_chroot(dir,"rc-update add syslog")

    # create a inittab with without tty login
    writefile(dir,"/etc/inittab",[
        "::sysinit:/sbin/openrc sysinit",
        "::sysinit:/sbin/openrc boot",
        "::wait:/sbin/openrc default",
        "::shutdown:/sbin/openrc shutdown"
        ])

    # cleanup
    run("rm %s/etc/resolv.conf"%dir)
