#!/usr/bin/env python3

from concurrent import futures
import time
import logging

import grpc
from grpc_reflection.v1alpha import reflection
import common
import sys
import subprocess
import re


from local_grpc import helloworld_pb2
from local_grpc import helloworld_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def get_host_ip():
    try:
        res = subprocess.check_output("ip -4 addr".split())
    except:
        return ""

    gs = re.findall("inet ([0-9.]+/\d+) ", str(res))
    if gs:
        for g in gs:
            if g.startswith("127.0.0.1"):
                continue
            items = g.split("/")
            if 1 < int(items[1]) < 32:
                return items[0]
    return ""

def get_content(s, request, context):
    method = sys._getframe(1).f_code.co_name
    infos = [
            ( "Service", "-helloworld.Greeter" ),
            ( "Method", method ),
            ]

    headers = {}
    for c in context.invocation_metadata():
        headers[c.key] = c.value

    return common.get_content("grpc", infos, context.peer(), get_host_ip(), headers)

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        code, md, kvs = get_content(self, request, context)
        print("handle:", context.peer())
        return helloworld_pb2.HelloReply(message=md)

def get_server_cred():
    with open('./cert/ssl.key', 'rb') as f:
        private_key = f.read()
    with open('./cert/ssl.crt', 'rb') as f:
        certificate_chain = f.read()
    # create server credentials
    server_credentials = grpc.ssl_server_credentials(
      ((private_key, certificate_chain,),))
    return server_credentials

def serve():
    port = 50051
    if len(sys.argv) >= 2:
        port = int(sys.argv[-1])

    print("Serving grpc on %s" %(sys.argv[1:]))

    if "grpcs" in sys.argv:
        sc = get_server_cred()
    else:
        sc = None

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    SERVICE_NAMES = (
        helloworld_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    if sc:
        server.add_secure_port('[::]:%s' % port, sc)
    else:
        server.add_insecure_port('[::]:%s' % port)
    print("Listen on [::]:%s" % port)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig()
    serve()
