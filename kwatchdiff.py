#!/usr/bin/env python
from __future__ import print_function
import sys
import difflib
import time
import subprocess
import datetime
import threading
import time

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
    return line.lstrip().startswith("resourceVersion:") or line == "---"

class Obj(object):
    def __init__(self):
        super(Obj, self).__init__()
        self.uid = ""
        self.ns = ""
        self.name = ""
        self.time = time.strftime('%H:%M:%S',time.localtime(time.time()))
        self.idx = -1
        self.lines = []

    def get_id(self):
        return "%3d %s %s %s/%s" % (self.idx, self.time, self.uid, self.ns, self.name)

    def diff(self, other):
        return difflib.unified_diff(self.lines, other.lines, fromfile=self.get_id(), tofile=other.get_id())

class Watcher(object):
    def __init__(self, handle_diff=diff_last_two):
        super(Watcher, self).__init__()
        self.objs = {}
        self.uncommited_obj = Obj()
        self.handle_diff = diff_last_two
        self.lock = threading.Lock()
        self.last_time = datetime.datetime.now()
        self.start_commit_timer()

    def start_commit_timer(self):
        def timer_thread():
            while True:
                time.sleep(0.2) # sleep 1s
                self.commit_with_lock(timeout=1)

        timer_thread = threading.Thread(target=timer_thread)
        timer_thread.daemon = True  # 将线程设置为守护线程，这样程序退出时会自动结束定时器线程
        timer_thread.start()

    def commit_with_lock(self, timeout=-1):
        last_time = datetime.datetime.now()
        with self.lock:
            if (last_time - self.last_time).total_seconds() >= timeout:
                self._commit()
                self.last_time = last_time

    def _commit(self):
        if not self.uncommited_obj.lines:
            return
        if self.uncommited_obj.uid:
            v = self.objs.setdefault(self.uncommited_obj.uid, [])
            v.append(self.uncommited_obj)
            v[-1].idx = len(v) - 1
            self.handle_diff(v)
        else:
            print("== incomplete obj", "\n".join(self.uncommited_obj.lines))
        self.uncommited_obj = Obj()

    def feed_with_lock(self, line):
        with self.lock:
            self._feed(line)
            self.last_time = datetime.datetime.now()

    def _feed(self, line):
        global IDENTIFY_LINE

        line = line.rstrip("\n")

        if IDENTIFY_LINE is None:
            IDENTIFY_LINE = line

        if line == IDENTIFY_LINE:
            print("============= ", datetime.datetime.now(), "= feed new object")
            self._commit()

        if not ignore_line(line):
            self.uncommited_obj.lines.append(line)
            if line.startswith("  uid:"):
                self.uncommited_obj.uid = line.split(":", 1)[-1].strip()
            elif line.startswith("  namespace:"):
                self.uncommited_obj.ns = line.split(":", 1)[-1].strip()
            elif line.startswith("  name:"):
                self.uncommited_obj.name = line.split(":", 1)[-1].strip()

def run():
    wd = Watcher()
    while True:
        try:
            line = sys.stdin.readline()
        except:
            break
        if not line: break

        wd.feed_with_lock(line)

    wd.commit_with_lock()

if __name__ == "__main__":
    run()


