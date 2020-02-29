#!/bin/sh
hostname=`cat /etc/hostname`

port_suffix=$1

print_arg() {
    cat <<EOF
== args:
    TCP_PORT: $TCP_PORT
    UDP_PORT: $UDP_PORT
    HTTP_PORT: $HTTP_PORT
    HTTPS_PORT: $HTTPS_PORT
    FG_CMD: $FG_CMD
    BG_CMD: $BG_CMD
EOF
    echo '== address:'
    ip addr |grep inet |awk '{print $2}' |grep -v '^127.0.0.1\|fe80::'
}

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
    echo '== port:'
    echo tcp: $tcp_port, udp: $udp_port, http: $http_port, https: $https_port
}

setup_tcp() {
    cd /Common_file/
    python TCP_server.py $tcp_port &
}

setup_tcp_stream() {
    let p=$tcp_port+1
    cd /Common_file/
    echo /usr/bin/socat -v TCP-LISTEN:$p,fork,reuseaddr  exec:'/bin/cat'
    /usr/bin/socat -v TCP-LISTEN:$p,fork,reuseaddr  exec:'/bin/cat' &
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

setup_fg_cmd() {
    cd /Common_file/
    if [ -z "$FG_CMD" ];then
        return
    fi
    echo FG_CMD: $FG_CMD
    eval $FG_CMD &
}

setup_bg_cmd() {
    cd /Common_file/
    if [ -z "$BG_CMD" ];then
        return
    fi
    echo BG_CMD: $BG_CMD
    eval $BG_CMD &
}


print_arg

setup_port
echo '== ====='

setup_fg_cmd
setup_bg_cmd

setup_tcp
setup_tcp_stream
setup_udp
setup_http
setup_https

