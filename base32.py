#!/usr/bin/python
import base64
import sys

op = sys.argv[1]

if op == "-d":
    fn = sys.argv[2]
    i = ""
    with open(fn, "r") as f:
        i = f.read()
        i = i.strip()
        print base64.b32decode(i),
else:
    fn = sys.argv[1]
    i = ""
    with open(fn, "r") as f:
        i = f.read()
        print base64.b32encode(i)
        #print base64.b32encode(i).lower(),
