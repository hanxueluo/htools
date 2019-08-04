#!/bin/sh
hostname=`cat /etc/hostname`

port_suffix=$1

setup_port() {
    tcp_port=${TCP_PORT:-$PORT}
    udp_port=${UDP_PORT:-$PORT}
    http_port=${HTTP_PORT:-$PORT}
    https_port=${HTTPS_PORT:-$PORT}

    if [ "$port_suffix" != "" ];then
        tcp_port=${tcp_port:-6$port_suffix}
        udp_port=${udp_port:-7$port_suffix}
        http_port=${http_port:-8$port_suffix}
        https_port=${https_port:-9$port_suffix}
    else
        tcp_port=${tcp_port:-60}
        udp_port=${udp_port:-70}
        http_port=${http_port:-80}
        https_port=${https_port:-443}
    fi
    echo tcp: $tcp_port, udp: $udp_port, http: $http_port, https: $https_port
}

setup_tcp() {
    mkdir /TCP
    cd /TCP/
    cp /Common_file/TCP_server.py ./
    touch index.html
    echo "TCP socket from $hostname" > index.html
    python TCP_server.py $tcp_port &
}


setup_udp() {
    mkdir /UDP; cd /UDP/;
    cp /Common_file/UDP_server.py ./;
    touch index.html; echo "UDP socket from $hostname" > index.html;
    python UDP_server.py $udp_port &
}

setup_http() {
    mkdir /HTTP/ && cd /HTTP/
    cp /Common_file/http2.py ./http.py;
    python http.py $http_port &
}

setup_https() {
    mkdir /HTTPS && cd /HTTPS/
    cp /Common_file/http2.py ./https.py;
    cp /Common_file/cert/* ./;
    python https.py $https_port
}

setup_port

setup_tcp
setup_udp
setup_http
setup_https

