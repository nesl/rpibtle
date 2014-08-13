from array import array
import os
import time

class Beacon:
    # variables
	identifier = ''
	xy_pos = (0,0)
	key_history = []
	time_history = []
	key_current = array('B', [0]*31)
	key_history_len = 100
	key_len = 31

	def __init__(self, ident):
		self.identifier = ident
		self.genNextKey()

	def getID(self):
		return self.identifier

	def getPos(self):
		return self.xy_pos
        
	def genNextKey(self):
		new_key = bytearray(os.urandom(self.key_len))
		self.key_current = new_key
		self.key_history.append(new_key)
		self.time_history.append(time.time())
		if len(self.key_history) > self.key_history_len:
			self.key_history.pop() 
			self.time_history.pop()

	def getKeyHistory(self):
		return self.key_history
	
	def getCurrentKey(self):
		return self.key_current


