#!/bin/bash

CA=/etc/kubernetes/etcd/ca.crt
CRT=/etc/kubernetes/etcd/etcd.crt
KEY=/etc/kubernetes/etcd/etcd.key
BIN=/usr/local/etcd/bin/etcdctl

if test -f $CA && test -f $CRT && test -f $KEY;then
    :
else
    CA=/etc/kubernetes/pki/etcd/ca.crt
    CRT=/etc/kubernetes/pki/apiserver-etcd-client.crt
    KEY=/etc/kubernetes/pki/apiserver-etcd-client.key
fi

if which $BIN >/dev/null 2>/dev/null;then
    :
else
    BIN=etcdctl
fi

_etcdctl() {
	ETCDCTL_API=3 $BIN \
		--cacert $CA \
		--cert $CRT \
		--key $KEY \
		"$@"
}

_etcdctl "$@"


