FROM alpine

RUN apk add --update --no-cache lxc lxc-templates bash curl tar xz ruby-full sudo libarchive-tools && \
    curl -s https://releases.hashicorp.com/vagrant/2.1.2/vagrant_2.1.2_x86_64.tar.xz | \
      tar xfJ - --warning=no-unknown-keyword -C / opt/vagrant && \
    /opt/vagrant/bin/vagrant plugin install vagrant-lxc

RUN /opt/vagrant/bin/vagrant box add debian/jessie64 --provider lxc

ADD machine/ /opt/machine/

WORKDIR /opt/machine

CMD /opt/machine/entrypoint.sh
