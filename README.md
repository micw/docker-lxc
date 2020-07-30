# Running stateful linux containers in docker ![](https://img.shields.io/docker/pulls/micwy/lxc.svg?v_DATE)

> :warning: This is a complete rewrite, using LXC only without vagrant. It is able to run LXC containers created with v0.1 but
> config and usage differs. Use tag v0.1 to get the old version.

Docker Hub: [micwy/lxc](https://hub.docker.com/r/micwy/lxc) 

I'm very impressed, how much pulls this image gets. Please let me know how you use this (just create an issue at github), I'll add this to the "Use-Cases" section.

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
* Creation of initial root filesystems: for some distributions, an initial root filesystem can simply be set up, using an environment variable
* Adding of initial SSH key via environment variable to get instant log-in

### Some Use-Cases

* Provide "home containers" for your users, each with own ssh access and persistent state
* Run a linux remote desktop server on kubernetes
* Easily run statefull software (like froxlor control panel or plesk) on docker/kubernetes

### Ideas / Backlog

* Support more distribution root filesystems
* Import rootfs from vagrant-lxc boxes

## How to run

```
docker run -d \
  --name lxc \
  --privileged  \
  --hostname lxctest1 \
  -v /path/to/data:/data \
  -v /path/to/somedir:/vol/somedir \
  -e DISTRIBUTION=alpine \
  -e INITIAL_SSH_KEY="ssh-rsa AAAA...Q== my-initial-ssh-key" \
  micwy/lxc
 ```

* "privileged" is currently required to run LXC on the container
* The hostname is passed into the lxc container
* The volume /data contains the root filesystem (under /data/rootfs) and some additional files (temporary root fs during system creation, lxc config)

### Running on Kubernetes

Here's an example yaml to run this on kubernetes. If there's some interest, I can also provide a helm chart.

```
---
# Source: lxc/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mylxcbox
  labels:
    app.kubernetes.io/name: lxc
    app.kubernetes.io/instance: mylxcbox
spec:
  replicas: 
  selector:
    matchLabels:
      app.kubernetes.io/name: lxc
      app.kubernetes.io/instance: mylxcbox
  template:
    metadata:
      labels:
        app.kubernetes.io/name: lxc
        app.kubernetes.io/instance: mylxcbox
    spec:
      containers:
        - name: lxc
          image: "micwy/lxc:latest"
          imagePullPolicy: Always
          # Required to launch lxc containers in the docker container
          securityContext:
            privileged: true
          # Required to make LXC console work
          stdin: true
          tty: true
          ports:
            - name: ssh
              containerPort: 22
              protocol: TCP
              hostPort: 2201
          env:
            - name: "DISTRIBUTION"
              value: "archlinux"
            - name: "INITIAL_SSH_KEY"
              value: "ssh-rsa ...DVs= my-ssh-key"
          volumeMounts:
            - mountPath: /data
              name: data
      # Will be passed into the lxc container
      hostname: mylxcbox
      volumes:
      - name: data
        hostPath:
          path: /data/mylxcbox
  # Strategy must be recreate if hostPort is used
  strategy:
    type: Recreate

```

### Environment variables

* DISTRIBUTION: triggers a distribution specific setup script if /data/rootfs does not exist (see below)
* INITIAL_SSH_KEY: if set, it is copied to /root/.ssh/authorized keys on startup if that file does not exist yet
* USE_LXCFS (default false): if true, mount [LXCFS](https://github.com/lxc/lxcfs) into the LXC container
    * :warning: May not work with systemd!
* COPY_RESOLV_CONF (default true): if true, copy resolv.conf from docker container into the LXC container

### Additional volumes

* the directory /vol of the docker container is mounted with "rbind" into /vol on the LXC container
* Every docker-volume that is mounted to /vol/something will appear as /vol/something on LXC

### Available distribution setup scripts

#### DISTRIBUTION: alpine

Installs alpine if rootfs does not exist.

Features:
* Quite minimal image with bash, nano and openssh

Supported environment variables:
* ALPINE_ARCH: (default x86_64): architecture of the rootfs
* ALPINE_VERSION: (default latest-stable): alpine version to install
* ALPINE_EXTRA_PACKAGES: additional packages to install along with the rootfs

#### DISTRIBUTION: archlinux

Installs archlinux if rootfs does not exist.

Features:
* Basic system image with common tools and openssh

Supported environment variables:
* ARCHLINUX_INSTALL_TRIZEN: (default: true): if true, install the trizen package manager for AUR packages
* ARCHLINUX_EXTRA_PACKAGES: additional packages to install along with the rootfs. Installation will be run with trizen if installed, otherwise with pacman
* ARCHLINUX_MIRRORLIST_COUNTRY (default: Germany - I confess, I'm biased): Country to use for create an initial packman mirror list
