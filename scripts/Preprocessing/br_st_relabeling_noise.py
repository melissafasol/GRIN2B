'''Classes to find indices labelled as noise in filtering calculations and change corresponding brain state indices.
Written February 2023. PacketLoss class is to locate indices which exceed 3000mV and NoiseEpochs class is to locate
indices from harmonics and spectral slope filtering.'''

import os 
import numpy as np
import pandas as pd 
import sys


sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing/')
from preproc2_extractbrainstate import ExtractBrainStateIndices


sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts/')
from prepare_files import PrepareGRIN2B
from GRIN2B_constants import br_animal_IDs, start_time_GRIN2B_baseline, end_time_GRIN2B_baseline

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
            if len(new_br_state_file.loc[new_br_state_file['start_epoch'] == noise_index_1]) > 0:
                idx_to_change = new_br_state_file.loc[new_br_state_file['start_epoch'] == noise_index_1]
            elif len(new_br_state_file.loc[new_br_state_file['end_epoch'] == noise_index_1]) > 0:
                idx_to_change = new_br_state_file.loc[new_br_state_file['end_epoch'] == noise_index_1]
            og_br_change = idx_to_change['index']
            #change corresponding index of brainstate column to 6
            br_state_file.loc[og_br_change, 'brainstate'] = 6
        
        return br_state_file
    

class NoiseEpochs():
    
    def __init__(self, brainstate_file_path, animal_id, brain_state_number):
        self.brainstate_file_path = brainstate_file_path
        self.animal_id = animal_id
        self.brain_state_number = brain_state_number
        
        
    def prepare_files(self):
        prepare_GRIN2B = PrepareGRIN2B(self.brainstate_file_path, self.animal_id)
        recording, br_1, br_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
        start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
        end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
        #GET TIME VALUES ARRAY
        extract_brain_state_1 = ExtractBrainStateIndices(brainstate_file = br_1, brainstate_number = self.brain_state_number)
        extract_brain_state_2 = ExtractBrainStateIndices(brainstate_file = br_2, brainstate_number = self.brain_state_number)
        epoch_indices_1 = extract_brain_state_1.load_brainstate_file()
        epoch_indices_2 = extract_brain_state_2.load_brainstate_file()
        timevalues_array_1 = extract_brain_state_1.get_data_indices(epoch_indices_1)
        timevalues_array_2 = extract_brain_state_2.get_data_indices(epoch_indices_2)
        
        return br_1, br_2, timevalues_array_1, timevalues_array_2
    
    
    def load_br_number_file(self, br_1, br_2):
        br_state_change_1 = br_1.loc[br_1['brainstate'] == self.brain_state_number]
        br_state_change_2 = br_2.loc[br_2['brainstate'] == self.brain_state_number]
        
        return br_state_change_1, br_state_change_2
    
    def prepare_noisy_indices(self,noisy_df_1, noisy_df_2):
        noisy_epochs_1 = noisy_df_1.loc[noisy_df_1['Animal_ID'] == int(self.animal_id)]
        noisy_epochs_2 = noisy_df_2.loc[noisy_df_2['Animal_ID'] == int(self.animal_id)]
        #separate indices that have noise and seizure labels 
        noise_artifacts_1 = noisy_epochs_1.loc[noisy_epochs_1['artifact'] == 'noise']
        seizure_artifacts_1 = noisy_epochs_1.loc[noisy_epochs_1['artifact'] == 'seizure']
        noise_artifacts_2 = noisy_epochs_2.loc[noisy_epochs_2['artifact'] == 'noise']
        seizure_artifacts_2 = noisy_epochs_2.loc[noisy_epochs_2['artifact'] == 'seizure']
          
        return noise_artifacts_1, seizure_artifacts_1, noise_artifacts_2, seizure_artifacts_2
    
    def load_changed_other_br(self, path_changed_files_rem, path_changed_files_nrem):
        if self.brain_state_number == 2:
            pass 
        elif self.brain_state_number == 1:
            os.chdir(path_changed_files_rem)
            br_1 = pd.read_pickle(str(self.animal_id) + '_BL1_noise.pkl')
            br_2 = pd.read_pickle(str(self.animal_id) + '_BL2_noise.pkl')
        elif self.brain_state_number == 0:
            os.chdir(path_changed_files_nrem)
            br_1 = pd.read_pickle(str(self.animal_id) + '_BL1_noise.pkl')
            br_2 = pd.read_pickle(str(self.animal_id) + '_BL2_noise.pkl')
        
        return br_1, br_2
    
    def extract_indices_from_noisy_df(self, noise_artifacts_1,  noise_artifacts_2, seizure_artifacts_1, 
                                      seizure_artifacts_2, timevalues_array_1, timevalues_array_2, br_1, br_2,
                                      br_state_change_1, br_state_change_2):
        #input br1 and br2 saved from changing other br files in another brain state (e.g wake or nrem)
        #br_state_change_1 is the indices selected using the brain_state_number e.g br_1.loc[br_1['brainstate'] == 2]
        
        if len(noise_artifacts_1) > 0:
            lst_noise_indices_1 = sorted(set(noise_artifacts_1['epoch_idx'].tolist()))
            for time_idx in lst_noise_indices_1:
                noise_index_1 = int(timevalues_array_1[time_idx]/250.4)
                idx_to_change = br_state_change_1.index[br_state_change_1['start_epoch'] == noise_index_1]
                #print(idx_to_change)
                br_1.loc[idx_to_change, 'brainstate'] = 5
        else:
            print(str(self.animal_id) + ' no noisy epochs')
        if len(noise_artifacts_2) > 0:
            lst_noise_indices_2 = sorted(set(noise_artifacts_2['epoch_idx'].tolist()))
            for time_idx in lst_noise_indices_2:
                noise_index_2 = int(timevalues_array_2[time_idx]/250.4)
                idx_to_change = br_state_change_2.index[br_state_change_2['start_epoch'] == noise_index_2]
                #print(idx_to_change)
                br_2.loc[idx_to_change, 'brainstate'] = 5
        else:
            print(str(self.animal_id) + ' no noisy epochs')
        if len(seizure_artifacts_1) > 0:
            seizure_indices_1 = sorted(set(seizure_artifacts_1['epoch_idx'].tolist()))
            for time_idx in seizure_indices_1:
                noise_index_1 = int(timevalues_array_1[time_idx]/250.4)
                idx_to_change = br_state_change_1.index[br_state_change_1['start_epoch'] == noise_index_1]
                #print(idx_to_change)
                br_1.loc[idx_to_change, 'brainstate'] = 3
        else:
            print(str(self.animal_id) + ' no seizure epochs BR1')
        if len(seizure_artifacts_2) > 0:
            seizure_indices_2 = sorted(set(seizure_artifacts_2['epoch_idx'].tolist()))
            for time_idx in seizure_indices_2:
                noise_index_2 = int(timevalues_array_2[time_idx]/250.4)
                idx_to_change = br_state_change_2.index[br_state_change_2['start_epoch'] == noise_index_2]
                #print(idx_to_change)
                br_2.loc[idx_to_change, 'brainstate'] = 3
        else:
            print(str(self.animal_id) + ' no seizure epochs BR2')
            
        return br_1, br_2


#function to run steps of class
def packet_loss_run(clean_concat_file, br_state_file, br_state_number, time_values):
    packet_loss_func = PacketLoss(clean_concat_file)
    sorted_keys = packet_loss_func.sort_filt_dict_keys()
    missing_nums = packet_loss_func.findMissingNums(sorted_keys)
    br_state_file = packet_loss_func.extract_packet_loss(br_state_file, br_state_number, missing_nums, time_values)
    return br_state_file
    

def noisy_epochs_run(brainstate_file_path, animal_id, brain_state_number, noisy_df_1, noisy_df_2, changed_file_path_nrem, changed_file_path_rem):
    noisy_epochs = NoiseEpochs(brainstate_file_path, animal_id, brain_state_number)
    br_1, br_2, timevalues_array_1, timevalues_array_2 = noisy_epochs.prepare_files()
    br_state_change_1, br_state_change_2 = noisy_epochs.load_br_number_file(br_1, br_2)
    noise_artifacts_1, seizure_artifacts_1, noise_artifacts_2, seizure_artifacts_2 = noisy_epochs.prepare_noisy_indices(noisy_df_1,
                                                                                                                       noisy_df_2)
    changed_br_1, changed_br_2 = noisy_epochs.load_changed_other_br(changed_file_path_rem, changed_file_path_nrem)
    br_1_final, br_2_final = noisy_epochs.extract_indices_from_noisy_df(noise_artifacts_1,  noise_artifacts_2, seizure_artifacts_1, 
                                      seizure_artifacts_2, timevalues_array_1, timevalues_array_2, br_1, br_2,
                                      br_state_change_1, br_state_change_2)
    
    return br_1_final, br_2_final