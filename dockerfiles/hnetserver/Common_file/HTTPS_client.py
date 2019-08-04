import ssl
import socket
import sys
import traceback
from threading import Thread

socket_num = 100
contents={}
dir_crt = "./cert/ca.crt"

class MyThread(Thread):
    def __init__(self, HOST, PORT, dir_crt):
        super(MyThread, self).__init__()
        self.HOST=HOST
        self.PORT=PORT
        self.dir_crt=dir_crt
    def run(self):
        try:
            received = single_socket(self.HOST, self.PORT, dir_crt)
            if received in contents.keys():
                contents[received] += 1
            else:
                contents[received] = 1
        except Exception, e:
            if repr(e) in contents.keys():
                contents[repr(e)] += 1
            else:
                contents[repr(e)] = 1

def single_socket(HOST, PORT, dir_crt):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s = ssl.wrap_socket(s, 
        server_side=False,
        #cert_reqs=ssl.CERT_OPTIONAL,
        #cert_reqs=ssl.CERT_REQUIRED, 
        ssl_version=ssl.PROTOCOL_SSLv23,
        #ca_certs=dir_crt
        )
    s.sendall("GET / HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" %HOST)
    latest_result = ""
    while True:
        received = s.recv(4096)
        if not received:
    	    s.close()
    	    break
        latest_result = received
    return latest_result

def sent_socket(HOST, PORT, dir_crt):
    queue_t = []
    for i in range(socket_num):
        t = MyThread(HOST, PORT, dir_crt)
        t.start()
        queue_t.append(t)
    for t in queue_t:
        t.join()

    print "%d HTTPS sockets have been sent. \n" %socket_num
    print "The feedback is from:"
    for item in contents.items():
        print "%s(%d)\n" %(item[0],item[1])


#input parameters
if len(sys.argv) == 2:
    sys.argv.append(443)
HOST = sys.argv[1]
PORT = int(sys.argv[2])
#HOST = "caicloudqa.com"

try:
    received = single_socket(HOST, PORT, dir_crt)
except Exception, e:
    print "HTTPS Connection(%s:%s) can not be established!" %(HOST,PORT)
    print 'traceback.print_exc():'; traceback.print_exc()
    sys.exit(0)

sent_socket(HOST, PORT, dir_crt)
