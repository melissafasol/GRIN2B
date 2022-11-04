import os 
import numpy as np 
import pandas as pd
from scipy import average, gradient
import sys 
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, seizure_free_IDs, GRIN_het_IDs
from prepare_files import PrepareGRIN2B, LoadGRIN2B, removing_seizure_epochs, clean_indices
from power import PowerSpectrum, RemoveNoisyEpochs
from filter import Filter

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing')
from preproc2_extractbrainstate import ExtractBrainStateIndices

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
brain_state_number = 0
channel_number_list =  [0,2,3,4,5,6,7,8,9,10,11,12,13,15]
seizure_epochs = []
average_df = []
noisy_ids = ['238', '132', '430', '382']
animals_exclude_seizures = ['140', '238', '362', '365', '375', '378', '401', '402', '404']
save_plot_directory = '/home/melissa/RESULTS/GRIN2B/WAKE/wake_cleaning'


for animal in br_animal_IDs:
    if animal in animals_exclude_seizures:
        print(str(animal) + ' in seizure free id')
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
            mean_psd_1, frequency_1, noisy_epochs_1 = power_1.average_psd(average='False')
            mean_psd_2, frequency_2, noisy_epochs_2 = power_2.average_psd(average='False')
            results_psd = pd.DataFrame(data = {'Power_1': mean_psd_1, 'Power_2': mean_psd_2})
            results_noisy_epochs = pd.DataFrame(data = {'Power_1': noisy_epochs_1, 'Power_2': noisy_epochs_2})
            average_psd = results_psd[['Power_1', 'Power_2']].mean(axis = 1)
            average_noisy_epochs = results_noisy_epochs[['Power_1', 'Power_2']].mean(axis = 1)
            psd_plot = average_psd.tolist()
            noisy_epochs_plot = average_noisy_epochs.tolist()
            save_plot_as_psd = str(animal) + '_' + str(channelnumber) + '_cleanepochs_'
            save_plot_as_noise = str(animal) + '_' + str(channelnumber) + '_noisyepochs_'
            plots_ = power_1.plotting_psd(psd_plot, frequency_1, save_plot_directory, save_plot_as_psd)
            plots_noisy = power_1.plotting_psd(noisy_epochs_plot, frequency_1, save_plot_directory, save_plot_as_noise)
            if animal in GRIN_het_IDs:
                    genotype = 'GRIN2B'
            else:
                    genotype = 'WT'
            dict_data = {'Animal_ID': [animal]*626, 'Channel': [channelnumber]*626, 'Power': average_psd[0:626], 
                        'Frequency': frequency_1[0:626], 'Genotype' : [genotype]*626}
            average_df.append(pd.DataFrame(data=dict_data))
    else:
        print(str(animal) + ' seizure pipeline beginning')
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
            seizure_epochs_2 = removing_seizure_epochs(br_2, timevalues_array_2)
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
            mean_psd_1, frequency_1, noisy_epochs_1 = power_1.average_psd(average='False')
            mean_psd_2, frequency_2, noisy_epochs_2 = power_2.average_psd(average='False')
            results_psd = pd.DataFrame(data = {'Power_1': mean_psd_1, 'Power_2': mean_psd_2})
            results_noisy_epochs = pd.DataFrame(data = {'Power_1': noisy_epochs_1, 'Power_2': noisy_epochs_2})
            average_psd = results_psd[['Power_1', 'Power_2']].mean(axis = 1)
            average_noisy_epochs = results_noisy_epochs[['Power_1', 'Power_2']].mean(axis = 1)
            psd_plot = average_psd.tolist()
            noisy_epochs_plot = average_noisy_epochs.tolist()
            save_plot_as_psd = str(animal) + '_' + str(channelnumber) + '_cleanepochs_'
            save_plot_as_noise = str(animal) + '_' + str(channelnumber) + '_noisyepochs_'
            plots_ = power_1.plotting_psd(psd_plot, frequency_1, save_plot_directory, save_plot_as_psd)
            plots_noisy = power_1.plotting_psd(noisy_epochs_plot, frequency_1, save_plot_directory, save_plot_as_noise)    
            results = pd.DataFrame(data = {'Power_1': mean_psd_1, 'Power_2': mean_psd_2})
            average_psd = results[['Power_1', 'Power_2']].mean(axis = 1)
            if animal in GRIN_het_IDs:
                    genotype = 'GRIN2B'
            else:
                    genotype = 'WT'
            dict_data = {'Animal_ID': [animal]*626, 'Channel': [channelnumber]*626, 'Power': average_psd[0:626], 
                        'Frequency': frequency_1[0:626], 'Genotype' : [genotype]*626}
            average_df.append(pd.DataFrame(data=dict_data))

average_df = pd.concat(average_df, axis = 0).drop_duplicates().reset_index(drop = True)
os.chdir('/home/melissa/RESULTS/GRIN2B/wake_cleaning')
average_df.to_csv(str(brain_state_number) + '_testing_cleaning_4/11.csv', index = True)

