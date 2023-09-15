#!/bin/bash
#docker run --privileged  --hostname lxctest1 -v /tmp/lxc:/data -e USE_LXCFS=false -e DISTRIBUTION=alpine lxc
docker run --privileged  --hostname lxctest1 -v /tmp:/data -e USE_LXCFS=false -e DISTRIBUTION=alpine -it lxc ash
#/usr/bin/python3 /scripts/launch.py
