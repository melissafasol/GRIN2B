import os 
import numpy as np 
import pandas as pd
import sys

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts/')

from GRIN2B_constants import br_animal_IDs, start_time_GRIN2B_baseline, end_time_GRIN2B_baseline
from prepare_files import LoadGRIN2B, PrepareGRIN2B
from filter import Filter

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing/')
from preproc2_extractbrainstate import ExtractBrainStateIndices
from preproc1_preparefiles import LoadDLSleep

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/PowerFeatureAnalysis/')
from Filter import Filter

save_path = '/home/melissa/PREPROCESSING/GRIN2B/coherence/REM_wt/'

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
brain_state_number = 2
save_directory = '/home/melissa/PREPROCESSING/GRIN2B/'
channel_number_list =  [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]


def select_channels(filtered_data):
    
    chan_0 = filtered_data[0]
    chan_2 = filtered_data[2]
    chan_3 = filtered_data[3]
    chan_4 = filtered_data[4]
    chan_5 = filtered_data[5]
    chan_6 = filtered_data[6]
    chan_7 = filtered_data[7]
    chan_8 = filtered_data[8]
    chan_9 = filtered_data[9]
    chan_10 = filtered_data[10]
    chan_11 = filtered_data[11]
    chan_12 = filtered_data[12]
    chan_13 = filtered_data[13]
    chan_15 = filtered_data[15]
    
    chan_arr = np.vstack((chan_0, chan_2, chan_3, chan_4, chan_5, chan_6, chan_7, chan_8,
                          chan_9, chan_10, chan_11, chan_12, chan_13, chan_15))
    
    return chan_arr

for animal in GRIN_wt_IDs:
    print('loading ' + animal)
    prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
    recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    recording_1 = recording[:, start_time_1:end_time_1 + 1]
    recording_2 = recording[:, start_time_2:end_time_2 + 1]
    filter_data_array_1 = Filter(recording_1)
    filter_data_array_2 = Filter(recording_2)
    filtered_data_1 = filter_data_array_1.butter_bandpass()
    filtered_data_2 = filter_data_array_2.butter_bandpass()
    channel_array_1 = select_channels(filtered_data_1)
    channel_array_2 = select_channels(filtered_data_2)
    extract_brain_state_1 = ExtractBrainStateIndices(brainstate_file = brain_state_1, brainstate_number = brain_state_number)
    extract_brain_state_2 = ExtractBrainStateIndices(brainstate_file = brain_state_2, brainstate_number = brain_state_number)
    epoch_indices_1 = extract_brain_state_1.load_brainstate_file()
    epoch_indices_2 = extract_brain_state_2.load_brainstate_file()
    timevalues_array_1 = extract_brain_state_1.get_data_indices(epoch_indices_1)
    timevalues_array_2 = extract_brain_state_2.get_data_indices(epoch_indices_2)
    extracted_1 = np.take(channel_array_1, timevalues_array_1, axis=1)
    extracted_2 = np.take(channel_array_2, timevalues_array_2, axis=1)
    os.chdir(save_path)
    np.save(str(animal) + '_rem_br_1.npy', extracted_1)
    np.save(str(animal) + '_rem_br_2.npy', extracted_2)
    print('files saved for ' + str(animal))