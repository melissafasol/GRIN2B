import os 
import numpy as np 
import pandas as pd
from scipy import average, gradient
import sys 
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs
from preparefiles import PrepareGRIN2B, LoadGRIN2B

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts')
from preproc2_extractbrainstate import ExtractBrainStateIndices
from preproc3_filter import Filter
from preproc4_power_spectrum_analysis import PowerSpectrum, RemoveNoisyEpochs
from save_functions import average_power_df, concatenate_files, power_df, save_files, spectral_slope_save


directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
br_animal_IDs = ['375']
brain_state_number = 0
channel_number_list =  [1] #[0,2,3,4,5,6,7,8,9,10,11,12,13,15]
power_two_brainstate_df = []
spectral_slope_two_brainstate_df = [] 
average_df = []

for animal in br_animal_IDs:
    prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
    recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files()
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
        filtered_data_1 = filter_1.butter_bandpass()
        filtered_data_2 = filter_2.butter_bandpass()
        print('filtering complete')
        power_1 = PowerSpectrum(filtered_data_1)
        power_2 = PowerSpectrum(filtered_data_2)
        mean_psd_1, frequency_1 = power_1.average_psd()
        mean_psd_2, frequency_2 = power_2.average_psd()
        psd_noise_1 = RemoveNoisyEpochs(mean_psd_1, frequency_1)
        psd_noise_2 = RemoveNoisyEpochs(mean_psd_2, frequency_2)
        slope_1, intercept_1, slope_remove_1, intercept_remove_1 = psd_noise_1.lin_reg_spec_slope(averaging=False)
        slope_2, intercept_2,slope_remove_2, intercept_remove_2 = psd_noise_2.lin_reg_spec_slope(averaging=False)
        #average_slope_df = pd.DataFrame(data =  {'Animal_ID':[animal], 'Channel': [channelnumber], 'Slope_1': [slope_1],
                                               # 'Slope_2': [slope_2], 'Intercept_1': [intercept_1], 'Intercept_2': intercept_2})
        #average_df.append(average_slope_df)
        #print(average_df)
        psd_1 = psd_noise_1.remove_noisy_epochs(mean_psd_1, slope_remove_1, intercept_remove_1)
        psd_2 = psd_noise_2.remove_noisy_epochs(mean_psd_2, slope_remove_2, intercept_remove_2)
        average_psd = average_power_df(psd_1, psd_2)
        power_data = power_df(animal, average_psd, channelnumber, brain_state_number, frequency=frequency_1)
        print('power calculated and saved')
        spectral_slope_data_1 = spectral_slope_save(animal, channelnumber, brain_state_number, slope_1, intercept_1)
        spectral_slope_data_2 = spectral_slope_save(animal, channelnumber, brain_state_number, slope_2, intercept_2)
        power_two_brainstate_df.append(power_data)
        spectral_slope_two_brainstate_df.append(spectral_slope_data_1)
        spectral_slope_two_brainstate_df.append(spectral_slope_data_2)
        print('spectral slope calculated and saved')


#merged_slope_intercept_df = pd.concat(average_df, axis = 0).drop_duplicates().reset_index(drop = True)
#os.chdir('/home/melissa/RESULTS/GRIN2B/average_slope_intercept')
#merged_slope_intercept_df.to_csv(str(brain_state_number) + 'average_slope_intercept.csv', index = True)

power_dataframe, spectral_slope_dataframe = concatenate_files(power_file_to_concatenate=power_two_brainstate_df, gradient_intercept_to_concatenate=spectral_slope_two_brainstate_df)

print(power_dataframe)

save_directory = '/home/melissa/RESULTS/GRIN2B/stricter_threshold_oct_22'
save_files(directory_name = save_directory, concatenated_power_file = power_dataframe, concatenated_slope_file = spectral_slope_dataframe, brain_state_number=brain_state_number, condition = 'emg') #condition = 'baseline')

