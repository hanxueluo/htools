import SocketServer
import sys
class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote: %s".format(self.client_address[0]) %data
        # just send back index.html
        file_object = open('index.html')
        try:
            file_context = file_object.read()
            socket.sendto(file_context, self.client_address)
        finally:
            file_object.close()

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    print "Serving UDP on %s port %d ..." %(HOST, PORT)
    server.serve_forever()
