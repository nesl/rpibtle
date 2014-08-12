
class Beacon
    # variables
    identifier = ''
    xy_pos = (0,0)
    status = 0 # <-- 0 down, 1 up
    key_history = []
    key_current = ''
    key_history_len = 100

    def __init__(self, ident, xy):
        self.identifier = ident
        self.xy_pos = xy

    def getID(self):
        return self.ipaddress

    def getPos(self):
        return self.xy_pos
        
    def genKey(self):
        pass

    def getKeyHistory(self):
        return key_history


