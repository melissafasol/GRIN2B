import os 
import numpy as np 
import pandas as pd
from scipy import average, gradient
import sys 
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, seizure_free_IDs, GRIN_het_IDs
from prepare_files import PrepareGRIN2B, LoadGRIN2B, removing_seizure_epochs, clean_indices
from power import PowerSpectrum, RemoveNoisyEpochs
from filter import Filter

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts')
from preproc2_extractbrainstate import ExtractBrainStateIndices



directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
brain_state_number = 0
channel_number_list =  [0,2,3,4,5,6,7,8,9,10,11,12,13,15]
seizure_epochs = []
average_df = []

for animal in br_animal_IDs:
    if animal in seizure_free_IDs:
        prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
        recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
        start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
        end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
        for channelnumber in channel_number_list:
            load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)
            data_1, data_2 = load_GRIN2B.load_GRIN2B_from_start()
            extract_brain_state_1 = ExtractBrainStateIndices(brainstate_file = brain_state_1, brainstate_number = brain_state_number)
            extract_brain_state_2 = ExtractBrainStateIndices(brainstate_file = brain_state_2, brainstate_number = brain_state_number)
            epoch_indices_1 = extract_brain_state_1.load_brainstate_file()
            epoch_indices_2 = extract_brain_state_2.load_brainstate_file()
            timevalues_array_1 = extract_brain_state_1.get_data_indices(epoch_indices_1)
            timevalues_array_2 = extract_brain_state_2.get_data_indices(epoch_indices_2)
            print('all data loaded for ' + str(animal) + ' channel number ' + str(channelnumber))
            filter_1 = Filter(data_1, timevalues_array_1)
            filter_2 = Filter(data_2, timevalues_array_2)
            filtered_data_1 = filter_1.butter_bandpass(seizure = 'False')
            filtered_data_2 = filter_2.butter_bandpass(seizure = 'False')
            print('filtering complete')
            power_1 = PowerSpectrum(filtered_data_1, nperseg=1252)
            power_2 = PowerSpectrum(filtered_data_2, nperseg=1252)
            mean_psd_1, frequency_1 = power_1.average_psd(average='True')
            mean_psd_2, frequency_2 = power_2.average_psd(average='True')
            psd_noise_1 = RemoveNoisyEpochs(mean_psd_1, frequency_1)
            psd_noise_2 = RemoveNoisyEpochs(mean_psd_2, frequency_2)
            slope_1, intercept_1, slope_remove_1, intercept_remove_1 = psd_noise_1.lin_reg_spec_slope(averaging=False)
            slope_2, intercept_2,slope_remove_2, intercept_remove_2 = psd_noise_2.lin_reg_spec_slope(averaging=False)
            psd_1 = psd_noise_1.remove_noisy_epochs(mean_psd_1, slope_remove_1, intercept_remove_1)
            psd_2 = psd_noise_2.remove_noisy_epochs(mean_psd_2, slope_remove_2, intercept_remove_2)
            average_psd = average_power_df(psd_1, psd_2)
            if animal in GRIN_het_IDs:
                    genotype = 'GRIN2B'
            else:
                    genotype = 'WT'
            dict_data = {'Animal_ID': [animal]*len(frequency_1), 'Channel': [channelnumber]*len(frequency_1), 'Power': average_psd, 
                        'Frequency': frequency_1, 'Genotype' : [genotype]*len(frequency_1)}
            average_df.append(pd.DataFrame(data=dict_data))
    else:
        prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
        recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
        start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
        end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
        os.chdir(seizure_br_path)
        br_1 = pd.read_csv('GRIN2B_' + str(animal) + '_BL1_Seizures.csv')
        br_2 = pd.read_csv('GRIN2B_' + str(animal) + '_BL2_Seizures.csv')
        for channelnumber in channel_number_list:
            load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)
            data_1, data_2 = load_GRIN2B.load_GRIN2B_from_start()
            extract_brain_state_1 = ExtractBrainStateIndices(brainstate_file = brain_state_1, brainstate_number = brain_state_number)
            extract_brain_state_2 = ExtractBrainStateIndices(brainstate_file = brain_state_2, brainstate_number = brain_state_number)
            epoch_indices_1 = extract_brain_state_1.load_brainstate_file()
            epoch_indices_2 = extract_brain_state_2.load_brainstate_file()
            timevalues_array_1 = extract_brain_state_1.get_data_indices(epoch_indices_1)
            timevalues_array_2 = extract_brain_state_2.get_data_indices(epoch_indices_2)
            seizure_epochs_1 = removing_seizure_epochs(br_1, timevalues_array_1)
            seizure_epochs_2 = removing_seizure_epochs(br_2, timevalues_array_1)
            seizure_data = {str(animal) + '_1': [seizure_epochs_1], str(animal) + '_2': [seizure_epochs_2]}
            seizure_epochs.append(pd.DataFrame(data = seizure_data))
            clean_epochs_1 = clean_indices(timevalues_array_1, seizure_epochs_1)
            clean_epochs_2 = clean_indices(timevalues_array_2, seizure_epochs_2)
            print('all data loaded for ' + str(animal) + ' channel number ' + str(channelnumber))
            filter_1 = Filter(data_1, clean_epochs_1)
            filter_2 = Filter(data_2, clean_epochs_2)
            filtered_data_1 = filter_1.butter_bandpass(seizure = 'False')
            filtered_data_2 = filter_2.butter_bandpass(seizure= 'False')
            print('filtering complete')
            power_1 = PowerSpectrum(filtered_data_1, nperseg=1252)
            power_2 = PowerSpectrum(filtered_data_2, nperseg=1252)
            mean_psd_1, frequency_1 = power_1.average_psd(average = 'True')
            mean_psd_2, frequency_2 = power_2.average_psd(average= 'True')
            psd_noise_1 = RemoveNoisyEpochs(mean_psd_1, frequency_1)
            psd_noise_2 = RemoveNoisyEpochs(mean_psd_2, frequency_2)
            slope_1, intercept_1, slope_remove_1, intercept_remove_1 = psd_noise_1.lin_reg_spec_slope(averaging=False)
            slope_2, intercept_2,slope_remove_2, intercept_remove_2 = psd_noise_2.lin_reg_spec_slope(averaging=False)
            psd_1 = psd_noise_1.remove_noisy_epochs(mean_psd_1, slope_remove_1, intercept_remove_1)
            psd_2 = psd_noise_2.remove_noisy_epochs(mean_psd_2, slope_remove_2, intercept_remove_2)
            average_psd = average_power_df(psd_1, psd_2)
            if animal in GRIN_het_IDs:
                    genotype = 'GRIN2B'
            else:
                    genotype = 'WT'
            dict_data = {'Animal_ID': [animal]*len(frequency_1), 'Channel': [channelnumber]*len(frequency_1), 'Power': average_psd, 
                        'Frequency': frequency_1, 'Genotype' : [genotype]*len(frequency_1)}
            average_df.append(pd.DataFrame(data=dict_data))


average_df = pd.concat(average_df, axis = 0).drop_duplicates().reset_index(drop = True)
seizure_concat_df = pd.concat(seizure_epochs, axis = 1).drop_duplicates().reset_index(drop = True)
os.chdir('/home/melissa/RESULTS/GRIN2B')
average_df.to_csv(str(brain_state_number) + '_seizure_free_power.csv', index = True)
seizure_concat_df.to_csv(str(brain_state_number) + '_seizure_indices_per_animal.csv', index = True)

