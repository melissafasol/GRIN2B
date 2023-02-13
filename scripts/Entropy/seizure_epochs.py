'''This script is to extract seizure indices and look at epochs prior to seizures'''

import os 
import sys
import numpy as np 
import pandas as pd 

import scipy
from scipy.fft import fft, fftfreq
from scipy import signal
import pandas as pd

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, seizure_free_IDs
from prepare_files import PrepareGRIN2B

directory_normal_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy/'
directory_seizure_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures/'

class SeizurePrep_DispEn():
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
    
    def only_wake_prior_epochs(self, indep_seizure_values, concat_seiz_duration, norm_br_state):
        #checks prior seizure epochs to see 
        prior_epochs_seizure_wake = []
        if indep_seizure_values == None:
            pass
        else:
            seizure_start_values = concat_seiz_duration['seizure_start'].to_numpy()
            seizure_end_values = concat_seiz_duration['seizure_end'].to_numpy()
            for value, seiz_start, seiz_end in zip(indep_seizure_values, seizure_start_values, seizure_end_values):
                if value - 30 > 0:
                    prior_epochs = value - 30
                    before_seizure_index = norm_br_state[norm_br_state['start_epoch'] == prior_epochs].index.values[0]
                    seizure_index = norm_br_state[norm_br_state['start_epoch'] == value].index.values[0]
                    bf_ict_df = norm_br_state[before_seizure_index:seizure_index]
                    pre_ict = bf_ict_df['brainstate'].values
                    if np.mean(pre_ict) > 0:
                        pass
                    else:
                        #dataframe with details to extract time values from recording for entropy calculations
                       data_dict = {'animal_id': [self.animal_id],'pr_seiz_time': [int(prior_epochs*250.4)], 'seiz_time_start': [int(value*250.4)], 
                                    'seiz_time_end':[int(seiz_end*250.4)]}
                       prior_epochs_seizure_wake.append(pd.DataFrame(data = data_dict))
                       
        return prior_epochs_seizure_wake
    

class Filter_Seizure():
    
    order = 3
    sampling_rate = 250.4
    nyquist = 125.2
    low = 0.2/nyquist
    high = 48/nyquist
    noise_limit = 3000
    
    def __init__(self, unfiltered_data):
        self.unfiltered_data = unfiltered_data
    
    def butter_bandpass(self):
        butter_b, butter_a = signal.butter(self.order, [self.low, self.high], btype='band', analog = False)
        
        filtered_data = signal.filtfilt(butter_b, butter_a, self.unfiltered_data)
        
        return filtered_data
    
#code to extract only wake prior seizure epochs
for animal in br_animal_IDs:
    if animal in seizure_free_IDs:
        pass
    else:
        prepare_GRIN2B = PrepareGRIN2B(directory_path = directory_normal_path, animal_id = animal)
        recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
        seizure_prep_br = SeizurePrep_DispEn(animal_id = animal, seizure_directory = directory_seizure_path, 
                                            normal_directory = directory_normal_path)
        seiz_start_1, seiz_start_2, seiz_end_1, seiz_end_2 = seizure_prep_br.time_values() #returns the seizure start times rounded to nearest multiple of five and the seizure end times rounded to nearest integer
        indep_seizure_start_1, indep_seizure_dur_1 = seizure_prep_br.checking_overlapping_seizures(seiz_start_1, seiz_end_1) #checks for non-overlapping seizures and returns start times 
        concat_seizure_df = pd.concat(indep_seizure_dur_1, axis = 0)
        only_wake_epochs = seizure_prep_br.only_wake_prior_epochs(indep_seizure_start_1, concat_seizure_df, brain_state_1)