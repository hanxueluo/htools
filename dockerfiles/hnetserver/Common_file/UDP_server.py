import socketserver
import sys
import http2

def get_content(self, socket, data):
    headers = http2.parse_as_header(data)
    status, msg = http2.get_content2("udp", [], self.client_address, socket.getsockname(), headers)
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
        socket = self.request[1]
        c = get_content(self, socket, data)

        socket.sendto(c, self.client_address)

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    print("Serving UDP on %s port %d ..." %(HOST, PORT))
    server.serve_forever()
