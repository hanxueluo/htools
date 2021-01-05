#!/usr/bin/env python3

import time
import socket

def parse_as_header(data):
    data2 = {}
    for a in data.splitlines():
        kvs = [a]
        if ";" in a:
            kvs = a.strip().split(";")
        for kv in kvs:
            kvlist = kv.strip().split("=", 1)
            if len(kvlist) == 2:
                data2[kvlist[0].strip()] = kvlist[1].strip()
    return data2

def get_content(proto, infos, peer, me, kvs):
    status = 200

    s = "Host: %s\n" % socket.gethostname()
    s += "C->S: %s -> %s\n" % (peer, me)
    s += "Proto: %s\n" % proto

    for k,v in infos:
        s += "%s: %s\n" % (k, v)

    s += "  Head:\n"
    for k, v in kvs.items():
        s += "    %s: %s\n" % (k, v)
        if k.upper() == "HTTPSTATUS":
            status = int(v) if v.isdigit() else 400

    l = kvs.get("L", "")
    if l.isdigit():
        s += "=" * int(l)
        s += "\n"

    l = kvs.get("SLEEP", "")
    if l.isdigit():
        print(" ** sleeping", l)
        time.sleep(int(l))

    s = "<html><body><pre>\n%s\n</pre></body></html>\n" % s

    return status, s.encode("utf-8"), kvs
