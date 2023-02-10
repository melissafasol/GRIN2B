'''This script is to extract seizure indices and look at epochs prior to seizures'''

import os 
import sys
import numpy as np 
import pandas as pd 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, GRIN_het_IDs

class SeizurePreparation():
    '''prepares brain states and recordings to analyse seizure epochs for entropy calculations in independent seizures to track
    brain dynamics prior to a seizure beginning'''
    def __init__(self, animal_id, seizure_directory, normal_directory):
        self.animal_id = animal_id
        self.brain_1 = animal_id + '_BL1.pkl'
        self.brain_2 = animal_id + '_BL2.pkl'
        self.start_dict_1 = animal_id + '_1'
        self.start_dict_2 = animal_id + '_2'
        self.end_dict_1 = animal_id + '_1A'
        self.end_dict_2 = animal_id + '_2A'
        self.seizure_directory = seizure_directory
        self.normal_directory = normal_directory
    
    def time_values(self):
        '''returns the start time values of seizures rounded to the nearest multiple of 5 to extract time values from regular
        brain states but returns end time values rounded to nearest integer and not nearest multiple of 5 - seizures are short in
        duration (this prevents start and end values being the same number)'''
        
        def round_to_multiple(number, multiple):
            return multiple*round(number/multiple)
        
        os.chdir(self.seizure_directory)
        seiz_br_1 = pd.read_csv('GRIN2B_' + str(self.animal_id) + '_BL1_Seizures.csv')
        seiz_br_2 = pd.read_csv('GRIN2B_' + str(self.animal_id) + '_BL1_Seizures.csv')
        
        seiz_start_1 = [int(value) for value in seiz_br_1['sec_start'].to_numpy()]
        seiz_start_2 = [int(value) for value in seiz_br_2['sec_start'].to_numpy()]
        seiz_end_1 = [int(value) for value in seiz_br_1['sec_end'].to_numpy()]
        seiz_end_2 = [int(value) for value in seiz_br_2['sec_end'].to_numpy()]

        seiz_start_multiples_1 = [round_to_multiple(value, 5) for value in seiz_start_1]
        seiz_start_multiples_2 = [round_to_multiple(value, 5) for value in seiz_start_2]
        
        return seiz_start_multiples_1, seiz_start_multiples_2, seiz_end_1, seiz_end_2
    
    
    def checking_overlapping_seizures(self, seiz_start_multiples, seiz_end):
        independent_seizure_start_times = []
        independent_seizure_duration = []
        
        if len(seiz_start_multiples) > 0:
            independent_seizure_start_times.append(seiz_start_multiples[0])
            data_dict = {'seizure_start': [seiz_start_multiples[0]], 'seizure_end':[seiz_end[0]]}
            independent_seizure_duration.append(pd.DataFrame(data = data_dict))
            for time_start, time_end in zip(range(len(seiz_start_multiples)-1), range(len(seiz_end)-1)):
                if seiz_start_multiples[time_start + 1] < (seiz_end[time_end] + 30):
                    pass
                elif seiz_start_multiples[time_start + 1] == seiz_end[time_end + 1]:
                    pass
                else:
                    independent_seizure_start_times.append(seiz_start_multiples[time_start + 1])
                    data_dict =  {'seizure_start': [seiz_start_multiples[time_start + 1]], 'seizure_end':[seiz_end[time_end + 1]]}
                    independent_seizure_duration.append(pd.DataFrame(data = data_dict))
                    
            else:
                pass
            return independent_seizure_start_times, independent_seizure_duration
    
    def only_wake_prior_epochs(self, indep_seizure_values, independent_seizure_duration, norm_br_state):
        #checks prior seizure epochs to see 
        prior_epochs_seizure_wake = []
        if indep_seizure_values == None:
            pass
        else:
            seizure_start_values = independent_seizure_duration['seizure_start'].to_numpy()
            seizure_end_values = independent_seizure_duration['seizure_end'].to_numpy()
            for idx, value, seiz_start, seiz_end in enumerate(zip(indep_seizure_values, seizure_start_values, seizure_end_values)):
                if value - 30 > 0:
                    prior_epochs = value - 30
                    before_seizure_index = norm_br_state[norm_br_state['start_epoch'] == prior_epochs].index.values[0]
                    seizure_index = norm_br_state[norm_br_state['start_epoch'] == value].index.values[0]
                    bf_ict_df = norm_br_state[before_seizure_index:seizure_index]
                    pre_ict = bf_ict_df['brainstate'].values
                    print(len(pre_ict))
                    print(np.mean(pre_ict))
                    if np.mean(pre_ict) > 0:
                        pass
                    else:
                        #dataframe with details to extract time values from recording for entropy calculations
                       data_dict = {'animal_id': [self.animal_id], 'timevalue_idx' : [idx],
                                    'pr_seiz_time': [prior_epochs], 'seiz_time_start': [value], 
                                    'seiz_time_end':[seiz_end]}
                       prior_epochs_seizure_wake.append(pd.DataFrame(data = data_dict))
                       
        return prior_epochs_seizure_wake

    def immediate_prior_epoch(self, seizure_time, norm_br, seiz_br):
        df_list = []
        if seizure_time == None:
            pass
        else:
            for count, value in enumerate(seizure_time):
                if value - 5 > 0:
                    prior_epoch = value - 30
                    before_seizure_index = norm_br[norm_br['start_epoch'] == prior_epoch].index.values[0]
                    seizure_index = norm_br[norm_br['start_epoch'] == value ].index.values[0]
                    bf_ict_df = norm_br[before_seizure_index:seizure_index + 1]
                    pre_ict = norm_br['brainstate'].values
                    data_dict = {'Animal_ID' : [str(self.animal_id)], 'Prior_Br': [pre_ict]}
                    ict_df = pd.DataFrame(data_dict)
                    df_list.append(ict_df)
        
        if len(df_list > 0):
            concat_df = pd.concat(df_list, axis = 0)
        else:
            pass
        
        return concat_df