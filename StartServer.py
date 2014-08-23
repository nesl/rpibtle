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
# custom constants
from Constants import *

# ===== BEACON STRUCTURES =====
active_beacons = {}
active_users = {}

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
			# packets are (client type, command, unique ID)
			typ = data[0]
			cmd = data[1]
			uid = data[2]
			# handle command appropriately
			handleClientCmd(self, typ,cmd,uid)

        print "Client exited from ", self.client_address
        self.request.close()

# ===== HANDLE CLIENT COMMANDS =====
def handleClientCmd(socket, typ, cmd, uid):
	# is this a beacon?
	if typ is CMD_TYPE_BEACON:
		# make sure this beacon is in the active beacons dict
		if uid not in active_beacons:
			active_beacons[uid] = Beacon(uid)

		if cmd is CMD_REQUESTKEY:
			# -- ATOMIC PROCEDURE BEGINS, AQUIRE THREAD LOCK --
			beacon = active_beacons[uid]
			socket.request.send( beacon.getCurrentKey() )
			# -- END ATOMIC PROCEDURE, RELEASE LOCK --
	
	# is this a mobile device?
	if typ is CMD_TYPE_MOBILE:
		# make sure this user is in the active user dict
		if uid not in active_users:
			active_users[uid] = User(uid)

		if cmd is CMD_REQUESTPATHS:
			print "mobile device requesting paths"




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




