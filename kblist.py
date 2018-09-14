#!/usr/bin/env python3

import sys
import os 
import subprocess
import json

def execute(cmd):
    info=subprocess.Popen(cmd, shell=True,stderr=subprocess.PIPE, stdout=subprocess.PIPE,close_fds=True).communicate()[0]
    return info.decode("utf-8")


def getveth(cid):
    res = execute("docker exec %s cat /sys/class/net/eth0/{address,ifindex}" % cid)
    res = res.splitlines()
    return res[0], res[1]


def main():
    veths = {}
    for line in execute("ip -o link").splitlines():
        ifname = line.split(":", 2)[1]
        if "@if" in ifname:
            name, index = ifname.split("@if")
            veths[index] = name.strip()
    pods = {}
    res = execute("kubectl get pods -o json")
    for pod in json.loads(res)["items"]:
        name = pod["metadata"]["name"]
        labelApp = pod["metadata"]["labels"]["app"]
        cid = pod["status"]["containerStatuses"][0]["containerID"][9:21]
        podIP = pod["status"]["podIP"]
        podPort = pod["spec"]["containers"][0]["ports"][0]["containerPort"]
        mac, ifindex = getveth(cid)
        pods.setdefault(labelApp, []).append((cid, mac, podIP, podPort, veths.get(ifindex, "-"), name))

    res = execute("kubectl get svc -o json")
    for svc in json.loads(res)["items"]:
        name = svc["metadata"]["name"]
        clusterIP = svc["spec"]["clusterIP"]
        ports = svc["spec"]["ports"][0]
        nodePort = ports.get("nodPort", "-")
        port = ports.get("port", "-")
        targetPort = ports.get("targetPort", "-")
        selectApp = svc["spec"].get("selector", {}).get("app", "")
        print(name, "%s: %s:%s:%s" % (clusterIP, nodePort, port, targetPort))
        for pod in pods.get(selectApp, []):
            print("\t", pod)
            
        #print(name, cid, podIP, podPort)

main()

#docker ps |grep -v '/pause-' | awk '{print $1, $2}' | sed -e 's/docker.io\///g' -e 's/kubeguide\///' -e 's/@.*//'
