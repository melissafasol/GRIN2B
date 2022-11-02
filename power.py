import numpy as np
import pandas as pd 
import scipy 

class PowerSpectrum:
    
    def __init__(self, data_without_noise, nperseg):
        self.data_without_noise = data_without_noise
        self.nperseg = nperseg
        self.welch_channel = []

        
    def average_psd(self, average):
        for data_array in self.data_without_noise:
            self.welch_channel.append(scipy.signal.welch(data_array, window = 'hann', fs = 250.4, nperseg = self.nperseg))
        power_spectrum_list = [power_array[1] for power_array in self.welch_channel]
        
        #save one array of frequency values for plotting 
        frequency = self.welch_channel[0][0]
        
        df_psd = pd.DataFrame(power_spectrum_list)
        if average == 'True':
            mean_values = df_psd.mean(axis = 0)
            mean_psd = mean_values.to_numpy()
            return mean_psd, frequency
        else:
            return df_psd, frequency
    

class RemoveNoisyEpochs:
    
    def __init__(self, psd, frequency):
        self.psd = psd
        self.frequency = frequency
        self.slope_list = []
        self.intercept_list = []
        self.intercept_remove = []
        self.slope_remove = []
    
    def lin_reg_spec_slope(self, averaging):
        if averaging == 'True':
            slope, intercept = np.polyfit(self.frequency, self.psd, 1)
            self.slope_list.append(slope)
            self.intercept_list.append(intercept)
            return slope, intercept, self.slope_list, self.intercept_list

        else:
            slope, intercept = np.polyfit(self.frequency, self.psd, 1)
            self.slope_list.append(slope)
            self.intercept_list.append(intercept)

            for i, item in enumerate(self.intercept_list):
                if self.intercept_list[i] > 500:
                    self.intercept_remove.append(i)
                
            for i, item in enumerate(self.slope_list):
                if self.slope_list[i] < -5:
                    self.slope_remove.append(i)
        
            return (slope, intercept,self.slope_remove, self.intercept_remove)
    
    
    def remove_noisy_epochs(self, psd, slope_remove, intercept_remove):
        if len(self.intercept_remove) or len(self.slope_remove) > 0:
            if len(self.intercept_remove) > len(self.slope_remove):
                for i in sorted(self.intercept_remove, reverse = True):
                        del self.psd[i]
                else:
                    for i in sorted(self.slope_remove, reverse = True):
                        del self.psd[i]       
        else:
            pass
        return self.psd
        
        