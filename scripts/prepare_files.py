import os
import sys 
from scipy import stats
from scipy import signal
import numpy as np
import pylab
import pandas as pd

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts/Preprocessing')
from preproc1_preparefiles import PrepareFiles, LoadFromStart
import matplotlib.pyplot as plt



class PrepareGRIN2B(PrepareFiles):
    
    def __init__(self, directory_path, animal_id):
        self.directory_path = directory_path
        self.animal_id = animal_id
        self.brain_1 = animal_id + '_BL1.pkl'
        self.brain_2 = animal_id + '_BL2.pkl'
        self.start_dict_1 = animal_id + '_1'
        self.start_dict_2 = animal_id + '_2'
        self.end_dict_1 = animal_id + '_1A'
        self.end_dict_2 = animal_id + '_2A'

    
    def get_end_times(self, end_times_GRIN2B_dict):
        end_time_1 = end_times_GRIN2B_dict[self.end_dict_1]
        end_time_2 = end_times_GRIN2B_dict[self.end_dict_2]
        return (end_time_1, end_time_2)

class LoadGRIN2B(LoadFromStart):

    def __init__(self, recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber):
        self.recording = recording
        self.start_time_1 = start_time_1
        self.start_time_2 = start_time_2
        self.channelnumber = channelnumber
        self.end_time_1 = end_time_1 + 1
        self.end_time_2 = end_time_2 + 1
        
    def load_GRIN2B_from_start(self):
        data_1 = self.recording[self.channelnumber, self.start_time_1: self.end_time_1]
        data_2 = self.recording[self.channelnumber, self.start_time_2: self.end_time_2]
        return (data_1, data_2)
    

class GRIN2B_Seizures():
    
    sample_rate = 250.4

    def __init__(self, br_file, epoch_length):
        self.br_file = br_file
        self.epoch_length = epoch_length

    def br_seizure_files(self):
        '''function to reformat seizure brain states'''
        seizure_times_start = self.br_file.iloc[:, 0:1].to_numpy().astype(int)
        seizure_times_end = self.br_file.iloc[:, 1:2].to_numpy().astype(int)
        seizure_times_start_epochs = [epoch for sublist in seizure_times_start for epoch in sublist]
        seizure_times_end_epochs = [epoch for sublist in seizure_times_end for epoch in sublist]
        seizure_start_sample_rate = [int(element*self.sample_rate) for element in seizure_times_start_epochs]
        seizure_end_sample_rate = [int(element*self.sample_rate) for element in seizure_times_end_epochs]
        zipped_timevalues = list(zip(seizure_start_sample_rate , seizure_end_sample_rate)) 
    
        return zipped_timevalues  
        
    def one_second_timebins(self, timevalues_array):

        function_timebins = lambda epoch_start, epoch_end: list(range(epoch_start, epoch_end, self.epoch_length))
    
        new_epoch_times = [list(map(lambda epoch: function_timebins(int(epoch[0]), int(epoch[1])), (timevalues_array)))]

        new_time_array = [time_start for epoch in new_epoch_times for time_start in epoch]
        one_second_timebins = [time_start for epoch in new_time_array for time_start in epoch]
        return one_second_timebins

    
    def preceding_following_epochs(self, zipped_timevalues):
        
        preceding_ictal_list = []
        post_ictal_list = []
    
        for epoch in zipped_timevalues:
            one_time_bin = 250
            start_preceding = epoch[0]
            end_preceding = start_preceding - one_time_bin*60
            start_post = epoch[1]
            end_post = int(start_post + one_time_bin*60)
            preceding_epochs = np.arange(end_preceding, start_preceding - one_time_bin, one_time_bin)
            preceding_ictal_list.append(preceding_epochs)
            post_epochs = np.arange(start_post + one_time_bin, end_post, one_time_bin)
            post_ictal_list.append(post_epochs)
    
        #preceding_ictal_epochs = np.concatenate([epoch for epoch in preceding_ictal_list])
        #post_ictal_epochs = np.concatenate([epoch for epoch in post_ictal_list])

        return preceding_ictal_list, post_ictal_list

    
    def removing_seizure_epochs(self, wake_indices):
    
        def round_to_multiple(number, multiple):
            return multiple*round(number/multiple)
    
        seizure_times_start = self.br_file.iloc[:, 0:1].to_numpy().astype(int)
        seizure_times_start_epochs = [epoch for sublist in seizure_times_start for epoch in sublist]
        testing_multiples = [round_to_multiple(i, 5) for i in seizure_times_start_epochs] 
        sample_rate_indices = [int(epoch*250.4) for epoch in testing_multiples]
    
        
        all_ictal_epochs = []
        
        for seizure_epoch in sample_rate_indices:
            if seizure_epoch in wake_indices:
                epoch_bins = 1252    
                preceding_epochs = [seizure_epoch - epoch_bins*5, seizure_epoch - epoch_bins*4, seizure_epoch - epoch_bins*3, seizure_epoch - epoch_bins*2, seizure_epoch - epoch_bins]
                following_epochs = [seizure_epoch + epoch_bins, seizure_epoch + epoch_bins*2, seizure_epoch + epoch_bins*3, seizure_epoch + epoch_bins*4, seizure_epoch + epoch_bins*5 ]
                all_ictal_epochs.extend(preceding_epochs + [seizure_epoch] + following_epochs)
            
        return all_ictal_epochs
    
    
    def clean_indices(self, timevalues_array, all_ictal_epochs):
        new_indices = []
        for epoch in timevalues_array:
            if epoch not in all_ictal_epochs:
                new_indices.append(epoch)

        return new_indices


    def harmonics_algo(self, filtered_data, save_directory, animal, channel):
        def thresholding_algo( y, lag, threshold, influence):
            signals = np.zeros(len(y))
            filteredY = np.array(y)
            avgFilter = [0]*len(y)
            stdFilter = [0]*len(y)
            avgFilter[lag - 1] = np.mean(y[0:lag])
            stdFilter[lag - 1] = np.std(y[0:lag])
            for i in range(lag, len(y)):
                if abs(y[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
                    if y[i] > avgFilter[i-1]:
                        signals[i] = 1
                    else:
                        signals[i] = -1

                    filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i-1]
                    avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
                    stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
                else:
                    signals[i] = 0
                    filteredY[i] = y[i]
                    avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
                    stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

            return np.asarray(signals),np.asarray(avgFilter),np.asarray(stdFilter)


        noisy_epochs_df = []
        noisy_epochs = []
        clean_epochs_power = []
        for epoch_idx, epoch in enumerate(filtered_data):
            power_calculations = signal.welch(epoch, window = 'hann', fs = 250.4, nperseg = 1252)
            frequency = power_calculations[0]
            slope, intercept = np.polyfit(frequency[0:626], power_calculations[1][0:626], 1)
            signals, avgfilter, stdfilter = thresholding_algo(y = power_calculations[1], lag = 30, threshold = 5, influence = 0) 
            i = np.mean(signals[25:50])
            j = np.mean(signals[60:85])
            if intercept > 500 or slope < -5:
                #print('noise artifacts')
                noisy_df = pd.DataFrame({'epoch_idx': [epoch_idx], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['noise']})
                noisy_epochs.append(epoch_idx)
                noisy_epochs_df.append(noisy_df)
            elif i and j > 0:
                noisy_df = pd.DataFrame({'epoch_idx': [epoch_idx], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['seizure']})
                noisy_epochs_df.append(noisy_df)
                noisy_epochs.append(epoch_idx)
                #print('seizure artifacts') 
                #plt.semilogy(frequency[0:626], power_calculations[1][0:626])
                #plt.yscale('log')
                #plt.xlim(0, 100)
                #plt.ylim(10**-5, 10**5)
                #os.chdir(save_directory)
                #plt.savefig('epoch_number' + str(epoch_idx) + '_' + str(animal) + '_' + str(channel) + 'discarded_epoch.jpg')
                #plt.clf()
            else:            
                clean_epochs_power.append(power_calculations[1])
                #print('clean plot') 
                #plt.semilogy(frequency[0:626], power_calculations[1][0:626])
                #plt.yscale('log')
                #plt.xlim(0, 100)
                #plt.ylim(10**-5, 10**5)
                #os.chdir(save_directory)
                #plt.savefig('epoch_number' + str(epoch_idx) + '_' + str(animal) + '_' + str(channel) + 'included_epoch.jpg')
                #plt.clf()
                
        noisy_indices = [*set(noisy_epochs)]
    
        for epoch in sorted(noisy_indices, reverse=True):
            del filtered_data[epoch]
        
        df_psd = pd.DataFrame(clean_epochs_power)
        mean_values = df_psd.mean(axis = 0)
        mean_psd = mean_values.to_numpy()
                
        return noisy_epochs_df, mean_psd, frequency