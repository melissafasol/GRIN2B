import os 
from os.path import exists
import numpy as np 
import pandas as pd
from scipy import average, gradient
import sys 
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, GRIN_het_IDs
from prepare_files import PrepareGRIN2B, LoadGRIN2B, br_seizure_files, one_second_timebins 
from filter import Filter
from power import PowerSpectrum, RemoveNoisyEpochs


sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts') 
from preproc2_extractbrainstate import ExtractBrainStateIndices
from save_functions import average_power_df, concatenate_files, save_files, spectral_slope_save


directory_npy_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
channel_number_list =  [0,2,3,4,5,6,7,8,9,10,11,12,13,15]

seizure_df = []

sampling_rate = 250.4
nperseg = 250


for animal in br_animal_IDs:
    prepare_GRIN2B = PrepareGRIN2B(directory_npy_path, animal)
    recording = prepare_GRIN2B.load_two_analysis_files(seizure = 'True')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    os.chdir(seizure_br_path)
    br_1 = pd.read_csv('GRIN2B_' + str(animal) + '_BL1_Seizures.csv')
    br_2 = pd.read_csv('GRIN2B_' + str(animal) + '_BL2_Seizures.csv')
    zipped_timevalues_1 = br_seizure_files(br_1, sampling_rate)
    if len(zipped_timevalues_1) > 0:
        for channelnumber in channel_number_list:
            load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)
            data_1, data_2 = load_GRIN2B.load_GRIN2B_from_start()
            timevalues_1 = one_second_timebins(zipped_timevalues_1,  epoch_length = int(250.4))
            filter_1 = Filter(data_1, timevalues_1)
            filtered_data_1 = filter_1.butter_bandpass(seizure = 'True')
            if len(filtered_data_1) > 0:
                power_1 = PowerSpectrum(filtered_data_1, nperseg = 250)
                mean_psd_1, frequency_1 = power_1.average_psd(average = 'True')
                psd_noise_1 = RemoveNoisyEpochs(mean_psd_1, frequency_1)
                slope_1, intercept_1, slope_remove_1, intercept_remove_1 = psd_noise_1.lin_reg_spec_slope(averaging=False)
                psd_1 = psd_noise_1.remove_noisy_epochs(mean_psd_1, slope_remove_1, intercept_remove_1)
                if animal in GRIN_het_IDs:
                    genotype = 'GRIN2B'
                else:
                    genotype = 'WT'
                dict_data = {'Animal_ID': [animal]*len(frequency_1), 'Channel': [channelnumber]*len(frequency_1), 'Power': psd_1, 
                    'Frequency': frequency_1, 'Genotype' : [genotype]*len(frequency_1)}
                seizure_df.append(pd.DataFrame(data=dict_data))
            else:
                print('no seizure epochs for' + str(animal))
    else:
        print('no seizure epochs for' + str(animal))
    zipped_timevalues_2 = br_seizure_files(br_2, sampling_rate)
    if len(zipped_timevalues_2) > 0:
        for channelnumber in channel_number_list:
            load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)
            data_1, data_2 = load_GRIN2B.load_GRIN2B_from_start()
            timevalues_2 = one_second_timebins(zipped_timevalues_2,  epoch_length = int(250.4))
            filter_2 = Filter(data_2, timevalues_2)
            filtered_data_2 = filter_2.butter_bandpass(seizure = 'True')
            if len(filtered_data_2) > 0:
                power_2 = PowerSpectrum(filtered_data_2, nperseg = 250)
                mean_psd_2, frequency_2 = power_2.average_psd(average = 'True')
                psd_noise_2 = RemoveNoisyEpochs(mean_psd_2, frequency_2)
                slope_2, intercept_2,slope_remove_2, intercept_remove_2 = psd_noise_2.lin_reg_spec_slope(averaging=False)
                psd_2 = psd_noise_2.remove_noisy_epochs(mean_psd_2, slope_remove_2, intercept_remove_2)
                if animal in GRIN_het_IDs:
                    genotype = 'GRIN2B'
                else:
                    genotype = 'WT'
                    dict_data = {'Animal_ID': [animal]*len(frequency_2), 'Channel': [channelnumber]*len(frequency_2), 'Power': psd_2, 
                    'Frequency': frequency_2, 'Genotype' : [genotype]*len(frequency_2)}
                seizure_df.append(pd.DataFrame(data=dict_data))
                print('data saved for ' + str(animal))
            else:
                print('no seizure epochs for' + str(animal))
    else:
        print('no seizure epochs for' + str(animal))

                 
merged_power_file = pd.concat(seizure_df, axis = 0).drop_duplicates().reset_index(drop = True)
os.chdir('/home/melissa/RESULTS/GRIN2B/seizures')
merged_power_file.to_csv(str('seizure_GRIN2B') + '_power.csv', index = True)