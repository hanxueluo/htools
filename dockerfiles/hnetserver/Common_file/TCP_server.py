import SocketServer
import sys
import http2

def get_content(self, socket, data):
    data2 = http2.parse_as_header(data)

    status, msg = http2.get_content2("tcp", socket.getpeername(), socket.getsockname(), "/", data2)
    return msg


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        data = self.request.recv(2048).strip()

        c = get_content(self, self.request, data)

        self.request.sendall(c)

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    
    print "Serving TCP on %s port %d ..." %(HOST, PORT)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
