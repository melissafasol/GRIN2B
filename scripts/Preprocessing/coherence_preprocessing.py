import os 
import numpy as np 
import pandas as pd
import sys



sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts/')

from GRIN2B_constants import br_animal_IDs, start_time_GRIN2B_baseline, end_time_GRIN2B_baseline
from prepare_files import LoadGRIN2B, PrepareGRIN2B
from filter import Filter
from idx_tracker import IDX_tracker

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing/')
from preproc2_extractbrainstate import ExtractBrainStateIndices

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
brain_state_number = 2
save_directory = '/home/melissa/PREPROCESSING/GRIN2B/coherence/REM'
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
    arr_1 = np.array(data_1)
    arr_2 = np.array(data_2)
    extracted_1 = np.take(arr_1, timevalues_array_1, axis=1)
    extracted_2 = np.take(arr_2, timevalues_array_2, axis=1)
    os.chdir(save_directory)
    np.save(str(animal) + '_' + str(brain_state_number) + '_file_1.npy', arr_1 )
    np.save(str(animal) + '_' + str(brain_state_number) + '_file_2.npy', arr_2 )