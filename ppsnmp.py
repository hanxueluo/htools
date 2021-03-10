#!/usr/bin/env python
# -e #error-only
# -i #increase-only
# -o #run-once
# -p xx,yy,zz #select-protocols

from __future__ import print_function
import time
import os

def read_snmp(fn):
    d = ""
    with open(fn, "r") as f:
        d = f.read()
    return d

def write_snmp(fn, d):
    with open(fn, "w") as f:
        f.write(d)


def extract_data(d):
    groups = {}
    g = []
    for l in d.splitlines():
        g.append(l.split())
        if len(g) == 1:
            continue
        g2, g = g, []
        kvs = {}
        for k,v in zip(g2[0], g2[1]):
            if k.endswith(":"):
                continue
            kvs[k] = int(v)
        groups[g2[0][0].lower().strip(":")] = kvs
    return groups

def delta_data(g1, g2):
    d = {}
    for p, l1 in g1.iteritems():
        l2 = g2[p]
        lx = {}
        d[p] = lx
        for k, v1 in l1.iteritems():
            v2 = l2[k]
            lx[k] = v2 - v1
    return d

def is_error(v):
    return "Fail" in v or "Err" in v or "No" in v or \
        "Timeout" in v or "Unknown" in v or "Discard" in v or \
        "Rst" in v or "Retrans" in v or \
        "Unreach" in v or "TimeExcds" in v

def print_d(d):
    increase_only = False
    error_only = True
    protocols = []

    s = "==============\n"
    for p,l in sorted(d.iteritems()):
        if protocols and p not in protocols:
            continue
        s2 = ""
        for k,v in sorted(l.iteritems()):
            if increase_only and v == 0:
                continue
            if error_only and not is_error(k):
                continue
            s2 += "  %-17s %-10s\n"%(k, v)
        if s2:
            s += p + ":\n" + s2
    print(s.strip())

def main_loop():
    o = None
    n = None
    while 1:
        time.sleep(1)
        n = extract_data(read_snmp("/proc/net/snmp"))
        if o is not None:
            d = delta_data(o, n)
            print_d(d)
        o, n = n, None
    
def print_once():
    nd = read_snmp("/proc/net/snmp")

    tmpfile = "/tmp/proc.net.snmp"
    if not os.path.isfile(tmpfile):
        write_snmp(tmpfile, nd)

    od = read_snmp(tmpfile)
    write_snmp(tmpfile, nd)

    o = extract_data(od)
    n = extract_data(nd)
    d = delta_data(o, n)
    print_d(d)

#print_once()
main_loop()
