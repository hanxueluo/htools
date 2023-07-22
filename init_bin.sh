#!/bin/bash

list_files() {
cat <<EOF
cmdindex.py
cmdtool.py

develop/codews
develop/diffgbranch.py
develop/gogitclone
develop/mgit

#k8s/hetctl.sh
#k8s/log_cni
#k8s/logindocker

#container/cvim
#container/cvm

#net/hipt.sh
#net/hovs
#net/ppsnmp.py
#net/vxlandump.sh

ssh/hguess
ssh/hss
ssh/hto
ssh/kss

k8s/kwatchdiff.py
k8s/pycrictl
k8s/pydocker
k8s/pykube
EOF

}


cd $(dirname $0)
mkdir -p ./bin

while read line
do
    p=../$line
    f=$(basename $p)
    echo ln -s $p ./bin/$f
    ln -s $p ./bin/$f
done < <(list_files |grep -v '^#' |grep -v '^ *$')

