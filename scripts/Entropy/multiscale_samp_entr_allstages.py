import EntropyHub as EH
import random 
import os 
import sys
import numpy as np 
import pandas as pd
from scipy import average, gradient
import scipy
from scipy.fft import fft, fftfreq
from scipy import signal

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, GRIN_het_IDs
from prepare_files import PrepareGRIN2B, LoadGRIN2B 
from filter import Filter

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing')
from preproc2_extractbrainstate import ExtractBrainStateIndices

br_animal_IDs = ['131', '137', '378', '382', '383', '401', '402', '404','424', '430','433',
                '140', '129', '130', '132','138', '139', '227',
                '228', '229', '236', '237', '238', '239', '240', '241', '362',
                '363', '364', '365', '366', '367', '368', '369', '371', '373', '375']

channel_number_list = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]

directory_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
save_path = '/home/melissa/RESULTS/GRIN2B/Entropy/MULTISCALE_SAMP/'
brain_state_number = 2

for animal in br_animal_IDs:
    animal = str(animal)
    prepare_GRIN2B = PrepareGRIN2B(directory_path, animal)
    recording, brain_state_1, brain_state_2 = prepare_GRIN2B.load_two_analysis_files(seizure = 'False')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    channel_df = []
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
        filtered_data_1 = filter_1.butter_bandpass_entropy_time(seizure = 'False')
        filtered_data_2 = filter_2.butter_bandpass_entropy_time(seizure = 'False')
        one_epoch_multi_samp_1 = []
        one_epoch_ci_1 = []
        one_epoch_multi_samp_2 = []
        one_epoch_ci_2 = []
        for epoch in filtered_data_1:
            Mobj = EH.MSobject('SampEn', m = 1, r = 0.2)
            Mobj.Func
            MSx, Ci = EH.cMSEn(epoch, Mobj, Scales = 5, RadNew = 0) 
            one_epoch_multi_samp_1.append(MSx)
            one_epoch_ci_1.append(Ci)
        one_chan_multi_samp_1 = np.concatenate(one_epoch_multi_samp_1)
        channel_dict_1 = {'Animal_ID': [animal]*len(one_chan_multi_samp_1), 'Multi_Samp_En': one_chan_multi_samp_1,
                'Ci_En': [one_epoch_ci_1]*len(one_chan_multi_samp_1), 'Channel': [channelnumber]*len(one_chan_multi_samp_1)}
        channel_data_1 = pd.DataFrame(data = channel_dict_1)
        channel_df.append(channel_data_1)    
        for epoch in filtered_data_2:
            Mobj = EH.MSobject('SampEn', m = 1, r = 0.2)
            Mobj.Func
            MSx, Ci = EH.cMSEn(epoch, Mobj, Scales = 5, RadNew = 0) 
            one_epoch_multi_samp_2.append(MSx)
            one_epoch_ci_2.append(Ci)
        one_chan_multi_samp_2 = np.concatenate(one_epoch_multi_samp_2)
        channel_dict_2 = {'Animal_ID': [animal]*len(one_chan_multi_samp_2), 'Multi_Samp_En': one_chan_multi_samp_2,
                'Ci_En': [one_epoch_ci_2]*len(one_chan_multi_samp_2), 'Channel': [channelnumber]*len(one_chan_multi_samp_2)}
        channel_data_2 = pd.DataFrame(data = channel_dict_2)
        channel_df.append(channel_data_2)
    animal_df = pd.concat(channel_df)
    os.chdir(save_path)
    animal_df.to_csv(str(animal) + '_samp_en.csv')              
        
            
        
    