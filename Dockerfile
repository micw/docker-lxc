FROM alpine:latest

RUN \
  apk add --update --no-cache bash curl lxc lxcfs python3 py3-requests py3-yaml arch-install-scripts tar zstd \
  && echo "lxc.lxcpath = /data" > /etc/lxc/lxc.conf \
  && ln -sf /scripts/shellwrapper /bin/sh \
  && echo "PS1='\\h (outer docker container, to enter inner container use: lxc-attach -n machine) \\w # '" > /root/.bashrc

ADD scripts /scripts

VOLUME /data /vol

CMD ["/usr/bin/python3","/scripts/launch.py"]
