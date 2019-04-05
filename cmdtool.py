#!/usr/bin/env python

import os
import subprocess
import sys
import re

################################

class Utility:

    @staticmethod
    def print_to_stderr(message, newilne=True):
        print >> sys.stderr, "# ", message,
        if newilne:
            print >> sys.stderr, ""
        sys.stderr.flush()

    @staticmethod
    def write_file(filename, content):
        try:
            with open(filename, "w") as f:
                f.write(content)
        except:
            pass

    @staticmethod
    def read_file(filename):
        content = ""
        try:
            with open(filename, "r") as f:
                content = f.read()
        except:
            pass
        return content

    @staticmethod
    def execute(cmd, stdio=False):
        shell = isinstance(cmd, str)
        if stdio:
            p = subprocess.Popen(cmd, shell=shell, close_fds=True)
            stdout, stderr = p.communicate()
            stdout = ""
        else:
            p = subprocess.Popen(cmd, shell=shell, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
            stdout, stderr = p.communicate()
	#if p.returncode != 0:
	#    logging.error('Failed to execute cmd: %s :%s', cmd, stderr.strip())
	#else:
	#    in_ = ' < %s ' % input_ if input_ else ''
	#    logging.debug('Successful to execute cmd: %s %s:%s', cmd, in_, stdout.strip())
	return (p.returncode, stdout, stderr)

class CmdOption(object):
    def __init__(self, raw):
        super(CmdOption, self).__init__()
        self.raw = raw

    def dupliacte(self, raw):
        return type(self)(raw)

    def _get_option(self, arg):
        i, _next = -1, None
        try:
            i = self.raw.index(arg)
            _next = self.raw[i+1]
            if _next.startswith("-"):
                _next = None
        except:
            pass
        if i < 0:
            for ii, a in enumerate(self.raw):
                if a.startswith(arg):
                    i = ii
                    _next = a[len(arg):].lstrip("=")
                    break
        return i, _next

    def has(self, arg, arg2=None):
        i, b = self._get_option(arg)
        if i < 0:
            return False
        return arg2 is None or arg2 == b

    def get(self, arg):
        _, b = self._get_option(arg)
        return b

    def remove_arg(self, arg):
        raw = self.raw[:]
        i, _next = self._get_option(arg)
        if _next is not None:
            if raw[i] != arg and len(raw) > i+1:
                del raw[i+1]
            del raw[i]
        elif i>= 0:
            del raw[i]
        return self.dupliacte(raw)

    def reset_arg(self, arg, arg2=None):
        op = self.remove_arg(arg)
        op.raw.append( arg if arg2 is None else arg + arg2 )
        return op

class KubeOption(CmdOption):
    def __init__(self, raw):
        super(KubeOption, self).__init__(raw)

    def get_output(self):
        _, output = self._get_option("-o")
        return  "" if output is None else output

    def is_list(self, output=None):
        if output is None:
            output = self.get_output()
        return not (output.startswith("yaml") or output.startswith("json") or output.startswith("name"))

    def try_set_wide_for_pod(self, kind):
        if kind == "pod" and self.get("-o") is None:
            return self.reset_arg("-o", "wide")
        return self.dupliacte(raw)

