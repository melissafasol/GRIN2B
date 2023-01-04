import os 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import pickle 
import string 

import scipy 
from scipy.fft import fft, fftfreq 
from scipy import signal 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from GRIN2B_constants import br_animal_IDs
from idx_tracker import IDX_tracker, HarmonicsPreFiltered

#file path 
directory_name_1 = '/home/melissa/PREPROCESSING/GRIN2B/idx_tracker/REM/test_folder/br_1/'
directory_name_2 = '/home/melissa/PREPROCESSING/GRIN2B/idx_tracker/REM/test_folder/br_2'
channel_numbers =  [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
brainstate = 2

noisy_epochs_list_1 = []
noisy_epochs_list_2 = []
mean_psd_df_list = []
for file in os.listdir(directory_name_1):
    print(file)
    animal = file[0:3]
    channel = file[4:6]
    br = file[-8]
    if "_" in channel:
        channel = channel.replace("_", "")
    os.chdir(directory_name_1)
    with open(file, "rb") as f:
        data_1 = pickle.load(f)
    for file_2 in os.listdir(directory_name_2):
        if file[0:10] == file_2[0:10]:
            print(file_2)
            os.chdir(directory_name_2)
            with open(file_2, "rb") as f_2:
                data_2 = pickle.load(f_2)
        else:
            continue
        idx_1 = HarmonicsPreFiltered(data_1, brainstate = brainstate)
        idx_2 = HarmonicsPreFiltered(data_2, brainstate = brainstate)
        noisy_epoch_1, mean_psd_1, frequency_1 = idx_1.harmonics_algo_idx(animal, channel)
        noisy_epoch_2, mean_psd_2, frequency_2 = idx_2.harmonics_algo_idx(animal, channel)
        if len(noisy_epoch_1) > 0:
            noisy_epoch_1 = pd.concat(noisy_epoch_1)
            noisy_epochs_list_1.append(noisy_epoch_1)
        else:
            pass 
        if len(noisy_epoch_2) > 0:
            print(len(noisy_epoch_2))
            noisy_epoch_2 = pd.concat(noisy_epoch_2)
            noisy_epochs_list_2.append(noisy_epoch_2)
        else:
            pass
        average_psd =  np.mean([mean_psd_1, mean_psd_2], axis = 0)
        print('average psd calculated for ' + str(animal) + ' ' + str(channel) )
        mean_psd_df = pd.DataFrame(data = {'Animal_ID': [animal]*626, 'Channel': [int(channel)]*626,
                                          'Power': average_psd[0:626], 'Frequency': frequency_1[0:626]})                                   
        mean_psd_df_list.append(mean_psd_df)
        