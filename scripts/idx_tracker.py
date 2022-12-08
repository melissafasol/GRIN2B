import os 
import numpy as np 
import pandas as pd
import scipy
from scipy.fft import fft, fftfreq
from scipy import signal

from filter import Filter


class IDX_tracker(Filter):
    
    
    def __init__(self, brain_state_file, timevalues_array):
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

        for idx_value, timevalue in zip(self.df_index['Time_Idx'], self.df_index['Time_Value']):
            start_time_bin = timevalue
            end_time_bin = timevalue + epoch_bins
            eeg_values = filtered_data[start_time_bin: end_time_bin]
            for data_point in eeg_values:
                if data_point >= self.noise_limit:
                    noisy_epochs.append(idx_value)
                    break

        for idx_value, timevalue in zip(self.df_index['Time_Idx'], self.df_index['Time_Value']):
            if idx_value not in noisy_epochs:
                start_time_bin = timevalue 
                end_time_bin = timevalue + epoch_bins
                eeg_values = filtered_data[start_time_bin: end_time_bin]
                clean_epochs.append({str(idx_value): eeg_values})

        
        clean_concat = {key:val for d in clean_epochs for key,val in d.items()}
        
        return clean_concat