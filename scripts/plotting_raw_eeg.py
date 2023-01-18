import os 
import pandas as pd
import numpy as np 
import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import mne
import mne.viz
import sys

#import from other scripts 


sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from prepare_files import PrepareGRIN2B
#ßfrom GRIN2B_constants import br_animal_IDs

directory_npy_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
sampling_rate = 250.4


number_of_channels = 16
sample_rate = 250.4
sample_datatype = 'int16'
display_decimation = 1

animals_exclude_seizures = ['140', '238', '362', '365', '375', '378', '401', '402', '404']
br_animal_IDs = ['364']
for animal in br_animal_IDs:
    if animal in animals_exclude_seizures:
        pass
    else:
        prepare_GRIN2B = PrepareGRIN2B(directory_npy_path, animal)
        recording = prepare_GRIN2B.load_two_analysis_files(seizure = 'True')
        
        
seizure_test = recording[:, 16776:21534]


#create info object
channels = ['S1Tr_RIGHT', 'EMG_RIGHT', 'M2_FrA_RIGHT','M2_ant_RIGHT','M1_ant_RIGHT',
                 'V2ML_RIGHT','V1M_RIGHT', 'S1HL_S1FL_RIGHT', 'V1M_LEFT','V2ML_LEFT',
                 'S1HL_S1FL_LEFT', 'M1_ant_LEFT','M2_ant_LEFT','M2_FrA_LEFT', 'EMG_LEFT',
                 'S1Tr_LEFT']
sample_rate = 250.4
channel_types = ['eeg', 'emg', 'eeg', 'eeg', 'eeg',
                'eeg', 'eeg', 'eeg', 'eeg', 'eeg',
                'eeg', 'eeg', 'eeg', 'eeg', 'emg',
                'eeg']

info_obj = mne.create_info(ch_names = channels , sfreq = sample_rate, ch_types = channel_types)

custom_raw = mne.io.RawArray(seizure_test, info_obj)

inline = matplotlib.get_backend()

print("Backend: ", inline)
mne.viz.plot_raw(custom_raw, n_channels = 16 )