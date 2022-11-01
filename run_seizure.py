import os 
from os.path import exists
import numpy as np 
import pandas as pd
from scipy import average, gradient
import sys 
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs
from prepare_files import PrepareGRIN2B, LoadGRIN2B, br_seizure_files 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B') 
from preproc2_extractbrainstate import ExtractBrainStateIndices
from preproc3_filter import Filter
from preproc4_power_spectrum_analysis import PowerSpectrum, RemoveNoisyEpochs
from save_functions import average_power_df, concatenate_files, power_df, save_files, spectral_slope_save


directory_npy_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
channel_number_list =  [0,2,3,4,5,6,7,8,9,10,11,12,13,15]
power_two_brainstate_df = []
spectral_slope_two_brainstate_df = [] 


for animal in br_animal_IDs:
    prepare_GRIN2B = PrepareGRIN2B(directory_npy_path, animal)
    recording = prepare_GRIN2B.load_two_analysis_files(seizure = 'True')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    os.chdir(seizure_br_path)
    path_br_1 = '/home/melissa/PREPROCESSING/GRIN2B/seizures/GRIN2B_' + str(animal) + '_BL1_Seizures.csv'
    path_br_2 = '/home/melissa/PREPROCESSING/GRIN2B/seizures/GRIN2B_' + str(animal) + '_BL2_Seizures.csv'
    if os.path.exists(path_br_1) == 'True': 
        os.chdir(seizure_br_path)
        br_file_1 = pd.read_csv('GRIN2B_' + str(animal) + '_BL1_Seizures.csv')
    else:
        print('no BR1 for ' + str(animal))
    
    if os.path.exists(path_br_2) == 'True':
        os.chdir(seizure_br_path)
        br_file_2 = pd.read_csv('GRIN2B_' + str(animal) + '_BL2_Seizures.csv')
    else:
        print('no BR2 for ' + str(animal))
        
    # timevalues_1 = br_seizure_files(br_file_1)
    # timevalues_2 = br_seizure_files(br_file_2)
    # for channel in channel_number_list:
    #     load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channel)
    #     data_1, data_2 = load_GRIN2B.load_GRIN2B_from_start()
    #     filter_1 = Filter(data_1, )
    
    
        
    # print(br_file_1)
    # for channelnumber in channel_number_list:
    #     load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)
        