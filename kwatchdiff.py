#!/usr/bin/env python
import sys
import difflib
import time
import subprocess

IDENTIFY_LINE=None


items = []

def diff_last_two(l):
    if len(l) < 2:
        return
    i = len(l) - 2
    j = len(l) - 1
    for line in l[i].diff(l[j]):
        sys.stdout.write(line.rstrip("\n") + "\n")
        sys.stdout.flush()

def ignore_line(line):
    return line.lstrip().startswith("resourceVersion:")

class Obj(object):
    def __init__(self):
        super(Obj, self).__init__()
        self.uid = ""
        self.time = time.strftime('%H:%M:%S',time.localtime(time.time()))
        self.idx = -1
        self.lines = []

    def get_id(self):
        return "%3d %s %s" % (self.idx, self.time, self.uid)

    def diff(self, other):
        return difflib.unified_diff(self.lines, other.lines, fromfile=self.get_id(), tofile=other.get_id())

class Watcher(object):
    def __init__(self, handle_diff=diff_last_two):
        super(Watcher, self).__init__()
        self.objs = {}
        self.uncommited_obj = Obj()
        self.handle_diff = diff_last_two

    def commit(self):
        if not self.uncommited_obj.lines:
            return
        if self.uncommited_obj.uid:
            v = self.objs.setdefault(self.uncommited_obj.uid, [])
            v.append(self.uncommited_obj)
            v[-1].idx = len(v) - 1
            self.handle_diff(v)
        else:
            print "== incomplete obj"
        self.uncommited_obj = Obj()

    def feed(self, line):
        global IDENTIFY_LINE

        line = line.rstrip("\n")

        if IDENTIFY_LINE is None:
            IDENTIFY_LINE = line

        if line == IDENTIFY_LINE:
            self.commit()

        if not ignore_line(line):
            self.uncommited_obj.lines.append(line)
            if line.startswith("  uid:"):
                self.uncommited_obj.uid = line.split(":", 1)[-1].strip()

def main():
    wd = Watcher()
    while True:
        try:
            line = sys.stdin.readline()
        except:
            break
        if not line: break

        wd.feed(line)

    wd.commit()

main()


