from array import array

class User:
	# variables
	identifier = ''
	xy_pos = (0,0)
	# TODO: expected key history, encrypted path id, etc.

	def __init__(self,ident):
		self.identifier = ident

	def getID(self):
		return self.identifier

	def getPos(self):
		return self.xy_pos
