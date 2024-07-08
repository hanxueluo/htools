#!/usr/bin/env python3
import os
import subprocess
import re
import sys
from typing import List, Dict, Tuple, Set

def execute(cmd: str or List[str]) -> Tuple[int, str, str]:
    print(cmd)
    shell = isinstance(cmd, str)
    p = subprocess.Popen(cmd, shell=shell, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()
    return (p.returncode, stdout, stderr)

def simple_line(msg: str, b: str) -> str:
    if b.startswith('origin/'):
        b = b.split('/', 1)[1]
    m0 = msg
    msg = msg.split(" ", 1)[1].strip()
    msg = re.sub(r"^\([^()]*\)", "", msg).strip() # remove tag decorate
    msg = msg.replace("[%s]" % b, "").strip() # remove current branch decorate
    #msg = msg.replace("\[[-\w\d\./]+\]", "").strip() # remove all branch decorate
    msg = re.sub(r"#\d+", "", msg).strip() # remove pr number
    msg = re.sub(r"\(\)", "", msg).strip()
    return msg

def simple_msg(logs: List[str], b: str) -> List[str]:
    res = []
    for msg in logs:
        res.append(simple_line(msg, b))
    return res

def diff_log(l1: List[str], b1: str, l2: List[str], b2: str) -> Tuple[List[str], List[str]]:
    res1 = []
    res2 = []

    simple_l1 = simple_msg(l1, b1)
    simple_l2 = simple_msg(l2, b2)

    for l in l1:
        m = simple_line(l, b1)
        if m not in simple_l2:
            res1.append(l)
    for l in l2:
        m = simple_line(l, b2)
        if m not in simple_l1:
            res2.append(l)
    return res1, res2

def diff_branch(b1: str, b2: str, args: str):

    if args == "":
        args = "@V"
    elif "@V" not in args:
        args = "@V " + args

    postfix = args.replace("@V", "%s..%s"%(b1, b2))
    _, log1, err =  execute("git log --oneline --decorate=short %s" % postfix)
    log1 = log1.splitlines()

    postfix = args.replace("@V", "%s..%s"%(b2, b1))
    _, log2, err =  execute("git log --oneline --decorate=short %s" % postfix)
    log2 = log2.splitlines()

    r1, r2 = diff_log(log1, b2, log2, b1)
    print("======== %-10s ======= %d" % (b2, len(log1)))
    print("\n".join(r1))
    print("======== %-10s ======= %d" % (b1, len(log2)))
    print("\n".join(r2))



argv = sys.argv[:]
b1=argv[1]
b2=argv[2]

args = " ".join(argv[3:])

diff_branch(b1, b2, args)
