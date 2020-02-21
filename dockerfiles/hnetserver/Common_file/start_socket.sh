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
    cd /Common_file/
    python TCP_server.py $tcp_port &
}


setup_udp() {
    cd /Common_file/
    python UDP_server.py $udp_port &
}

setup_http() {
    cd /Common_file/
    cp /Common_file/http2.py ./http.py;
    python http.py $http_port &
}

setup_https() {
    cd /Common_file/cert/
    cp /Common_file/http2.py /Common_file/cert/https.py;
    python https.py $https_port
}

setup_port

setup_tcp
setup_udp
setup_http
setup_https

