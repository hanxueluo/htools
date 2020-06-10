#!/usr/bin/env python3
import socketserver
import sys
import common

def get_content(self, socket, data):
    headers = common.parse_as_header(data)
    status, msg, _ = common.get_content("tcp", [], socket.getpeername(), socket.getsockname(), headers)
    return msg


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        data = self.request.recv(2048).strip()
        data = data.decode('utf-8')
        c = get_content(self, self.request, data)

        self.request.sendall(c)

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server.allow_reuse_address = True
    
    print("Serving TCP on %s port %d ..." %(HOST, PORT))
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
