#ref: https://docs.python.org/2/library/socketserver.html
import socket
import sys
import traceback
from threading import Thread
from func_timeout import func_set_timeout
import func_timeout
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
        except func_timeout.exceptions.FunctionTimedOut:
            if "ERRPR(wait result timeout)" in contents.keys():
                contents["ERROR(wait result timeout)"] += 1
            else:
                contents["ERROR(wait result timeout)"] = 1
        except Exception, e:
            if repr(e) in contents.keys():
                contents[repr(e)] += 1
            else:
                contents[repr(e)] = 1

@func_set_timeout(5)
def single_socket(host, port):
    # SOCK_DGRAM is the socket type to use for UDP sockets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # As you can see, there is no connect() call; UDP has no connections.
    # Instead, data is directly sent to the recipient via sendto().
    sock.sendto( "test\n", (HOST, PORT))
    received = sock.recv(1024)
    return received

def sent_socket(HOST, PORT):
    queue_t = []
    for i in range(socket_num):
        t = MyThread(HOST, PORT)
        t.start()
        queue_t.append(t)
    for t in queue_t:
        t.join()

    print "%d UDP sockets have been sent. \n" %socket_num
    print "The feedback is from:"
    for item in contents.items():
        print "%s(%d)\n" %(item[0],item[1])

try:
    received = single_socket(HOST, PORT)
except func_timeout.exceptions.FunctionTimedOut:
    print "Establish UDP Connection(%s:%s) time out!" %(HOST,PORT)
    sys.exit(0)
except Exception, e:
    print "UDP Connection(%s:%s) can not be established!" %(HOST,PORT)
    print 'traceback.print_exc():'; traceback.print_exc()
    sys.exit(0)

sent_socket(HOST, PORT)
