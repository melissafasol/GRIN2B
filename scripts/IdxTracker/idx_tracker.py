#script written in December 2022 to 

import os 
import numpy as np 
import pandas as pd
import scipy
from scipy.fft import fft, fftfreq
from scipy import signal

from filter import Filter


class IDX_tracker(Filter):
    '''Class to track indices of noisy and clean epochs to plot raw data'''
    
    def __init__(self, unfiltered_data, brain_state_file, timevalues_array):
        self.unfiltered_data = unfiltered_data
        self.brain_state_file = brain_state_file
        self.timevalues_array = timevalues_array
        self.br_idx = self.brain_state_file.index.values.tolist()
        self.list_br = list(zip(self.br_idx, timevalues_array))
        self.df_index = pd.DataFrame(self.list_br, columns = ['Time_Idx', 'Time_Value'])

    def butter_bandpass_index_tracker(self, seizure):
        '''function to keep track of original brain state indices to plot corresponding raw data indices'''
        #timevalues array should be a dataframe with one column of indices and one column of 
        noisy_epochs = []
        clean_epochs = []
        
        if seizure == 'True':
            epoch_bins = int(250.4)
        else:
            epoch_bins = 1252

        butter_b, butter_a = signal.butter(self.order, [self.low, self.high], btype='band', analog = False)
        
        filtered_data = signal.filtfilt(butter_b, butter_a, self.unfiltered_data)
        
        #check if all values exceed noisy limit and track epoch indices
        for idx_value, timevalue in zip(self.df_index['Time_Idx'], self.df_index['Time_Value']):
            start_time_bin = timevalue
            end_time_bin = timevalue + epoch_bins
            eeg_values = filtered_data[start_time_bin: end_time_bin]
            for data_point in eeg_values:
                if data_point >= self.noise_limit:
                    noisy_epochs.append(idx_value)     
                else:
                    pass
        
        #extracting clean epochs from noisy epochs
        for idx_value, timevalue in zip(self.df_index['Time_Idx'], self.df_index['Time_Value']):
            if idx_value not in noisy_epochs:
                start_time_bin = timevalue 
                end_time_bin = timevalue + epoch_bins
                eeg_values = filtered_data[start_time_bin: end_time_bin]
                clean_epochs.append({str(idx_value): eeg_values})

        
        clean_concat = {key:val for d in clean_epochs for key,val in d.items()}
        
        return clean_concat
    
    def harmonics_algo_idx(self, filtered_data, animal, channel):
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
        for key, epoch in filtered_data.items():
            power_calculations = signal.welch(epoch, window = 'hann', fs = 250.4, nperseg = 1252)
            frequency = power_calculations[0]
            slope, intercept = np.polyfit(frequency[0:626], power_calculations[1][0:626], 1)
            signals, avgfilter, stdfilter = thresholding_algo(y = power_calculations[1], lag = 30, threshold = 5, influence = 0) 
            i = np.mean(signals[25:50])
            j = np.mean(signals[60:85])
            if intercept > 500 or slope < -5:
                print('noisy_epochs')
                noisy_df = pd.DataFrame({'epoch_idx': [key], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['noise']})
                noisy_epochs.append(key)
                noisy_epochs_df.append(noisy_df)
            elif i and j > 0:
                print('seizure')
                noisy_df = pd.DataFrame({'epoch_idx': [key], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['seizure']})
                noisy_epochs_df.append(noisy_df)
                noisy_epochs.append(key)
            else: 
                clean_epochs_power.append(power_calculations[1])
                
                
        noisy_indices = [*set(noisy_epochs)]
    
        for epoch in sorted(noisy_indices, reverse=True):
            del filtered_data[epoch]
        
        df_psd = pd.DataFrame(clean_epochs_power)
        mean_values = df_psd.mean(axis = 0)
        mean_psd = mean_values.to_numpy()
                
        return noisy_epochs_df, mean_psd, frequency
    
    def power_filtering_idx(self, filtered_data, animal, channel):
        
        noisy_epochs_df = []
        noisy_epochs = []
        clean_epochs_power = []
        for key, epoch in filtered_data.items():
            power_calculations = signal.welch(epoch, window = 'hann', fs = 250.4, nperseg = 1252)
            frequency = power_calculations[0]
            slope, intercept = np.polyfit(frequency[0:626], power_calculations[1][0:626], 1)
        
            if intercept > 500 or slope < -5:
                print('noise artifacts')
                noisy_df = pd.DataFrame({'epoch_idx': [key], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['noise']})
                noisy_epochs.append(key)
                noisy_epochs_df.append(noisy_df)
            else: 
                print('no artifacts')
                clean_epochs_power.append(power_calculations[1])
                
                
        noisy_indices = [*set(noisy_epochs)]
    
        for epoch in sorted(noisy_indices, reverse=True):
            del filtered_data[epoch]
        
        df_psd = pd.DataFrame(clean_epochs_power)
        mean_values = df_psd.mean(axis = 0)
        mean_psd = mean_values.to_numpy()
                
        return noisy_epochs_df, mean_psd, frequency
    
    
class HarmonicsPreFiltered():
        
    def __init__(self, filtered_data, brainstate):
        self.filtered_data = filtered_data
        self.brainstate = brainstate
            
            
    def harmonics_algo_idx(self, animal, channel):
            
        def thresholding_algo(y, lag, threshold, influence):
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
        if self.brainstate == 0:
            for key, epoch in self.filtered_data.items():
                power_calculations = signal.welch(epoch, window = 'hann', fs = 250.4, nperseg = 1252)
                frequency = power_calculations[0]
                slope, intercept = np.polyfit(frequency[0:626], power_calculations[1][0:626], 1)
                signals, avgfilter, stdfilter = thresholding_algo(y = power_calculations[1], lag = 30, threshold = 5, influence = 0) 
                i = np.mean(signals[25:50])
                j = np.mean(signals[60:85])
                if intercept > 500 or slope < -5:
                    print('noisy_epochs')
                    noisy_df = pd.DataFrame({'epoch_idx': [key], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['noise']})
                    noisy_epochs.append(key)
                    noisy_epochs_df.append(noisy_df)
                elif i and j > 0:
                    print('seizure')
                    noisy_df = pd.DataFrame({'epoch_idx': [key], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['seizure']})
                    noisy_epochs_df.append(noisy_df)
                    noisy_epochs.append(key)
                else: 
                    clean_epochs_power.append(power_calculations[1])
                
        else:
            for key, epoch in self.filtered_data.items():
                power_calculations = signal.welch(epoch, window = 'hann', fs = 250.4, nperseg = 1252)
                frequency = power_calculations[0]
                slope, intercept = np.polyfit(frequency[0:626], power_calculations[1][0:626], 1)
                if intercept > 500 or slope < -5:
                    print('noisy_epochs')
                    noisy_df = pd.DataFrame({'epoch_idx': [key], 'Animal_ID': [animal], 'channel': [channel], 'artifact': ['noise']})
                    noisy_epochs.append(key)
                    noisy_epochs_df.append(noisy_df)
                else: 
                    clean_epochs_power.append(power_calculations[1])
                
                
        noisy_indices = [*set(noisy_epochs)]
    
        for epoch in sorted(noisy_indices, reverse=True):
            del self.filtered_data[epoch]
        
        df_psd = pd.DataFrame(clean_epochs_power)
        mean_values = df_psd.mean(axis = 0)
        mean_psd = mean_values.to_numpy()
            
        return noisy_epochs_df, mean_psd, frequency