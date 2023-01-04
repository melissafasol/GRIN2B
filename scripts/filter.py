from turtle import st
import scipy
from scipy.fft import fft, fftfreq
from scipy import signal
import pandas as pd

'''apply scipy butterworth bandpass filter and remove epochs with amplitudes larger than 3000mV'''

class Filter:
    
    order = 3
    sampling_rate = 250.4
    nyquist = 125.2
    low = 0.2/nyquist
    high = 100/nyquist
    noise_limit = 3000
    
    

    def __init__(self, unfiltered_data, timevalues_array):
        self.unfiltered_data = unfiltered_data
        self.timevalues_array = timevalues_array
        self.extracted_datavalues = []
        self.channel_threshold = []
        
        
    '''filter out low-frequency drifts and frequencies above 50Hz'''
     

    def butter_bandpass(self, seizure):
        '''function to filter data per channel and remove epochs above a certain mV threshold'''
        if seizure == 'True':
            epoch_bins = int(250.4)
        else:
            epoch_bins = 1252

        butter_b, butter_a = signal.butter(self.order, [self.low, self.high], btype='band', analog = False)
        
        filtered_data = signal.filtfilt(butter_b, butter_a, self.unfiltered_data)

        for timevalue in self.timevalues_array:
            start_time_bin = timevalue
            end_time_bin = timevalue + epoch_bins
            
            self.extracted_datavalues.append(filtered_data[start_time_bin: end_time_bin])

        for i in range(len(self.extracted_datavalues)):
            for j in range(len(self.extracted_datavalues[i])):
                if self.extracted_datavalues[i][j] >= self.noise_limit:
                    self.channel_threshold.append(i)
                else:
                    pass

        remove_duplicates = sorted(list(set(self.channel_threshold)))
        channels_without_noise = [i for j, i in enumerate(self.extracted_datavalues) if j not in remove_duplicates]
        return channels_without_noise 
    
    
    def butter_bandpass_all_channels_coherence(self, seizure):
        '''function to filter all 14 eeg channels to save for coherence calculations'''
        butter_b, butter_a = signal.butter(self.order, [self.low, self.high], btype='band', analog = False)
        
        filtered_data = signal.filtfilt(butter_b, butter_a, self.unfiltered_data)

        for timevalue in self.timevalues_array:
            start_time_bin = timevalue
            if seizure == 'True':
                end_time_bin = timevalue + self.seizure_epoch_bins
            else:
                end_time_bin = timevalue + self.epoch_bins
            
            self.extracted_datavalues.append(filtered_data[0:14, start_time_bin: end_time_bin])    


        for i in range(len(self.extracted_datavalues)):
            for j in range(len(self.extracted_datavalues[i])):
                if self.extracted_datavalues[i][j] >= self.noise_limit:
                    self.channel_threshold.append(i)
                else:
                    pass
    
    def butter_bandpass_entropy_time(self, seizure):
            
        if seizure == 'True':
            epoch_bins = int(250.4)
        else:
            epoch_bins = 1252

        butter_b, butter_a = signal.butter(self.order, [self.low, self.high], btype='band', analog = False)
        
        filtered_data = signal.filtfilt(butter_b, butter_a, self.unfiltered_data)

        for timevalue in self.timevalues_array:
            start_time_bin = timevalue
            end_time_bin = timevalue + epoch_bins
            
            self.extracted_datavalues.append(filtered_data[start_time_bin: end_time_bin])

        return self.extracted_datavalues