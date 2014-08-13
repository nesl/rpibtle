#!/usr/bin/env python

# ===== IMPORTS =====
import socket
import sys
import time
import select
import struct
import binascii
from array import array
from subprocess import call
import atexit

# ===== TCP/IP COMMANDS =====
CMD_NULL = 0
CMD_REQUESTKEY = 1

# ===== GET PORT =====
port = 31000
if len(sys.argv) >= 2:
	print 'Running Client on port ', sys.argv[1]
	port = int(sys.argv[1])	

# ===== VARIABLES =====
server_address = ('localhost', port)
delay_nominal = 0.200
delay_max = 5.0
delay = delay_nominal
tries_before_backoff = 10
missed_tries = 0
max_socket_bytes = 4096
key = array('B', [0]*31)

# ===== READ UNIQUE ID =====
f_id = open('uniqueid','r')
unique_id = int(f_id.readline())

# ===== PRE-MADE PACKETS =====
PKT_REQUESTKEY = array('B', [CMD_REQUESTKEY, unique_id])

# ===== CONFIGURE BTLE ADV =====
devnull = open('/dev/null','w')
def updateBtleAdv(data):
	prefix = "sudo hcitool -i hci0 cmd 0x08 0x0008 1F "
	#config_cmd = prefix + [binascii.hexlify(chunk) for chunk in data]
	config_cmd = prefix + ''.join('{:02x} '.format(x) for x in data)
	call([config_cmd], shell=True)

def configureAllBtleAdv(data):
	# bring up BTLE
	call(["sudo hciconfig hci0 up"], shell=True)
	updateBtleAdv(data)
	# set rate to 100 ms
	call(["sudo hcitool -i hci0 cmd 0x08 0x0006 A0 00 A0 00 03 00 00 00 00 00 00 00 00 07 00"], shell=True)
	# enable adv. through tool (hciconfig overrites rate to make slower)
	call(["sudo hcitool -i hci0 cmd 0x08 0x000a 01"], shell=True)
	
def stopAllBtle():
	call(["sudo hciconfig hci0 noleadv"], shell=True)
	call(["sudo hciconfig hci0 down"], shell=True)

btle_data = bytearray([0]*31)
configureAllBtleAdv(btle_data)
atexit.register(stopAllBtle)

# ===== MAIN LOOP =====
while True:
    # delay
	time.sleep(delay)
    # Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		# request new key from server
		sock.connect(server_address)
		sock.send(PKT_REQUESTKEY)
		resp = bytearray(sock.recv(max_socket_bytes))
		if resp != btle_data:
			btle_data = resp 
			print 'new key: ' + binascii.hexlify(resp)
			updateBtleAdv(bytearray(btle_data))
		sock.close()
		# successful? reduce delay
		delay = delay_nominal
		missed_tries = 0
	except:
		missed_tries = missed_tries + 1
		print 'Unable to reach server, attempt ', str(missed_tries)
		if missed_tries > tries_before_backoff:
			delay = delay_max
















			

