#!/usr/bin/env python

# ===== IMPORTS =====
import socket
import sys
import time
import select
import struct
import binascii

# ===== UNIQUE ID =====
unique_id = 1000

# ===== TCP/IP COMMANDS =====
CMD_NULL = 0
CMD_REQUESTKEY = 1
CMD_REGISTER = 2

# ===== TCP/IP STRUCT =====
packet = (1, 2)
packer = struct.Struct('<BH')

# ===== VARIABLES =====
server_address = ('localhost', 31001)
delay_nominal = 0.500
delay_max = 5.0
delay = delay_nominal
tries_before_backoff = 10
missed_tries = 0
max_socket_bytes = 4096

# ===== MAIN LOOP =====
while True:
    # delay
    time.sleep(delay)
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # request new key from server
    try:
		sock.connect(server_address)
		cmd = (CMD_REQUESTKEY,0)
		sock.send( packer.pack(*cmd) )
		resp = sock.recv(max_socket_bytes)
		print 'Received: ',resp
		sock.close()
		# successful? reduce delay
		delay = delay_nominal
		missed_tries = 0
    except:
        missed_tries = missed_tries + 1
        print 'Unable to reach server, attempt ', str(missed_tries)
        if missed_tries > tries_before_backoff:
            delay = delay_max

