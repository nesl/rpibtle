import random

class Settings:
    
    def __init__(self):
        #
        # general settings
        #
        self.SIMULATION_TIME = 1000 # (seconds)
        self.TIME_STEP = 1      # unit time (seconds)
        self.WINDOW_SIZE = 30   # the number of time steps that are considered in the trajectory encryption
        self.SCALE = 10         # for animation
        
        self.OUTPUT_FILE_NAME = "result.csv" # name of the simulation log file
        
        self.BEACON_PLACEMENT_FILE = "beacons.csv" # baacon placement in a csv format
        
        self.RADIO_RANGE = 10.0 # transmission range of BLE signals
        
        self.RANDOM_SEED = 3    # seed for random number generator
        random.seed(self.RANDOM_SEED)
        
        self.MIN_RECEPTION_PROBABILITY = 0.1
        self.PARAM_K = [10, 20, 30]      # list of parameter k
        self.MAX_SET_SIZE = [15, 24, 33] # list of |W| corresponding to each k

        
        self.LIKELIHOOD_THRESHOLD = 0.7  # minimum likelihood for decryption
        
        self.BEACON_RECEPTION_PROBABILITY = 0.9 # reception probability of BLE beacons
                
        #
        # mobility settings
        #
        self.MAX_SPEED = 1.5 # maximum speed of pedestrians
        self.MIN_SPEED = 0.5 # minimum speed of pedestrians
        
        self.N_NODES = 30   #number of nodes 
        
        self.OUTPUT_FILE_PATH = "../../" # default directory for output files
        self.DATA_FILE_PATH = "../../"   # default directory for configuration files
                
                
                 
