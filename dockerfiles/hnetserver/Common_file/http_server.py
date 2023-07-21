#!/usr/bin/env python3

import http.server
import socketserver
import ssl
import sys
import time
import common

proto = [""]

def get_content(self):
    infos = [
            ( "Version", "%s -> %s" % (self.request_version, self.server_version) ),
            ( "Method", self.command ),
            ( "Path", self.path ),
            ]

    return common.get_content(proto[0], infos, self.connection.getpeername(), self.connection.getsockname(), self.headers)

def do_GET2(self):
    status, msg, kvs = get_content(self)
    print(self.headers)

    self.send_response(status)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    l = kvs.get("BODYSLEEP", "")
    if l.isdigit() and int(l) > 0:
        print(" ** body sleeping", l)
        time.sleep(int(l))
    self.wfile.write(msg)

def do_POST2(self):
    post_data = ""
    content_length = int(self.headers.get('Content-Length', '0'))
    if content_length > 0:
        post_data = self.rfile.read(content_length)

    status, msg, _ = get_content(self)

    self.send_response(status)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(msg)

def run_https(port, handler):
    proto[0] = "https"
    httpd = http.server.HTTPServer(("", port), handler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='./cert/ssl.crt', keyfile="./cert/ssl.key")
    context.set_ciphers('ALL:@SECLEVEL=0')

    httpd.socket = context.wrap_socket (httpd.socket, server_side=True)
    print("serving at port", port)
    httpd.serve_forever()

def run_http(port, handler):
    proto[0] = "http"
    httpd = socketserver.TCPServer(("", port), handler)
    print("serving at port", port)
    httpd.serve_forever()

def main():
    port = 80
    if len(sys.argv) >= 2:
        port = int(sys.argv[-1])

    print("Serving http on %s" %(sys.argv[1:]))

    Handler = http.server.SimpleHTTPRequestHandler
    Handler.do_GET = do_GET2
    Handler.do_POST = do_POST2
    Handler.do_PUT = do_POST2
    Handler.do_DELETE = do_POST2

    if "https" in sys.argv:
        run_https(port, Handler)
    else:
        run_http(port, Handler)

if __name__ == "__main__":
    main()
