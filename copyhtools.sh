#!/usr/bin/env bash

if test -z "$1";then
    echo "Error arguments:"
    echo "   $0 IP [PASSWORD]"
    exit 1
fi

list_file() {
    cat <<EOF
#calicoctl
#etcdctl
#ipvsadm
#ixcalc
#kubectl
*.sh
*.py
alias_pykube
hovs
hss
hguess
kube_alias
log_cni
pykube
pydocker
vvm
EOF
}

rm -rf /tmp/htools/
mkdir /tmp/htools
cp -a `list_file |grep -v '^#'|xargs` /tmp/htools/

./hss u "$1" /tmp/htools/ /root/
exec ./hss "$1"
