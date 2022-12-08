import os 
import numpy as np 
import pandas as pd
from scipy import average, gradient, signal
import sys 
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, seizure_free_IDs, GRIN_het_IDs
from prepare_files import PrepareGRIN2B, LoadGRIN2B, GRIN2B_Seizures
from idx_tracker import IDX_tracker
from power import PowerSpectrum, RemoveNoisyEpochs
from filter import Filter

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing')
from preproc2_extractbrainstate import ExtractBrainStateIndices

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
brain_state_number = 2
channel_number_list =  [0,2,3,4,5,6,7,8,9,10,11,12,13,15]
seizure_epochs = []
average_df = []
noisy_indices_list = []

testing_animals = ['130']



save_path = '/home/melissa/RESULTS/GRIN2B/Power/WAKE/testing_idx_tracker'
os.chdir(save_path)
save_file_as = '_harmonics_algo.csv'


for animal in br_animal_IDs:
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
            filtered_idx_1 = idx_1.butter_bandpass_index_tracker(seizure = False)
            filtered_idx_2 = idx_2.butter_bandpass_index_tracker(seizure = False)
            if brain_state_number == 0:
                noisy_indices_1, mean_psd_1, frequency_1  = idx_1.harmonics_algo_idx(filtered_idx_1, animal, channelnumber)
                noisy_indices_2, mean_psd_2, frequency_2  = idx_2.harmonics_algo_idx(filtered_idx_2, animal, channelnumber)
                print('harmonics algoirthm finished ')
            else:
                noisy_indices_1, mean_psd_1, frequency_1  = idx_1.power_filtering_idx(filtered_idx_1, animal, channelnumber)
                noisy_indices_2, mean_psd_2, frequency_2  = idx_2.power_filtering_idx(filtered_idx_2, animal, channelnumber)
            if len(mean_psd_1) > 0 and len(mean_psd_2) > 0 :
                results = pd.DataFrame(data = {'Power_1': mean_psd_1, 'Power_2': mean_psd_2})
                average_psd = results[['Power_1', 'Power_2']].mean(axis = 1)
                if animal in GRIN_het_IDs:
                        genotype = 'GRIN2B'
                else:
                        genotype = 'WT'
                dict_data = {'Animal_ID': [animal]*626, 'Channel': [channelnumber]*626, 'Power': average_psd[0:626], 
                        'Frequency': frequency_1[0:626], 'Genotype' : [genotype]*626}
                average_data = pd.DataFrame(data=dict_data)
                average_df.append(average_data)
                os.chdir(save_path)
                average_data.to_csv(str(animal) + '_' +'channel_average_mean_' + save_file_as)
            elif len(mean_psd_1) > 0:
                if animal in GRIN_het_IDs:
                        genotype = 'GRIN2B'
                else:
                        genotype = 'WT'
                dict_data = {'Animal_ID': [animal]*626, 'Channel': [channelnumber]*626, 'Power': mean_psd_1[0:626], 
                        'Frequency': frequency_1[0:626], 'Genotype' : [genotype]*626}
                average_data = pd.DataFrame(data=dict_data)
                average_df.append(average_data)
                os.chdir(save_path)
                average_data.to_csv(str(animal) + '_' +'channel' + '_mean_1' + save_file_as)
            elif len(mean_psd_2) > 0: 
                if animal in GRIN_het_IDs:
                        genotype = 'GRIN2B'
                else:
                        genotype = 'WT'
                dict_data = {'Animal_ID': [animal]*626, 'Channel': [channelnumber]*626, 'Power': mean_psd_2[0:626], 
                        'Frequency': frequency_1[0:626], 'Genotype' : [genotype]*626}
                average_data = pd.DataFrame(data=dict_data)
                average_df.append(average_data)
                os.chdir(save_path)
                average_data.to_csv(str(animal) + '_' +'channel' + '_mean_2' + save_file_as)
            else:
                pass 
                
                
noisy_df = pd.concat(noisy_indices_list, axis = 0).drop_duplicates().reset_index(drop = True) 
os.chdir(save_path)