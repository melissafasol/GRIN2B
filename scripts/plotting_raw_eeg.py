import sys
import os 
import pandas as pd
import numpy as np
import mne
import matplotlib


ch_names = ['S1Tr_RIGHT', 'EMG_RIGHT', 'M2_FrA_RIGHT','M2_ant_RIGHT','M1_ant_RIGHT', 'V2ML_RIGHT',
            'V1M_RIGHT', 'S1HL_S1FL_RIGHT', 'V1M_LEFT', 'V2ML_LEFT', 'S1HL_S1FL_LEFT',
            'M1_ant_LEFT','M2_ant_LEFT','M2_FrA_LEFT', 'EMG_LEFT', 'S1Tr_LEFT']

ch_types = ['eeg', 'emg', 'eeg', 'eeg', 'eeg', 'eeg',
           'eeg', 'eeg', 'eeg', 'eeg', 'eeg',
           'eeg', 'eeg', 'eeg', 'emg', 'eeg']


raw_info = mne.create_info(ch_names, sfreq = 250.4, ch_types=ch_types)

os.chdir('/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy/')
test_file = np.load('130_GRIN2B.npy')

raw = mne.io.RawArray(test_file, raw_info)
raw.plot(scalings = 'auto')