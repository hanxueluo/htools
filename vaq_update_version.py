#!/usr/bin/env python3

import sys
import os
import re

#os.chdir("/Users/huanle/gitwt/vaquita_net")
DICT_ = """
roles/network/defaults/main.yml bridge_vlan_version bridge-vlan
roles/network/defaults/main.yml fixedip_ipam_version fixedip-ipam-server
roles/network/defaults/main.yml multus_cni_version multus-cni
roles/network/defaults/main.yml network_agent_version network-agent

roles/network/defaults/main.yml canal_flannel_version flannel
roles/network/defaults/main.yml canal_calico_version calico-pod2daemon-flexvol
roles/network/defaults/main.yml calico_version calico-node

roles/loadbalancer/defaults/main.yml ingress_ipvsdr_image loadbalancer-provider-ipvsdr
roles/loadbalancer/defaults/main.yml ingress_sidecar_image loadbalancer-provider-ingress

roles/loadbalancer/defaults/main.yml ingress_controller_image nginx-ingress-controller
"""

def get_dict():
    d = {}
    for l in DICT_.strip().splitlines():
        if not l:
            continue
        f, v, i = l.split()
        d[i] = (f, v)
    return d


def parse_image_list():
    fn = "image_list/image.list"
    ls = []
    with open(fn, "r") as f:
        for l in f.readlines():
            l = l.strip()
            if not l:
                continue
            k, version = l.split(":", 1)
            k = k.split('/')[-1]
            ls.append((k, version.strip()))
    return ls

def check_files(d, ls):
    def get_version(k):
        res = []
        for l in ls:
            if l[0] == k:
                res.append(k[1])
        return res

    a = get_version("fixedip-ipam-server")
    b = get_version("fixedip-ipam-client")
    if not (len(a) == 1 and len(b) == 1 and a[0] == b[0]):
        print("Error: unequal version of fixedip-ipam", a, b)

    a = get_version("loadbalancer-provider-ipvsdr")
    b = get_version("loadbalancer-provider-ingress")
    if not (len(a) == 1 and len(b) == 1 and a[0] == b[0]):
        print("Error: unequal version of lb-provider")
    print("Finish check")


def update_content(lines, kvs):
    newlines = []
    for l in lines:
        for k, version in kvs:
            if l.startswith(k):
                pattern = r'^(%s:.*)(\bv[0-9]+\..+)([$"])' % k
                replacement = r'\1%s\3' % version

                if k == 'ingress_controller_image':
                    pattern = r'^(%s:.*)(:[0-9]+\..+)([$"])' % k
                    replacement = r'\1:%s\3' % version
                newl = re.sub(pattern, replacement, l)
                if l != newl:
                    print("Updating:", l)
                    print("         ", newl)
                l = newl
                break
        newlines.append(l)
    return newlines


def update_files(d, ls, checkonly=True):
    fmap = {}
    for i, version in ls:
        fv = d.get(i)
        if not fv:
            continue
        fmap.setdefault(fv[0], []).append((fv[1], version))

    newlines = []
    for fn, kvs in fmap.items():
        lines = []
        with open(fn, "r") as f:
            lines = list(f.read().splitlines())
        newlines = update_content(lines, kvs)
        if newlines and not checkonly:
            with open(fn, "w") as f:
                f.write("\n".join(newlines)+"\n")

d = get_dict()
ls = parse_image_list()

update_files(d, ls, False)
check_files(d, ls)
