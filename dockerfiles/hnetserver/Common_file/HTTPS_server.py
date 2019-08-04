import BaseHTTPServer, SimpleHTTPServer
import ssl
import sys
PORT = int(sys.argv[1])
HOST = '0.0.0.0'
httpd = BaseHTTPServer.HTTPServer((HOST, PORT),
        SimpleHTTPServer.SimpleHTTPRequestHandler)

httpd.socket = ssl.wrap_socket (httpd.socket,
        keyfile="./ssl.key",
        certfile='./ssl.crt',
        ca_certs="./ca.crt",
        ssl_version=ssl.PROTOCOL_SSLv23,
        cert_reqs=ssl.CERT_OPTIONAL,
        #cert_reqs=ssl.CERT_REQUIRED,
        server_side=True)
print "Serving HTTPS on %s port %d ..." %(HOST, PORT)
httpd.serve_forever()
