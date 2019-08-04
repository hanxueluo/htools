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

proto = []


def get_content(self):
    s = "Host: %s\n" % socket.gethostname()
    s += "Proto: %s\n" % proto
    s += "C->S: %s -> %s\n" % (self.connection.getpeername(), self.connection.getsockname())
    s += "Path: %s\n" % self.path

    s += "  Head:\n"
    for k, v in self.headers.items():
        s += "    %s: %s\n" % (k, v)

    l = self.headers.get("L", "")
    if l.isdigit():
        s += "=" * int(l)
        s += "\n"

    #agent = self.headers.get("User-Agent", "")
    s = "<html><body><pre>\n%s\n</pre></body></html>\n" % s
    #import pdb;pdb.set_trace()
    return s.encode("utf-8")


def do_GET2(self):
    msg = get_content(self)
    print(self.headers)

    self.send_response(200)
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
main()
