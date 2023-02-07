import os 
import numpy as np
import pandas as pd 

class PacketLoss():
    
    def __init__(self, filtered_data_dict):
        self.filtered_data_dict = filtered_data_dict
    
    def sort_filt_dict_keys(self):
        sorted_keys = [int(key_value) for key_value in self.filtered_data_dict.keys()]
        
        return sorted_keys
        
    def findMissingNums(self, input_arr):
        #function to find missing values in sorted list 
        max_num = max(input_arr) # get max number from input list/array
        input_set = set(input_arr) # convert input array into a set
        set_num = set(range(1,max(input_arr)+1)) #create a set of all num from 1 to n (n is the max from the input array)

        missing_nums = list(set_num - input_set) # take difference of both sets and convert to list/array
        return missing_nums
    
    def extract_packet_loss(self, br_state_file, br_state_number, missing_nums, time_values):
        #function to identify missing epochs in filtered file 
        new_br_state_file = br_state_file.loc[br_state_file['brainstate'] == br_state_number].reset_index()
        for time_idx in missing_nums:
            noise_index_1 = int(time_values[time_idx]/250.4)
            idx_to_change = new_br_state_file.loc[new_br_state_file['start_epoch'] == noise_index_1]
            og_br_change = idx_to_change['index']
            br_state_file.loc[og_br_change, 'brainstate'] = 6
            