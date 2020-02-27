#!/usr/bin/env python


#import http.server
import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import io
import ssl
#from http import HTTPStatus
import socket
import sys
import time

proto = []

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

def get_content2(proto, peer, me, path, kvs):
    status = 200

    s = "Host: %s\n" % socket.gethostname()
    s += "Proto: %s\n" % proto
    s += "C->S: %s -> %s\n" % (peer, me)
    s += "Path: %s\n" % path

    s += "  Head:\n"
    for k, v in kvs.items():
        s += "    %s: %s\n" % (k, v)
        if k.lower() == "httpstatus":
            status = int(v) if v.isdigit() else 400

    l = kvs.get("L", "")
    if l.isdigit():
        s += "=" * int(l)
        s += "\n"

    l = kvs.get("SLEEP", "")
    if l.isdigit():
        time.sleep(int(l))
    #agent = self.headers.get("User-Agent", "")
    s = "<html><body><pre>\n%s\n</pre></body></html>\n" % s
    #import pdb;pdb.set_trace()

    return status, s.encode("utf-8")

def get_content(self):
    return get_content2(proto, self.connection.getpeername(), self.connection.getsockname(), self.path, self.headers)

def do_GET2(self):
    status, msg = get_content(self)
    print(self.headers)

    self.send_response(status)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(msg)

def run_https(port, handler):
    proto.append("https")
    httpd = BaseHTTPServer.HTTPServer(("", port), handler)
    httpd.socket = ssl.wrap_socket (httpd.socket,
            keyfile="./ssl.key",
            certfile='./ssl.crt',
            ca_certs="./ca.crt",
            ssl_version=ssl.PROTOCOL_SSLv23,
            cert_reqs=ssl.CERT_OPTIONAL,
            #cert_reqs=ssl.CERT_REQUIRED,
            server_side=True)
    print("serving at port", port)
    httpd.serve_forever()

def run_http(port, handler):
    proto.append("http")
    httpd = SocketServer.TCPServer(("", port), handler)
    print("serving at port", port)
    httpd.serve_forever()

def main():
    port = 80
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    Handler.do_GET = do_GET2

    if "https" in sys.argv[0]:
        run_https(port, Handler)
    else:
        run_http(port, Handler)

if __name__ == "__main__":
    main()
