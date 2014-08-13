#!/usr/bin/env python

# ===== IMPORTS =====
import SocketServer
import socket
from threading import Thread, Lock
import sys
from Beacon import *
import struct
import binascii
from array import array
import time

# ===== TCP/IP COMMANDS =====
CMD_NULL = chr(0)
CMD_REQUESTKEY = chr(1)

# ===== BEACON STRUCTURES =====
all_beacon_ids = [chr(i) for i in range(100,110)]
active_beacons = {}

# ===== CLIENT HANDLER ===== 
class ClientHandler(SocketServer.BaseRequestHandler):
    
    # function for handling new connections
    def handle(self):
        data = 'default'
        print "Client connected from ", self.client_address
        while len(data):
			# parse incoming data
			data = self.request.recv(1024)
			if len(data) < 2:
				break
			# packets are (command, unique ID)
			cmd = data[0]
			uid = data[1]
			# handle command appropriately
			if cmd is CMD_REQUESTKEY:
				# -- ATOMIC PROCEDURE BEGINS, AQUIRE THREAD LOCK --
				# make sure this beacon is in the active beacons dict
				if uid not in active_beacons and uid in all_beacon_ids:
					active_beacons[uid] = Beacon(uid)
				beacon = active_beacons[uid]
				self.request.send( beacon.getCurrentKey() )
				# -- END ATOMIC PROCEDURE, RELEASE LOCK --

        print "Client exited from ", self.client_address
        self.request.close()


# ===== THREADED SERVER CLASS =====
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# ===== THREAD TO CHANGE KEYS =====
class KeyChanger(Thread):
	# - variables -
	delay = 0.500
	beacons = {}

	def __init__(self,beacons):
		super(KeyChanger, self).__init__()
		self.beacons = beacons


	def run(self):
		while 1:
			# delay
			time.sleep(self.delay)
			# cycle all keys
			for uid in self.beacons:
				self.beacons[uid].genNextKey()

# ===== FIRE UP KEY CHANGER =====
keychanger = KeyChanger(active_beacons)
keychanger.setDaemon(True)
keychanger.start()
	

# ===== FIRE UP THE SERVER ON GIVEN PORT =====
if len(sys.argv) < 2:
    print 'Usage: python StartServer.py <port_num>'
else:
	print 'Opening Server on port', str(sys.argv[1])
	myserver = ThreadedTCPServer(('',int(sys.argv[1])), ClientHandler)
	myserver.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	myserver.serve_forever()




