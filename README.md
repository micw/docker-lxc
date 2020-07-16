# Running stateful linux containers in docker

> [!WARNING]
> This is a complete rewrite, using LXC only without vagrant. It is able to run LXC containers created with v0.1 but
> config and usage differs. Use tag v0.1 to get the old version.

## Why?

In some cases, it might be usefull to run full-blown operating systems in a docker environment which have "state", primarily meaning to have a persitent root volume. With docker only, this is not possible since docker does not allow / to be a volume. This is where LXC comes into play. LXC provides a process isolation similar to docker but with statefull root filesystems. Unfortunately, with the rise of docker, management tools for docker are much more widespread and sophisticated than those for LXC.

This project allows to use a single LXC container within a docker container to get best of both worlds.

## Features

* Runs a single LXC container in docker with full OS and persistent root
* Use features unique to docker for your lxc containers (e.g. docker-compose, exposed ports, traefik for ingress, kubernetes as platform)
* The LXC container uses the same limits and network stack as the docker container, so things like exposed ports works as expected
* Proper signal handling in both directions (shutting down the docker container properly shuts down the LXC container. Poweroff in LXC shuts down the docker container)
* LXCFS support: Within the container, uptime and limits are displayed correctly
* Shell-Wrapper: If /bin/sh is invoked with "docker exec", a shell in the LXC container is spawned. So a console in most management tools opens directly within the LXC container, not in the surrounding docker container
* Creation of initial root filesystems: for some distributions, a root filesystem can simply be set, using an environment variable
* Adding of initial SSH key via environment variable


## How to run

docker run -d \
  --name lxc \
  --privileged  \
  --hostname lxctest1
  -v /path/to/data:/data \
  -e DISTRIBUTION=alpine \
  -e INITIAL_SSH_KEY="ssh-rsa AAAA...Q== my-initial-ssh-key" \
  micwy/lxc

* "privileged" is currently required to run LXC on the container
* The hostname is passed into the lxc container
* The volume /data contains the root filesystem (under /data/rootfs) and some additional files (temporary root fs during system creation, lxc config)

### Environment variables

* DISTRIBUTION: triggers a distribution specific setup script if /data/rootfs does not exist (see below)
* INITIAL_SSH_KEY: if set, it is copied to /root/.ssh/authorized keys on startup if that file does not exist yet
* USE_LXCFS (default true): if true, mount [LXCFS](https://github.com/lxc/lxcfs) into the LXC container
* COPY_RESOLV_CONF (default true): if true, copy resolv.conf from docker container into the LXC container

### Available distribution setup scripts

#### DISTRIBUTION: alpine

Installs alpine if rootfs does not exist.

Features:
* Quite minimal image with bash, nano and openssh

* ALPINE_ARCH: (default x86_64): architecture of the rootfs
* ALPINE_VERSION: (default latest-stable): alpine version to install
* ALPINE_EXTRA_PACKAGES: additional packages to install along with the rootfs



