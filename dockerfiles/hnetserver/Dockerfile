FROM ubuntu:22.04

LABEL maintainer="Huanle Han <hanxueluo@gmail.com>"

COPY ./sources.list /etc/apt/

RUN set -ex \
    && apt update \
    && apt -y upgrade \
    && apt -y install --no-install-recommends \
    apache2-utils \
    bash \
    dnsutils \
    bird \
    iputils-ping \
    iputils-arping \
    bridge-utils \
    conntrack \
    curl \
    dhcping \
    ethtool \
    file\
    fping \
    iftop \
    iperf \
    iproute2 \
    ipset \
    iptables \
    iptraf-ng \
    ipvsadm \
    mtr \
    procps \
    netcat-openbsd \
    nftables \
    ngrep \
    nmap \
    openssl \
    python3 \
    python3-pip \
    socat \
    strace \
    tcpdump \
    tcptraceroute \
    util-linux \
    wget \
    vim \
    git \
    ssh \
    sshpass \
	&& rm -rf /var/lib/apt/lists/*


RUN cd / && git clone https://github.com/hanxueluo/htools.git && /bin/bash /htools/init_bin.sh
ENV PATH="$PATH:/htools/bin/"

ADD Common_file /Common_file

WORKDIR /Common_file

ENTRYPOINT ["bash", "/Common_file/start_socket.sh"]
