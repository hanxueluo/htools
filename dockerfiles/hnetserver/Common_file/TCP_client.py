#ref: https://docs.python.org/2/library/socketserver.html
import socket
import sys
import traceback
from threading import Thread
socket_num = 100
contents={}
HOST = sys.argv[1]
PORT = int(sys.argv[2])

class MyThread(Thread):
    def __init__(self, HOST, PORT):
        super(MyThread, self).__init__()
        self.HOST=HOST
        self.PORT=PORT
    def run(self):
        try:
            received = single_socket(self.HOST, self.PORT)
            if received in contents.keys():
                contents[received] += 1
            else:
                contents[received] = 1
        except Exception, e:
            if repr(e) in contents.keys():
                contents[repr(e)] += 1
            else:
                contents[repr(e)] = 1

def single_socket(host, port):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((host, port))
        sock.sendall("test\n")
        # Receive data from the server and shut down
        received = sock.recv(1024)
        return received
    finally:
        sock.close()

def sent_socket(HOST, PORT):
    queue_t = []
    for i in range(socket_num):
        t = MyThread(HOST, PORT)
        t.start()
        queue_t.append(t)
    for t in queue_t:
        t.join()

    print "%d TCP sockets have been sent. \n" %socket_num
    print "The feedback is from:"
    for item in contents.items():
        print "%s(%d)\n" %(item[0],item[1])


try:
    received = single_socket(HOST, PORT)
except Exception, e:
    print "TCP Connection(%s:%s) can not be established!" %(HOST,PORT)
    print "traceback.print_exc():"; traceback.print_exc()
    sys.exit(0)

sent_socket(HOST, PORT)
