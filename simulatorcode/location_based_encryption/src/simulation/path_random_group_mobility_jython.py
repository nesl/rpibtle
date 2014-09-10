import utils.dijkstra as dijkstra
import math
import random

from settings.parameters import Settings
from simulation.trajectory_identification_jython import TrajectoryIdentification


# mobility generator
class PathRandomGroupMobility():
    
    def __init__(self, settings):
        
        # loading settings 
        self.settings = settings
        
        # file paths for map data
        self.filename_waypoints = self.settings.DATA_FILE_PATH + "waypoints.csv"
        self.filename_links = self.settings.DATA_FILE_PATH + "links.csv"
        self.filename_walls = self.settings.DATA_FILE_PATH + "walls.csv"
                    
        # some aliases
        self.SIMULATION_TIME = self.settings.SIMULATION_TIME
        self.MAX_SPEED = self.settings.MAX_SPEED
        self.MIN_SPEED = self.settings.MIN_SPEED 
        self.TIME_STEP = self.settings.TIME_STEP     
        
        # loading the locations of BLE beacon transmitters
        filename_beacons = self.settings.DATA_FILE_PATH + self.settings.BEACON_PLACEMENT_FILE
        
        self.beacon_list = {}    
        file_beacons = open(filename_beacons, "r")
        for line in file_beacons.readlines():
            print line
            elements = line.strip().split(",")
            if int(elements[3]) == 1:
                beacon_id = int(elements[0])
                x_pos = int(elements[1])
                y_pos = int(elements[2])            
                self.beacon_list[beacon_id] = (x_pos, 24-y_pos)   
        
    # generation systhetic pedestrian mobility (path-based random waypoint model)
    def generate_mobility(self):      
        
        dict_waypoints = {}
        list_pois = []
        list_walls = []

        file_waypoints = open(self.filename_waypoints, "r")
        for line in file_waypoints.readlines():
            elements = line.strip().split(",")
            waypoint_id = int(elements[0])
            x_pos = int(elements[1])
            y_pos = int(elements[2])
            is_poi = int(elements[3])
            dict_waypoints[waypoint_id] = (x_pos, 24-y_pos)
            if is_poi:
                list_pois.append(waypoint_id)                                    
            
        n_waypoints = len(dict_waypoints)
        n_pois = len(list_pois)
        print n_waypoints, "waypoints have been read."
        print n_pois, "POIs have been read."            
        
        graph = {}
        for i in range(1, n_waypoints+1):
            graph[i] = {}
            
        file_links = open(self.filename_links, "r")
        for line in file_links.readlines():
            elements = line.strip().split(",")
            src_id = int(elements[0])
            dst_id = int(elements[1])
            distance = math.sqrt((dict_waypoints[dst_id][0] - dict_waypoints[src_id][0])**2 + (dict_waypoints[dst_id][1] - dict_waypoints[src_id][1])**2) 
            graph[src_id][dst_id] = distance
            graph[dst_id][src_id] = distance
            
        file_walls = open(self.filename_walls, "r")
        for line in file_walls.readlines():
            elems = line.strip().split(",")
            list_walls.append(((int(elems[1]), 24-int(elems[2])), (int(elems[3]), 24-int(elems[4]))))
        
        #
        # generate trajectories
        #
        
        human_trajectory = {}
        for i in range(self.settings.N_NODES):
            human_trajectory[i] = {}
        
        for human_id in range(self.settings.N_NODES):
                            
            initial_waypoint = dict_waypoints.keys()[int(len(dict_waypoints.keys()) * random.random())]
            initial_pos = dict_waypoints[initial_waypoint]
                            
            destination_waypoint = list_pois[min(int(random.random() * n_pois), n_pois-1)]
            while initial_waypoint == destination_waypoint:
                destination_waypoint = list_pois[min(int(random.random() * n_pois), n_pois-1)]
            sp = dijkstra.shortestpath(graph, initial_waypoint, destination_waypoint, [], {}, {})[1]
            
            current_pos = list(initial_pos)
            current_waypoint = sp.pop(0)
            next_waypoint = sp.pop(0)    
            next_pos = dict_waypoints[next_waypoint]
                                            
            current_time = 0
            next_movement = self.TIME_STEP
            current_speed = self.MIN_SPEED + (self.MAX_SPEED - self.MIN_SPEED) * random.random()
            
            while current_time < self.SIMULATION_TIME:
                                        
                if next_movement <= current_time:
                    remaining_distance_to_move = current_speed * self.TIME_STEP
                    
                    while remaining_distance_to_move > 0:
                        while True:
                            distance = math.sqrt((next_pos[0] - current_pos[0])**2 + (next_pos[1] - current_pos[1])**2)
                            if distance < remaining_distance_to_move:
                                current_pos[0] = next_pos[0]
                                current_pos[1] = next_pos[1]
                                remaining_distance_to_move -= distance            
                                current_waypoint = next_waypoint
                                if current_waypoint == destination_waypoint:
                                    remaining_distance_to_move = 0
                                    break
                                else:
                                    next_waypoint = sp.pop(0)
                                    next_pos = dict_waypoints[next_waypoint]                            
                            else:
                                current_pos[0] += (next_pos[0] - current_pos[0]) / distance * remaining_distance_to_move
                                current_pos[1] += (next_pos[1] - current_pos[1]) / distance * remaining_distance_to_move
                                remaining_distance_to_move = max(0, remaining_distance_to_move - distance)                    
                                break
            
                    if current_waypoint == destination_waypoint:
                        next_movement += max(1, int(random.random() * 90)) * self.TIME_STEP
                        current_speed = self.MIN_SPEED + (self.MAX_SPEED - self.MIN_SPEED) * random.random()
                        
                        destination_waypoint = current_waypoint
                        # randomly select a different waypoint as a destination
                        while destination_waypoint == current_waypoint:
                            destination_waypoint = list_pois[min(int(random.random() * n_pois), n_pois-1)]
                        sp = dijkstra.shortestpath(graph, current_waypoint, destination_waypoint, [], {}, {})[1]
                        current_waypoint = sp.pop(0)
                        next_waypoint = sp.pop(0)    
                        next_pos = dict_waypoints[next_waypoint]                                    
                    else:
                        next_movement += self.TIME_STEP
                        
                human_trajectory[human_id][current_time] = current_pos[:]                       
                current_time += self.TIME_STEP                  
                        
        print "Done."
        return human_trajectory
                

if __name__ == "__main__":
    settings = Settings()
    prgm = PathRandomGroupMobility(settings)
    ground_truth_trajectory = prgm.generate_mobility()
    identifier = TrajectoryIdentification(settings)
    identifier.trajectory_identification(ground_truth_trajectory, consider_walls=True)

                