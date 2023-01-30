import EntropyHub as EH
import random 
import os 
import numpy as np 
import pandas as pd
from scipy import average, gradient
from scipy.fft import fft, fftfreq
from scipy import signal
import sys


sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, GRIN_het_IDs
from prepare_files import PrepareGRIN2B, LoadGRIN2B, br_seizure_files, one_second_timebins 
from filter import Filter
from power import PowerSpectrum, RemoveNoisyEpochs


sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing')
from preproc2_extractbrainstate import ExtractBrainStateIndices

directory_npy_path = '/home/melissa/PREPROCESSING/GRIN2B/GRIN2B_numpy'
seizure_br_path = '/home/melissa/PREPROCESSING/GRIN2B/seizures'
sampling_rate = 250.4
channel_number_list = [0,2,3,4,5,6,7,8,9,10,11,12,13,15]

animals_exclude_seizures = ['140', '238', '362', '365', '375', '378', '401', '402', '404']
animals_seizure_list = []
for animal in br_animal_IDs:
    if animal not in animals_exclude_seizures:
        animals_seizure_list.append(animal)

ent_df_1 = [] 
ent_df_2 = []
conf_df_1 = []
conf_df_2 = []

for animal in animals_seizure_list:
    prepare_GRIN2B = PrepareGRIN2B(directory_npy_path, animal)
    recording = prepare_GRIN2B.load_two_analysis_files(seizure = 'True')
    start_time_1, start_time_2 = prepare_GRIN2B.get_two_start_times(start_time_GRIN2B_baseline)
    end_time_1, end_time_2 = prepare_GRIN2B.get_end_times(end_time_GRIN2B_baseline)
    os.chdir(seizure_br_path)
    br_1 = pd.read_csv('GRIN2B_' + str(animal) + '_BL1_Seizures.csv')
    br_2 = pd.read_csv('GRIN2B_' + str(animal) + '_BL2_Seizures.csv')
    zipped_timevalues_1 = br_seizure_files(br_1, sampling_rate)
    zipped_timevalues_2 = br_seizure_files(br_2, sampling_rate)
    if len(zipped_timevalues_1) > 0:
        for channelnumber in channel_number_list:
            load_GRIN2B = LoadGRIN2B(recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber)
            data_1, data_2 = load_GRIN2B.load_GRIN2B_from_start()
            timevalues_1 = one_second_timebins(zipped_timevalues_1,  epoch_length = int(250.4))
            timevalues_2 = one_second_timebins(zipped_timevalues_2,  epoch_length = int(250.4))
            filter_1 = Filter(data_1, timevalues_1)
            filtered_data_1 = filter_1.butter_bandpass(seizure = 'True')
            filter_2 = Filter(data_2, timevalues_2)
            filtered_data_2 = filter_2.butter_bandpass(seizure = 'True')
            if len(filtered_data_1) > 0:
                for i in range(len(filtered_data_1)):
                    Dispx_1, Ppi_1 = EH.DispEn(filtered_data_1[i], m = 3, tau = 2, c = 4, Typex = 'ncdf') #refine = True
                    d = {'Dispx' + '_' + str(animal) + '_' + str(channelnumber): Dispx_1}
                    c = {'Ppi' + '_' + str(animal) + '_' + str(channelnumber): Ppi_1}
                    ent_df_1.append(pd.DataFrame(data = d, index = [i]))
                    conf_df_1.append(pd.DataFrame(data = c, index = [i]))
            if len(filtered_data_2) > 0:
                for i in range(len(filtered_data_2)):
                    Dispx_2, Ppi_2 = EH.DispEn(filtered_data_2[i], m = 3, tau = 2, c = 4, Typex = 'ncdf') #refine = True
                    d = {'Dispx' + '_' + str(animal) + '_' + str(channelnumber): Dispx_2}
                    c = {'Ppi' + '_' + str(animal) + '_' + str(channelnumber): Ppi_2}
                    ent_df_2.append(pd.DataFrame(data = d, index = [i]))
                    conf_df_2.append(pd.DataFrame(data = c, index = [i]))

entro_df_1 = pd.concat(ent_df_1, axis = 1)
entro_df_2 = pd.concat(ent_df_2, axis = 1)


os.chdir('/home/melissa/RESULTS/GRIN2B/Entropy')
entro_df_1.to_pickle("dispent_seizure_GRIN2B_1.pkl")
entro_df_2.to_pickle("dispent_seizure_GRIN2B_2.pkl")

concat_df_1 = pd.concat(conf_df_1, axis = 1)
concat_df_2 = pd.concat(conf_df_2, axis = 1)


os.chdir('/home/melissa/RESULTS/GRIN2B/Entropy')
concat_df_1.to_pickle("disppi_seizure_GRIN2B_1.pkl")
concat_df_2.to_pickle("disppi_seizure_GRIN2B_2.pkl")