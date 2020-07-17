#!/usr/bin/env python3

import os
import subprocess
import requests
import yaml
from urllib.request import urlopen
from lxcutil import *

def install_to(dir):

    extra_packages=os.environ.get("ARCHLINUX_EXTRA_PACKAGES","")
    install_trizen=os.environ.get("ARCHLINUX_INSTALL_TRIZEN","true")=="true"
    mirrorlist_country=os.environ.get("ARCHLINUX_MIRRORLIST_COUNTRY","Germany")

    print("Setting up pacman")
    writefile("/etc","pacman.conf",[
            "[core]",
            "Server = http://ftp.tu-chemnitz.de/pub/linux/archlinux/$repo/os/$arch",
            "[extra]",
            "Server = http://ftp.tu-chemnitz.de/pub/linux/archlinux/$repo/os/$arch",
            "[community]",
            "Server = http://ftp.tu-chemnitz.de/pub/linux/archlinux/$repo/os/$arch",
        ],"a")
    
    run("curl -s -L https://www.archlinux.org/packages/core/any/archlinux-keyring/download/ | tar xf - --zstd -C / usr/share/pacman/")
    run("pacman-key --init")
    run("pacman-key --populate archlinux")

    print("Preparing rootfs")
    run(("pacstrap -c -G -M %s pacman "
         "filesystem systemd-sysvcompat bash bzip2 coreutils "
         "diffutils file findutils gawk gcc-libs gettext glibc "
         "grep gzip inetutils iproute2 less licenses logrotate "
         "netctl pacman procps-ng psmisc s-nail sed shadow "
         "sysfsutils tar util-linux which "
         "reflector pacman-contrib "
         "sudo openssh ca-certificates curl wget python-simplejson git base-devel "
         "pacutils perl perl-libwww perl-term-ui perl-json "
         "perl-data-dump perl-lwp-protocol-https perl-term-readline-gnu "
         "perl-json-xs")%dir)

    # copy resolv.conf
    run("cat /etc/resolv.conf > %s/etc/resolv.conf"%dir)

    # update certs
    run_chroot(dir,"trust extract-compat")

    # prepare pacman
    run_chroot(dir,"pacman-key --init")
    run_chroot(dir,"pacman-key --populate archlinux")

    # generate package mirrors
    run_chroot(dir,"reflector --verbose --age 12 --country '%s' --sort rate --protocol http --protocol https --save /etc/pacman.d/mirrorlist"%mirrorlist_country)

    run_chroot(dir,"systemctl enable sshd")

    # enable sudoers includes
    run_chroot(dir,"sed -i 's|#includedir /etc/sudoers.d|#includedir /etc/sudoers.d|' /etc/sudoers")

    # don't check space (does not work in chroot)
    run_chroot(dir,"sed -i 's/CheckSpace/#CheckSpace/' /etc/pacman.conf")

    if install_trizen:
        print("Installing trizen package manager")

        # enable the nobody user to install with trizen and sudo
        writefile(dir,"/etc/sudoers.d/nobody","nobody ALL=(ALL) NOPASSWD: ALL")
        run_chroot(dir,"usermod -d /tmp nobody")

        run_chroot(dir,"su - nobody -s /bin/sh -c 'git clone https://aur.archlinux.org/trizen.git /tmp/trizen && cd /tmp/trizen && makepkg -si --noconfirm'")

    if extra_packages!="":
        if install_trizen:
            run_chroot(dir,"su - nobody -s /bin/sh -c 'trizen -Sy --noconfirm %s'"%extra_packages)
        else:
            run_chroot(dir,"pacman -Sy --noconfirm %s"%extra_packages)

    # cleanup
    run("rm -f %s/etc/resolv.conf"%dir)
    run_chroot(dir,"sed -i 's/#CheckSpace/CheckSpace/' /etc/pacman.conf")

    if install_trizen:
        # remove extra permissions from nobody user
        run_chroot(dir,"usermod -d / nobody")
        run("rm -f %s/etc/sudoers.d/nobody"%dir)
