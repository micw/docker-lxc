This docker container creates, provisions and runs a stateful lxc container using vagrant-lxc.

Advantages:
* Have statefull full-os containers on a docker environment
* Use features unique to docker for your lxc containers (e.g. docker-compose, exposed ports, traefik for ingress, kubernetes as platform)

Features:
* Initialize the lxc-container with a preexisting image on first start
* Run ansible provisioner if "playbook.yml" exist on the data directory
* Runs lxc directly on the docker container's network, so no special bridge is required for lxc
* shutdown signal handler that gracfully stops the lxc container on docker stop

Todos/Ideas:
* check if it's possible to run in an unprivileged container
* bind-mount docker's /etc/hosts to get service discovery
* Inherit the container's hostname?

