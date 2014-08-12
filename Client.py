#!/usr/bin/env python

# ===== IMPORTS =====
import socket
import sys
import time
import select

# ===== TCP/IP COMMANDS =====
CMD_REQUESTKEY = 'RQST'

# ===== VARIABLES =====
server_address = ('172.17.5.1', 31000)
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
        sock.send(CMD_REQUESTKEY)
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

