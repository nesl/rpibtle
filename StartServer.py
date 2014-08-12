#!/usr/bin/env python

# ===== IMPORTS =====
import SocketServer
from threading import Thread
import sys
from Beacon import *
import struct
import binascii

# ===== TCP/IP STRUCT =====
unpacker = struct.Struct('<BH')
# ===== BEACON STRUCTURES =====
active_beacons = []


# ===== CLIENT HANDLER ===== 
class ClientHandler(SocketServer.BaseRequestHandler):
    
    # function for handling new connections
    def handle(self):
        data = 'default'
        print "Client connected from ", self.client_address
        while len(data):
			data = self.request.recv(unpacker.size)
			if not len(data):
				break
			# application-specific handling of data
			unpacked = unpacker.unpack(data)
			print '     received CMD %d and VAL %d ' % (unpacked[0], unpacked[1])
			self.request.send(data)

        print "Client exited from ", self.client_address
        self.request.close()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if len(sys.argv) < 2:
    print 'Usage: python StartServer.py <port_num>'
else:
    print 'Opening Server on port', str(sys.argv[1])
    ThreadedTCPServer(('',31001), ClientHandler).serve_forever()
