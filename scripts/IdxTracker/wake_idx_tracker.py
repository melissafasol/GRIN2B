import os 
import numpy as np 
import pandas as pd
import pickle 

from scipy import average, gradient, signal 
import sys 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts/')
from GRIN2B_constants import br_animal_IDs, start_time_GRIN2B_baseline, end_time_GRIN2B_baseline
from prepare_files import PrepareGRIN2B, LoadGRIN2B
from power import PowerSpectrum
from filter import Filter
from idx_tracker import IDX_tracker, HarmonicsPreFiltered

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing')
from preproc2_extractbrainstate import ExtractBrainStateIndices

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
brain_state_number = 0
channel_number_list =  [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15] 

mean_psd_df_list = []
noisy_epochs_list_1 = []
noisy_epochs_list_2 = []
#adapt for channel 0 :
for animal in br_animal_IDs:
    print(animal)
    prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
    recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    for channelnumber in channel_number_list:
            load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)
            data_1, data_2 = load_GRIN2B.load_GRIN2B_from_start()
            print('all data loaded for ' + str(animal) + ' channel number ' + str(channelnumber))
            extract_brain_state_1 = ExtractBrainStateIndices(brainstate_file = brain_state_1, brainstate_number = brain_state_number)
            extract_brain_state_2 = ExtractBrainStateIndices(brainstate_file = brain_state_2, brainstate_number = brain_state_number)
            epoch_indices_1 = extract_brain_state_1.load_brainstate_file()
            epoch_indices_2 = extract_brain_state_2.load_brainstate_file()
            timevalues_array_1 = extract_brain_state_1.get_data_indices(epoch_indices_1)
            timevalues_array_2 = extract_brain_state_2.get_data_indices(epoch_indices_2)
            print('filtering starting')
            idx_1 = IDX_tracker(data_1, brain_state_1, timevalues_array_1)
            idx_2 = IDX_tracker(data_2, brain_state_2, timevalues_array_2)
            clean_concat_1 = idx_1.butter_bandpass_index_tracker(seizure = 'False')
            print('file_1')
            clean_concat_2 = idx_2.butter_bandpass_index_tracker(seizure = 'False')
            print('file_2')
            idx_1 = HarmonicsPreFiltered(clean_concat_1, brainstate = brain_state_number)
            idx_2 = HarmonicsPreFiltered(clean_concat_2, brainstate = brain_state_number)
            noisy_epoch_1, mean_psd_1, frequency_1 = idx_1.harmonics_algo_idx(animal, channelnumber)
            noisy_epoch_2, mean_psd_2, frequency_2 = idx_2.harmonics_algo_idx(animal, channelnumber)
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
            print('average psd calculated for ' + str(animal) + ' ' + str(channelnumber) )
            mean_psd_df = pd.DataFrame(data = {'Animal_ID': [animal]*626, 'Channel': [int(channelnumber)]*626,
                                          'Power': average_psd[0:626], 'Frequency': frequency_1[0:626]})                                   
            mean_psd_df_list.append(mean_psd_df)
            
#save wake files 
os.chdir('/home/melissa/RESULTS/GRIN2B/Power')
psd_concat = pd.concat(mean_psd_df_list)
noisy_epochs_1 = pd.concat(noisy_epochs_list_1)
noisy_epochs_2 = pd.concat(noisy_epochs_list_2)
psd_concat.to_csv('wake_power_old_algo.csv')
noisy_epochs_1.to_csv('wake_noisy_indices_br_1_feb_23.csv')
noisy_epochs_2.to_csv('wake_noisy_indices_br_2_feb_23.csv')