import os 
import pandas as pd
import numpy as np
import scipy 
from scipy import average, gradient, signal
import sys

from prepare_files import PrepareGRIN2B
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/PowerFeatureAnalysis/')
from Filter import Filter

channel_number_list =  [0,2,3,4,5,6,7,8,9,10,11,12,13,15]
sampling_rate = 250.4
epoch_length = 1252
brain_state_number = 4

br_animal_seiz = ['130', '129', '131', '132', '137', '138', '139', '227', '229', '236', '237',
                  '239', '240', '241', '363', '364', '366', '367', '368', '369', '371', '373', '382', 
                  '383', '424', '430', '433']

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/RESULTS/GRIN2B/PAPER/DATASETS/brainstate_quantification/Integrated_Seiz_Brainstates/'
save_path = '/home/melissa/RESULTS/GRIN2B/PAPER/SEIZURE_POWER_DF'

def time_values(br_1):
    if 'Unnamed: 0' in br_1.columns:
        br_1.drop(['Unnamed: 0'], axis = 1, inplace = True)
    elif 'Unnamed: 0.1' in br_1.columns:
        br_1.drop(['Unnamed: 0.1'], axis = 1, inplace = True)
    else:
        pass 
    
    seiz_time_values = br_1.loc[br_1['brainstate'] == 4]
    start = seiz_time_values['start_epoch'].to_numpy()
    end = seiz_time_values['end_epoch'].to_numpy()
    time_values = []
    for st_time, ed_time in zip(start, end):
        samp_st = int(st_time*250.4)
        samp_ed = int(ed_time*250.4)
        if st_time == ed_time:
            pass
        else:
            time_array = np.arange(samp_st, samp_ed, epoch_length)
            time_values.append(time_array)
            
    concat_time = np.concatenate(time_values)
    return concat_time

def power_function(array_1d):
    power_calc = scipy.signal.welch(array_1d, window = 'hann', fs = 250.4, nperseg = 1252)
    return power_calc[1]

for animal in br_animal_seiz:
    animal = str(animal)
    print('calculating power values for ' + animal)
    prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
    recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    #load recording from start in all channels
    data_1 = recording[:, start_time_1: end_time_1 + 1]
    data_2 = recording[:, start_time_2: end_time_2 + 1]
    
    #load brainstate files for seizure files and return time array
    os.chdir(seizure_br_path)
    br_1 = pd.read_csv(str(animal) + '_BL1.csv')
    br_2 = pd.read_csv(str(animal) + '_BL2.csv')

    #filter dataset across all channels
    filter_data_array_1 = Filter(data_1)
    filter_data_array_2 = Filter(data_2)
    filtered_data_1 = filter_data_array_1.butter_bandpass()
    filtered_data_2 = filter_data_array_1.butter_bandpass()
    
    time_1 = time_values(br_1)
    time_2 = time_values(br_2)
    
    #calculating power for each bin 
    power_values_1 = []
    power_values_2 = []
    
    for time in time_1:
        time_end = time + 1253
        data_bin = filtered_data_1[:, time:time_end]
        power_calculations = np.apply_along_axis(power_function, 1, data_bin)
        power_values_1.append(power_calculations)
    
    for time in time_2:
        time_end = time + 1253
        data_bin = filtered_data_2[:, time: time_end]
        power_calculations = np.apply_along_axis(power_function, 1, data_bin)
        power_values_2.append(power_calculations)
     
    #averaging across channels in br_1 and br_2
    test_avg_1 = np.mean(power_values_1, axis=0)
    test_avg_2 = np.mean(power_values_2, axis=0)
    #averaging br_1 and br_2 into one array
    total_avg = (test_avg_1 + test_avg_2)/2
    os.chdir(save_path)
    np.save(animal + '_harmonics_seizure_avg_power.npy', total_avg)
    print('total average calculated and saved for ' + animal)