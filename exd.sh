#!/bin/bash

tmpfile=/tmp/execdocker.txt

declare  -A POD_IP

get_pod_ip() {
    while read pod ip
    do
        POD_IP[$pod]=$ip
    done < <(kubectl get pods --all-namespaces -o wide | awk '{print $2, $7}')
}

get_container_pid() {
    docker inspect -f '{{.State.Pid}}' $1
}

get_docker_pod() {
    let i=1
    while read id pod c
    do
        if [ "$c" = POD ];then
            continue
        fi
        ip=${POD_IP[$pod]}
        pid=$(get_container_pid $id)
        printf "%3d %s %6d %15s  %25s [%3d] %-25s\n" $i $id $pid ${ip:--} $pod $i $c
        ((i++))
    done < <(docker ps --format '{{.ID}}\t\t{{.Label "io.kubernetes.pod.name"}}\t\t{{.Label "io.kubernetes.container.name"}}')
}

exec_docker_shell() {
    local id=$1
    shift
    if test -z "$1";then
        set -- "bash"
    fi
    exec docker exec -it $id "$@"
}

enter_ns() {
    local line=${1#p}
    local pid=$(cat $tmpfile  | awk -v line=$line 'NR==line { print $3}')
    shift
    if test -z "$1";then
        set -- "bash"
    fi
    nsenter -t $pid -n  "$@"
    exit
}

exe_by_index() {
    local id=$(cat $tmpfile  | awk -v line=$1 'NR==line { print $2}')
    shift
    exec_docker_shell "$id" "$@"
    exit
}

exe_by_name() {
    local label=io.kubernetes.container.name
    if [ "$1" = "pod" ];then
        label=io.kubernetes.pod.name
        shift
    fi

    local name=$1
    shift
    f=$(mktemp -u)
    docker ps -f "label=$label=$name" --format '{{.ID}} {{.Label "io.kubernetes.container.name"}}' | grep -v ' POD$' > $f

    count=$(cat $f | wc -l)
    if [ "$count" = "0" ] ;then
        echo "Empty"
        rm -f $f
        exit 1
    elif [ "$count" = "1" ] ;then
        read cid cname <$f
        echo $cid $cname
        rm -f $f
        exec_docker_shell $cid "$@"
        exit
    elif [ "$count" = "2" ] ;then
        cat $f
        rm -f $f
        echo "Too Many"
        exit 1
    fi
    exit
}


if [ "$1" = "" ];then
    get_pod_ip
    get_docker_pod | tee $tmpfile
    exit
fi

if echo "$1" | grep -q '^[0-9]\{1,2\}$' ;then
    exe_by_index "$@"
    exit
elif echo "$1" | grep -q '^p[0-9]\{1,2\}$' ;then
    enter_ns "$@"
    exit
elif [ "$1" = "id" ];then
    shift
    exec_docker_shell "$@"
    exit
elif [ "${1:0:1}" = "/" ];then
    key="${1:1:100}"
    if [ "$key" = cn ];then
        shift
        exe_by_name contiv-netplugin "$@"
    fi
else
    exe_by_name "$@"
fi

