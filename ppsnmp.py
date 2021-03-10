#!/usr/bin/env python

from __future__ import print_function
import time
import os
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-b', type=int, help='batch-mode interval')
parser.add_argument('-e', action='store_true', help='show error count only')
parser.add_argument('-i', action='store_true', help='show increased count only')
parser.add_argument('-p', action='store', help='show specified protocols only')

args = parser.parse_args()

print(args)
batch_interval = args.b if args.b else 0
increase_only = args.i
error_only = args.e
protocols = [] if not args.p else args.p.split(",")
if protocols:
    if "udp" in protocols:
        protocols.append("udplite")
    if "icmp" in protocols:
        protocols.append("icmpmsg")

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

def main_loop(interval=1):
    o = None
    n = None
    while True:
        time.sleep(interval)
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

if batch_interval:
    main_loop(batch_interval)
else:
    print_once()
