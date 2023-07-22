#!/usr/bin/env python

from __future__ import print_function
import base64
import sys

op = sys.argv[1]

if op == "-d":
    fn = sys.argv[2]
    i = ""
    with open(fn, "r") as f:
        i = f.read()
        i = i.strip()
        i = i.encode("utf-8")
        print(base64.b32decode(i).decode("utf-8"), end='')
else:
    fn = sys.argv[1]
    i = ""
    with open(fn, "r") as f:
        i = f.read()
        i = i.encode("utf-8")
        print(base64.b32encode(i).decode("utf-8"))
