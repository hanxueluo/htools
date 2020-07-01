#!/usr/bin/env python

# TODO LIST:
# . do not do all if no match

# condition
# 1
# /pattern
# @pattern
# N/pattern
# N@pattern
# N=pattern
# N=pattern

# result
# 1.1

import os
import subprocess
import sys
import re
from functools import partial
from cmdtool import *

KUBECTL_GET_TMPFILE="/tmp/hhl.kubectl_alias/get.tmpfile"

tmpdir=os.path.dirname(KUBECTL_GET_TMPFILE)
if not os.path.isdir(tmpdir):
    os.mkdir(tmpdir)

def column_extractor(columns, line):
    items = line.split()
    if type(columns) is list:
        return tuple([ items[c] for c in columns ])
    else:
        return items[columns]

def or_selectors(*ss):
    def _f(line, ext):
        for s in ss:
            b, ext = s(line, ext)
            if b:
                return True, ext
        return False, ext
    return _f

def and_selectors(*ss):
    def _f(line, ext):
        for s in ss:
            b, ext = s(line, ext)
            if not b:
                return False, ext
        return True, ext
    return _f

def not_selector(s):
    def _f(line, ext):
        b, ext = s(line, ext)
        return not b, ext
    return _f

def true_selector(line, ext):
    return True, ext

def line_no_selector(line, ext):
    return False, ext

def get_patter_selector(pattern, column=-1):
    reverse = pattern[0] == '@'
    equal = pattern[0] == '='
    pattern_ = pattern[1:]
    rc = None
    if not equal:
        rc = re.compile(pattern_)

    def _pattern_selector(line, ext):
        s = line
        if column >= 0:
            s = line.split()[column]
        if equal:
            return s == pattern_, ext
        if rc.search(s):
            return False if reverse else True, ext
        else:
            return True if reverse else False, ext
    return _pattern_selector



def do_filter(lines, selector, extractor):
    res = []
    ext = None
    for line in lines:
        if selector:
            b, ext = selector(line, ext)
        else:
            b = True
        if b:
            if extractor:
                line = extractor(line)
            res.append(line)
    return res


class Executor(object):
    def __init__(self, action, kind, resource="", others=""):
        super(Executor, self).__init__()
        self.action = action
        self.kind = kind
        self.resource = resource
        self.others = others.split() if others is str else others

        self.kind, self.resource = self._reset_kind_resource(self.kind, self.resource)

    def _reset_kind_resource(self, kind, resource):
        # handle "pod/kube-proxy-pch4q" and "all pod/kube-proxy-pch4q"
        if "all" == kind and resource and "/" in resource[1:]:
            kind = resource
            resource = "."
        if "/" in kind[1:] and resource == ".":
            ss = kind.split("/", 1)
            kind = ss[0].split(".")[0]
            resource = ss[1]
        return kind, resource

    def kube_execute1(self, namespace, action, kind, resource, option):
        print('1######## ', namespace, action, kind, resource, option.raw)
        out = ""
        if action == "get":
            if len(namespace) > 2:
                lines = Utility.read_file("./nonspods.txt").splitlines()
            else:
                lines = Utility.read_file("./pods.txt").splitlines()
        return lines

    def kube_execute(self, namespace, action, kind, resource, option):
        print('2######## ', namespace, action, kind, resource, option.raw)
        return []

    def _patch_ndoe_ip(self, lines):
        if not lines:
            return lines

        cmd = "kubectl get node -o=custom-columns=NAME:.metadata.name,ADDRESS:.status.addresses[0].address"
        out = Utility.execute(cmd)[1]
        ips = {}
        for l in out.splitlines():
            k, v = l.split()
            ips[k] = v
        lines2 = []
        for l in lines:
            n = l.split()[0]
            line = l + "   " + ips.get(n, "")
            lines2.append(line)
        lines = lines2
        return lines

    def execute(self):
        _pattern = ""
        action = self.action
        kind = self.kind
        resource = ""
        option = KubeOption(self.others)

        # 1. expand namespace and resource
        #import pdb;pdb.set_trace()
        hasfilter = False
        if self.resource.isdigit():
            lines = Utility.read_file(KUBECTL_GET_TMPFILE + "." + kind).splitlines()
            items = self.extract_namespace_resource(lines, [self.resource])
            if items:
                namespace = items[0][0]
                resource = items[0][1]
            else:
                namespace = ""
                resource = ""
                hasfilter = True
            kind, resource = self._reset_kind_resource(kind, resource)
        elif self.resource.startswith("."):
            namespace = self.resource[1:]
            if namespace.startswith("."):
                namespace = {".ks": "kube-system", ".d": "default"}.get(namespace, namespace)
        elif self.resource.startswith("/") or self.resource.startswith("@"):
            _pattern = self.resource
            namespace = ""
            hasfilter = True
        else:
            resource = self.resource
            namespace = self.extract_ns_by_name(self.kube_execute1("", "get", kind, "", KubeOption([])), 1, resource)

        if action == "yaml":
            action = "get"
            option = option.reset_arg("-o", "yaml")


        # 2. first call
        lines = None
        if action == "get":
            op = option
            if _pattern:
                op = op.reset_arg("-o", "wide")

            lines = self.kube_execute1(namespace, "get", kind, resource, op)
            if op.is_list():
                lines = self.format_namespace(lines, kind, namespace)
            lines = self.format_by_pattern(lines, _pattern)

            if not _pattern or option.is_list():
                self.output_result(lines, kind, op.is_list() and resource == "")
                return
        elif hasfilter:
            lines = self.kube_execute1(namespace, "get", kind, resource, KubeOption(["-o", "wide"]))
            lines = self.format_namespace(lines, kind, namespace)
            lines = self.format_by_pattern(lines, _pattern)

        # 3. second call
        if lines is not None:
            # TODO different namespaces
            namespace, resources = self.extract_namespace_resource_all(lines)
            resource = " ".join(resources)

        if not resource and not option.raw:
            action = "get"

        if action in ["delete", "edit"] and " " in resource:
            if not self.confirm_before_do("\nAre you sure to %s %s %s? (y/n) " % (action, kind, "\n\t" + resource.replace(" ", "\n\t") + "\n")):
                print_to_stderr("Aborted.")
                return

        lines = self.kube_execute(namespace, action, kind, resource, KubeOption(option.raw + self.others))
        print("\n".join(lines))

    def format_namespace(self, lines, kind, namespace):
        if namespace:
            formtter = "%%-%ds %%s" % max(len(namespace), 2)
            lines2 = []
            for l in lines:
                if l.startswith("NAME "):
                    line = formtter % ("NS", l)
                else:
                    line = formtter % (namespace, l)
                lines2.append(line)
            lines = lines2
        return lines

    def format_by_pattern(self, lines, pattern):
        if pattern:
            lines = self.select_by_pattern(lines, pattern)
        return lines

    def output_result(self, lines, kind, tofile):
        if tofile:
            lines = self.add_line_number(lines, "")

        result = "\n".join(lines)

        if tofile:
            Utility.write_file(KUBECTL_GET_TMPFILE + "." + kind, result + "\n")
        print(result)
        return lines

    def select_by_pattern(self, lines, pattern):
        def _select_title(line, ext):
            return line.startswith("NAME ") or line.startswith("NAMESPACE"), ext
        f = get_patter_selector(pattern)
        return do_filter(lines, or_selectors(_select_title, f), None)

    def confirm_before_do(self, message):
        print_to_stderr(message, False)
        try:
            r = raw_input()
        except:
            r = "n"
        return r.strip().lower() in ["y", "yes"]

    def extract_namespace_resource_all(self, lines):
        namespace = ""
        resources = []
        res = do_filter(lines[1:], None, partial(column_extractor, [0, 1]))
        if res:
            namespace = res[0]
            resources = [ a[1] for a in res ]
        return namespace, resources

    def extract_ns_by_name(self, lines, column, name):
        res = do_filter(lines, get_patter_selector("="+name, column), partial(column_extractor, 0))
        return res[0] if res else ""
        

    def extract_namespace_resource(self, lines, numbers):
        if not lines:
            return lines
        has_ns = lines[0].split()[1] in ["NS", "NAMESPACE"]

        def _s(line, ext):
            items = line.split()
            b = items[0] in numbers #TODO reduce numbers
            return b, ext

        def _e(line):
            if has_ns:
                return items[1], items[2]
            else:
                return "-", items[1]

        return do_filter(lines, _s, _e)

    def add_line_number(self, lines, prefix=""):
        def _e(index, line):
            s = str(index[0])
            index[0] = index[0] + 1
            if line.startswith("NAME ") or line.startswith("NAMESPACE"):
                s = "=="
            return "%-2s %s" % (s, prefix+line)

        return do_filter(lines, None, partial(_e, [0]))

def test():
    # 1. resource is "", but others is not
    Executor("get", "pod", "/ipam-", []).execute()
    print('=====')
    Executor("describe", "pod", ".test", []).execute()
    print('=====')
    Executor("get", "pod", "test-7d9f4c8b75-4k2c9", []).execute()

def main2(argv):
    action = "get"
    kind = ""
    resource = "."

    argv = argv[:]
    argv.reverse()
    if argv and argv[-1][0] != "-":
        action = argv.pop()
    if argv and argv[-1][0] != "-":
        kind = argv.pop()
    if argv and argv[-1][0] != "-":
        resource = argv.pop()
    argv.reverse()
    print(action, kind, resource, argv)
    Executor(action, kind, resource, argv).execute()


if __name__ == "__main__":
    ##main(sys.argv[1:])
    test()

