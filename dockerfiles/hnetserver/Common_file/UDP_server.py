#!/usr/bin/env python3
import socketserver
import sys
import common

def get_content(self, socket, data):
    headers = common.parse_as_header(data)
    status, msg, _ = common.get_content("udp", [], self.client_address, socket.getsockname(), headers)
    return msg

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        data = data.decode('utf-8')
        socket = self.request[1]
        c = get_content(self, socket, data)

        socket.sendto(c, self.client_address)

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server.allow_reuse_address = True
    print("Serving UDP on %s port %d ..." %(HOST, PORT))
    server.serve_forever()
