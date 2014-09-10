import random
import math
import pickle
from settings.parameters import Settings
import itertools
import operator as op

from jp.mclab.higuchi.le.policy import PolicyCalculator

from java.util import HashMap
from java.util import Vector

class TrajectoryIdentification:
        
    def __init__(self, settings):
        self.settings = settings
                       
        filename_beacons = self.settings.DATA_FILE_PATH + self.settings.BEACON_PLACEMENT_FILE
        
        # loading locations of BLE beacon devices        
        self.beacon_list = {}    
        file_beacons = open(filename_beacons, "r")
        next_beacon_id = 0
        for line in file_beacons.readlines():
            elements = line.strip().split(",")
            if int(elements[3]) == 1:                
                beacon_id = next_beacon_id
                next_beacon_id += 1
                x_pos = int(elements[1])
                y_pos = int(elements[2])
                self.beacon_list[beacon_id] = (x_pos, 24-y_pos)
            
        filename_walls = self.settings.DATA_FILE_PATH + "walls.csv"      
        
        # loading walls         
        self.list_walls = []    
        file_walls = open(filename_walls, "r")
        for line in file_walls.readlines():
            elems = line.strip().split(",")
            self.list_walls.append(((int(elems[1]), 24-int(elems[2])), (int(elems[3]), 24-int(elems[4]))))
            
        # loading an external Java class
        self.policy_calculator = PolicyCalculator()
    
    # calculate the number of combinations (nCr)
    def ncr(self, n, r):
        r = min(r, n-r)
        if r == 0: return 1
        numer = reduce(op.mul, xrange(n, n-r, -1))
        denom = reduce(op.mul, xrange(1, r+1))
        return numer//denom   
             
    # radio reception model; should be replaced by more realistic one    
    def beaconReceptionProbability(self, distance):
        if distance < self.settings.RADIO_RANGE:        
            return self.settings.BEACON_RECEPTION_PROBABILITY
        else:
            return 0.001 # very small value; intending to avoid zero-division
        
    # check the presence of line-of-sight between a client and a beacon device
    def checkLOS(self, node_pos, neighbor_pos, walls):

        x1 = node_pos[0]
        y1 = node_pos[1]
        x2 = neighbor_pos[0]
        y2 = neighbor_pos[1]
        
        for wall in walls:
            x3 = wall[0][0]
            y3 = wall[0][1]
            x4 = wall[1][0]
            y4 = wall[1][1]
                        
            ta = (x3-x4)*(y1-y3)+(y3-y4)*(x3-x1)
            tb = (x3-x4)*(y2-y3)+(y3-y4)*(x3-x2)
            tc = (x1-x2)*(y3-y1)+(y1-y2)*(x1-x3)
            td = (x1-x2)*(y4-y1)+(y1-y2)*(x1-x4)

            if ta * tb < 0 and tc * td < 0:
                return False
        
        return True    
    
    # main function for trajectory identification                         
    def trajectory_identification(self, ground_truth_trajectory, consider_walls=True):
        
        # just some aliases
        TIME_STEP = self.settings.TIME_STEP
        SIMULATION_TIME = self.settings.SIMULATION_TIME
        WINDOW_SIZE = self.settings.WINDOW_SIZE
        
        output_filename = self.settings.OUTPUT_FILE_PATH + self.settings.OUTPUT_FILE_NAME        
        output_file = open(output_filename, "w")
                        
        beacon_list = self.beacon_list
        
        output_file.write("n_nodes=%d, consider_walls=%s, n_beacons=%d, beacon_reception_probability=%f, likelihood_threshold=%f, random_seed=%d, time_step=%d, window_size=%d, " % (self.settings.N_NODES, consider_walls, len(beacon_list), self.settings.BEACON_RECEPTION_PROBABILITY, self.settings.LIKELIHOOD_THRESHOLD, self.settings.RANDOM_SEED, self.settings.TIME_STEP, self.settings.WINDOW_SIZE))
        output_file.write("k=")
        for k in self.settings.PARAM_K:
            output_file.write(" %d" % k)
        output_file.write(", w_max=")
        for w_max in self.settings.MAX_SET_SIZE:
            output_file.write(" %d" % w_max)
        output_file.write("\n")
                       
        if consider_walls:
            list_walls = self.list_walls
            print list_walls
        else:
            list_walls = []            
            
        beacon_reception_probability = HashMap()
                
        for trajectory_id in ground_truth_trajectory.keys():
            beacon_reception_probability.put(trajectory_id, HashMap())
            for beacon_id in beacon_list.keys():
                beacon_reception_probability.get(trajectory_id).put(beacon_id, HashMap())
                
        # set of beacons that are received by each client
        received_beacons = {}
        for trajectory_id in ground_truth_trajectory.keys():
            received_beacons[trajectory_id] = set([])
        
        decryptability_table = {}           
        for current_time in range(0, SIMULATION_TIME, TIME_STEP):
                        
            param_id = (current_time/TIME_STEP) % len(self.settings.PARAM_K)
            k = self.settings.PARAM_K[param_id]
            max_size_w = self.settings.MAX_SET_SIZE[param_id]
            
            print "time=", current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K)), ", k=", k
                                                                    
            for trajectory_id in ground_truth_trajectory.keys():
                
                # simulating wireless communication between BLE beacons                
                for beacon_id in beacon_list.keys():
                    if self.checkLOS(ground_truth_trajectory[trajectory_id][current_time], beacon_list[beacon_id], list_walls):
                        distance = math.sqrt((ground_truth_trajectory[trajectory_id][current_time][0] - beacon_list[beacon_id][0])**2 + (ground_truth_trajectory[trajectory_id][current_time][1] - beacon_list[beacon_id][1])**2)
                        beacon_reception_probability.get(trajectory_id).get(beacon_id).put(current_time, self.beaconReceptionProbability(distance))
                        if random.random() < beacon_reception_probability.get(trajectory_id).get(beacon_id).get(current_time):
                            signature = Vector()
                            signature.add(beacon_id)
                            signature.add(current_time)
                            received_beacons[trajectory_id].add(signature)
                    else:
                        beacon_reception_probability.get(trajectory_id).get(beacon_id).put(current_time, 0.0)
                        
                    if current_time - TIME_STEP * len(self.settings.PARAM_K) * WINDOW_SIZE >= 0:
                        beacon_reception_probability.get(trajectory_id).get(beacon_id).remove(current_time - TIME_STEP * len(self.settings.PARAM_K) * WINDOW_SIZE)
                        
            # trajectory identification phase
            if current_time < WINDOW_SIZE * TIME_STEP * len(self.settings.PARAM_K):
                continue

            if current_time % (TIME_STEP * len(self.settings.PARAM_K)) == 0:
                decryptability_table[current_time] = {}                                             

            for target_trajectory_id in ground_truth_trajectory.keys():
                
                # decryptability_table[t][i][j] is True if the client i can decrypt trajectory j at time t
                if current_time % (TIME_STEP * len(self.settings.PARAM_K)) == 0:
                    decryptability_table[current_time][target_trajectory_id] = {}
                    for trajectory_id in ground_truth_trajectory.keys():
                        decryptability_table[current_time][target_trajectory_id][trajectory_id] = False
                
                # set of all the location signatures that the client has received during the recent ${WINDOW_SIZE} time steps                                            
                all_location_signatures = []
                for beacon_id in beacon_list.keys():
                    for time in range(current_time - (WINDOW_SIZE - 1) * (TIME_STEP * len(self.settings.PARAM_K)), current_time + 1, TIME_STEP * len(self.settings.PARAM_K)):
                        if beacon_reception_probability.get(target_trajectory_id).get(beacon_id).get(time) > self.settings.MIN_RECEPTION_PROBABILITY:
                            aposteriori_prob = beacon_reception_probability.get(target_trajectory_id).get(beacon_id).get(time) / sum([beacon_reception_probability.get(trajectory_id).get(beacon_id).get(time) for trajectory_id in ground_truth_trajectory.keys()])
                            signature = Vector()
                            signature.add(beacon_id)
                            signature.add(time)
                            all_location_signatures.append((signature, aposteriori_prob))
                            
                #
                # selecting the set W (this process is off-loaded to Java code) 
                #
                            
                all_location_signatures.sort(key=lambda a: a[1], reverse=1)
                all_location_signatures = [elem[0] for elem in all_location_signatures]
                                                    
                if len(all_location_signatures) < k:
                    print "trajectory_id=", target_trajectory_id, ", time=", current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K)), ", k=", k, ", W= N/A"
                    output_file.write("0,%d,%d,%d,N/A,N/A\n" % (target_trajectory_id, current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K)), k))                                    
                else:                                        
                    size_of_W = self.policy_calculator.calcPolicy(current_time, all_location_signatures, beacon_reception_probability, target_trajectory_id, self.settings.LIKELIHOOD_THRESHOLD, k, min(len(all_location_signatures), max_size_w))
                    
                    #
                    # Selection of the set W (Python version) (slow; it seems that overhead for reference of dictionary values significantly affects the total execution time)
                    #
                    
#                     size_of_W = max_size_w

#                     size_of_W = k
#                     for set_size in range(k, len(all_location_signatures)+1):
#                         sum_likelihood = 0.0
#                         target_likelihood = 0.0
#                         for trajectory_id in ground_truth_trajectory.keys():
#                             probability = 1.0
#                             for signature_idx in range(set_size-k, set_size):
#                                 probability *= beacon_reception_probability.get(trajectory_id).get(all_location_signatures[signature_idx][0]).get(all_location_signatures[signature_idx][1])
#                             if trajectory_id == target_trajectory_id:
#                                 target_likelihood = probability
#                             sum_likelihood += probability
#                         aposteriori_prob = target_likelihood / sum_likelihood
#                         
#                         if aposteriori_prob > self.settings.LIKELIHOOD_THRESHOLD:
#                             size_of_W = set_size
#                         else:
#                             break
                        

#                     for set_size in reversed(range(k, )):                        
                        
                        
#                         for k_set in itertools.combinations(range(set_size), k):
#                             if not aposteriori_prob.has_key(k_set):                              
#                                 likelihood = {}
#                                 for trajectory_id in ground_truth_trajectory.keys():
#                                     probability = 1.0
#                                     for signature_idx in k_set:
#                                         probability *= beacon_reception_probability.get(trajectory_id).get(all_location_signatures[signature_idx][0]).get(all_location_signatures[signature_idx][1])
#                                     likelihood[trajectory_id] = probability
#                                 aposteriori_prob[k_set] = likelihood[target_trajectory_id] / sum(likelihood.values())
# #                                 aposteriori_prob[k_set] = 0.9
# 
#                             if aposteriori_prob[k_set] < self.settings.LIKELIHOOD_THRESHOLD:
#                                 is_valid = False
#                                 break
                            
                    if size_of_W > 0:
                        print "trajectory_id=", target_trajectory_id, ", time=", current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K)), ", k=", k, ", |W|=", size_of_W
                        output_file.write("0,%d,%d,%d,%d," % (target_trajectory_id, current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K)), k, size_of_W))
                        output_file.write("\n")                                                                    
                        for trajectory_id in ground_truth_trajectory.keys():                            
                            if len(set(all_location_signatures[0:size_of_W]).intersection(received_beacons[trajectory_id])) >= k:
                                decryptability_table[current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K))][target_trajectory_id][trajectory_id] = True
                    else: 
                        print "trajectory_id=", target_trajectory_id, ", time=", current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K)), ", k=", k, ", W= N/A"
                        output_file.write("0,%d,%d,%d,N/A,N/A\n" % (target_trajectory_id, current_time / (TIME_STEP * len(self.settings.PARAM_K)) * (TIME_STEP * len(self.settings.PARAM_K)), k))
        
        for time in decryptability_table.keys():
                for target_trajectory_id in ground_truth_trajectory.keys():
                    for trajectory_id in ground_truth_trajectory.keys():
                        output_file.write("1,%d,%d,%d,%s\n" % (time, target_trajectory_id, trajectory_id, decryptability_table[time][target_trajectory_id][trajectory_id]))    
        
        
        # calculating performance statistics
        n_true_positives = 0
        n_false_positives = 0
        n_true_negatives = 0
        n_false_negatives = 0
        for time in decryptability_table.keys():
            for target_trajectory_id in ground_truth_trajectory.keys():
                for trajectory_id in ground_truth_trajectory.keys():
                    if target_trajectory_id == trajectory_id:
                        if decryptability_table[time][target_trajectory_id][trajectory_id]:
                            n_true_positives += 1
                        else:
                            n_false_negatives += 1
                    else:
                        if decryptability_table[time][target_trajectory_id][trajectory_id]:
                            n_false_positives += 1
                        else:
                            n_true_negatives += 1
                            
        print "accuracy=", float(n_true_positives + n_true_negatives) / (n_true_positives + n_false_positives + n_true_negatives + n_false_negatives)
        precision = float(n_true_positives) / (n_true_positives + n_false_positives)
        recall = float(n_true_positives) / (n_true_positives + n_false_negatives)
        f_measure = 2*precision*recall / (precision+recall)
        print n_true_positives, n_true_negatives, n_false_positives, n_false_negatives
        output_file.write("2,%f,%f,%f,%d,%d,%d,%d\n" % (precision, recall, f_measure, n_true_positives, n_true_negatives, n_false_positives, n_false_negatives))
        
        output_file.close()
            
                    
# selection of W by depth-first search; super slow :( 
                
#                 if len(all_location_signatures) < self.settings.PARAM_K:
#                     print "trajectory_id=", target_trajectory_id, ", time=", current_time, ", W= NaN"
#                 else:                                    
#                     valid_combinations = []
#                     for k_set in itertools.combinations(range(len(all_location_signatures)), self.settings.PARAM_K):                         
#                         likelihood = {}
#                         for trajectory_id in ground_truth_trajectory.keys():
#                             probability = 1.0
#                             for signature_idx in k_set:
#                                 probability *= beacon_reception_probability[trajectory_id][all_location_signatures[signature_idx][0]][all_location_signatures[signature_idx][1]]
#                             likelihood[trajectory_id] = probability
#                         aposteriori_prob = likelihood[target_trajectory_id] / sum(likelihood.values())                    
#                         if aposteriori_prob > 0.8:
#                             label = 0
#                             for i in range(len(all_location_signatures)):
#                                 if i in k_set:
#                                     label += pow(2, i)
#                             valid_combinations.append(label)                
#                     
#                     stack = ["1", "0"]
#                     visited = []
#                     best_label = ""
#                     while len(stack) > 0:
#                         label = stack.pop(0)
#                         if label not in visited:
#                             visited.append(label)                        
#                             if label.count("1") < self.settings.PARAM_K: 
#                                 if len(label) < len(all_location_signatures):
#                                     stack = [label + "1", label + "0"] + stack                    
#                             else:
#                                 num_valid_combinations = 0
#                                 target_label = sum([pow(2, i) for i in range(len(label)) if label[i] == "1"])
#                                 for valid_combination in valid_combinations:
#                                     if bin(valid_combination & target_label).count("1") == self.settings.PARAM_K:
#                                         num_valid_combinations += 1
#                                 if num_valid_combinations == self.ncr(label.count("1"), self.settings.PARAM_K):                        
#                                     if best_label.count("1") < label.count("1"):
#                                         best_label = label
#                                         if best_label.count("1") >= self.settings.MAX_SET_SIZE:
#                                             break
#                                         print best_label, best_label.count("1"), len(all_location_signatures), len(label)
#                                     if len(label) < len(all_location_signatures):
#                                         stack = [label + "1", label + "0"] + stack                     
#                     if best_label != "":
#                         print "trajectory_id=", target_trajectory_id, ", time=", current_time, ", W=", [all_location_signatures[i] for i in range(len(best_label)) if best_label[i] == "1"]
#                     else: 
#                         print "trajectory_id=", target_trajectory_id, ", time=", current_time, ", W= NaN"

        print 'Done.'  
        

