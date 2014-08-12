#!/usr/bin/env python

# ===== IMPORTS =====
import SocketServer
from threading import Thread
import sys
from Beacon import *

# ===== BEACON STRUCTURES =====
active_beacons = []


# ===== CLIENT HANDLER ===== 
class ClientHandler(SocketServer.BaseRequestHandler):
    
    # function for handling new connections
    def handle(self):
        data = 'default'
        print "Client connected from ", self.client_address
        while len(data):
            data = self.request.recv(1024)
            # application-specific handling of data
            self.request.send(data)

        print "Client exited from ", self.client_address
        self.request.close()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if len(sys.argv) < 2:
    print 'Usage: python StartServer.py <port_num>'
else:
    print 'Opening Server on port', str(sys.argv[1])
    ThreadedTCPServer(('',31000), ClientHandler).serve_forever()
