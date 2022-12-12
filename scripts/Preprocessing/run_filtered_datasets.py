import os 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import pickle
import string
import sys

import scipy
from scipy.fft import fft, fftfreq
from scipy import signal

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from GRIN2B_constants import br_animal_IDs, start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, brainstate_number_name
from idx_tracker import HarmonicsPreFiltered

#file path 
brainstate = 2
brainstate_name = brainstate_number_name(brainstate = brainstate)
directory_name = '/home/melissa/PREPROCESSING/GRIN2B/idx_tracker/REM/'
save_path = '/home/melissa/RESULTS/GRIN2B/Power/REM/IDX'
channel_numbers = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]

noisy_epochs_list = []
mean_psd_df_list = []
for file in os.listdir(directory_name):
    os.chdir(directory_name)
    animal = file[0:3]
    channel = file[4:6]
    br = file[-8]
    if "_" in channel:
        channel = channel.replace("_", "")
        print(channel)
    else:
        pass
    with open(file, "rb") as f:
        data = pickle.load(f)
        idx_1 = HarmonicsPreFiltered(data, brainstate = brainstate)
        noisy_epochs_df_1, mean_psd_1, frequency_1 = idx_1.harmonics_algo_idx(animal, channel)
        noisy_epoch = pd.concat(noisy_epochs_df_1)
        mean_psd_df = pd.DataFrame(data = {'Animal_ID': [animal]*len(mean_psd_1), 'Channel': [channel]*len(mean_psd_1),
                                          'Power': mean_psd_1, 'Frequency': frequency_1, 'File_Number': [br]*len(mean_psd_1)})
        noisy_epochs_list.append(noisy_epoch)
        mean_psd_df_list.append(mean_psd_df)
        
noisy_concat = pd.concat(noisy_epochs_list, axis = 0)
psd_concat = pd.concat(mean_psd_df_list, axis = 0)

os.chdir(save_path)
psd_concat.to_csv(brainstate_name + '_filtered_data.csv')
noisy_concat.to_csv(brainstate_name + '_noisy_indices.csv')