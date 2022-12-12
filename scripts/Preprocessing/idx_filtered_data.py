'''This file is to save filtered data and indices per brain state to speed up power calculations'''

import os 
import numpy as np 
import pandas as pd
import pickle

from scipy import average, gradient, signal
import sys 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts/')
from GRIN2B_constants import br_animal_IDs
from prepare_files import LoadFromStart, LoadGRIN2B
from filter import Filter
from idx_tracker import IDX_tracker

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing')
from preproc2_extractbrainstate import ExtractBrainStateIndices

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
save_path = '/home/melissa/PREPROCESSING/GRIN2B/idx_tracker/NREM'
brain_state_number = 1
channel_number_list =  [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]


for animal in br_animal_IDs:
    prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
    recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    channel_data = [(channelnumber, LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)) for channelnumber in channel_number_list]
    data = map(lambda x: x[1].load_GRIN2B_from_start(), channel_data)
    data_1, data_2 = zip(*data)
    extract_brain_state_1 = ExtractBrainStateIndices(brainstate_file = brain_state_1, brainstate_number = brain_state_number)
    extract_brain_state_2 = ExtractBrainStateIndices(brainstate_file = brain_state_2, brainstate_number = brain_state_number)
    epoch_indices_1 = extract_brain_state_1.load_brainstate_file()
    epoch_indices_2 = extract_brain_state_2.load_brainstate_file()
    timevalues_array_1 = extract_brain_state_1.get_data_indices(epoch_indices_1)
    timevalues_array_2 = extract_brain_state_2.get_data_indices(epoch_indices_2)
    for channel_array_1, channel_array_2, channelnumber in zip(data_1, data_2, channel_number_list):
        idx_1 = IDX_tracker(channel_array_1, brain_state_1, timevalues_array_1)
        idx_2 = IDX_tracker(channel_array_2, brain_state_2, timevalues_array_2)
        clean_concat_1 = idx_1.butter_bandpass_index_tracker(seizure = 'False')
        clean_concat_2 = idx_2.butter_bandpass_index_tracker(seizure = 'False')
        with open(str(animal) + '_' + str(channelnumber) + '_data_1.pickle', 'wb') as handle:
            os.chdir(save_path)
            pickle.dump(clean_concat_1, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(str(animal) + '_' + str(channelnumber) + '_data_2.pickle', 'wb') as handle:
            os.chdir(save_path)
            pickle.dump(clean_concat_2, handle, protocol=pickle.HIGHEST_PROTOCOL)
