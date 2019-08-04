#!/usr/bin/python
import sys
import requests
from threading import Thread
socket_num = 100
status_codes={}
contents={}
class MyThread(Thread):
    def __init__(self, url):
        super(MyThread, self).__init__()
        self.url=url
    def run(self):
        r = requests.get(self.url)
        if r.status_code in status_codes.keys():
            status_codes[r.status_code] += 1
        else:
            status_codes[r.status_code] = 1

        if r.content in contents.keys():
            contents[r.content] += 1
        else:
            contents[r.content] = 1
def sent_socket(url):
    queue_t = []
    for i in range(socket_num):
        t = MyThread(url)
        t.start()
        queue_t.append(t)
    for t in queue_t:
        t.join()

    print "%d HTTP sockets have been sent. \nReceive status_codes:" %socket_num
    for item in status_codes.items():
        print "%d(%d)\t" %(item[0],item[1])
    print "\nThe feedback is from:"
    for item in contents.items():
        print "%s(%d)\n" %(item[0],item[1])

if len(sys.argv) == 2:
    sys.argv.append(80)
host = sys.argv[1]
port = sys.argv[2]
url="http://%s:%s" %(host, port)
if requests.get(url).status_code != 200:
    print "can not access this host %s" %url
    sys.exit(0)
sent_socket(url)
