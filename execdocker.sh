#!/bin/bash

tmpfile=/tmp/execdocker.txt

exec_docker_shell() {
    [ -z "$SHELL" ] && SHELL=bash
    exec docker exec -it $1 $SHELL
}

if [ "$1" = "" ];then
    docker ps --format '{{.ID}}\t\t{{.Label "io.kubernetes.pod.name"}}\t\t{{.Label "io.kubernetes.container.name"}}' \
        | grep -v '\sPOD$' |cat -n | tee $tmpfile
    exit
fi

if [ "$1" = "id" ];then
    exec_docker_shell $2
    exit
fi

if echo "$1" | grep -q '^[0-9]\{1,2\}$' ;then
    id=$(cat $tmpfile  | awk -v line=$1 'NR==line { print $2}')
    exec_docker_shell $id
    exit
fi

label=io.kubernetes.container.name
if [ "$1" = "pod" ];then
    label=io.kubernetes.pod.name
    shift
fi

name=$1
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
    exec_docker_shell $cid
elif [ "$count" = "2" ] ;then
    cat $f
    rm -f $f
    echo "Too Many"
    exit 1
fi

exit
