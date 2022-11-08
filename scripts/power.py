import numpy as np
import pandas as pd 
import scipy 
import matplotlib.pyplot as plt
import os
from statistics import mean
import math

class PowerSpectrum:
    
    def __init__(self, data_without_noise, nperseg):
        self.data_without_noise = data_without_noise
        self.nperseg = nperseg
        self.welch_channel = []

        
    def average_psd(self, average, cleaning, save_directory, animal, channel): 
        if average == 'True':
            for data_array in self.data_without_noise:
                power_calculations = scipy.signal.welch(data_array, window = 'hann', fs = 250.4, nperseg = self.nperseg)
                power_spectrum_list = [power_array[1] for power_array in power_calculations]
                frequency = power_calculations[0]
                df_psd = pd.DataFrame(power_spectrum_list)
                mean_values = df_psd.mean(axis = 0)
                mean_psd = mean_values.to_numpy()
                return mean_psd, frequency
        else:
            threshold_power = []
            noisy_epochs = []
            for data_array in enumerate(self.data_without_noise):
                power_calculations = scipy.signal.welch(data_array[1], window = 'hann', fs = 250.4, nperseg = self.nperseg)
                frequency = power_calculations[0]
                if mean(power_calculations[1]) > 1000 or mean(power_calculations[1]) < 0.00001:
                    noisy_epochs.append(power_calculations[1])
                else:
                    threshold_power.append(power_calculations[1])
                    plot_per_epoch = power_calculations[1]
                    print('test plot') 
                    plt.semilogy(frequency[0:626], plot_per_epoch[0:626])
                    plt.yscale('log')
                    plt.xlim(0, 100)
                    plt.ylim(10**-5, 10**5)
                    os.chdir(save_directory)
                    plt.savefig('epoch_number' + str(data_array[0]) + '_' + str(animal) + '_' + str(channel) + 'wake_testing_thresholds.jpg')
                    plt.clf()
                        
       
            df_psd = pd.DataFrame(threshold_power)
            mean_values = df_psd.mean(axis = 0)
            mean_psd = mean_values.to_numpy()

            df_noisy_epochs = pd.DataFrame(noisy_epochs)
            mean_noisy_epochs_df = df_noisy_epochs.mean(axis=0)
            mean_noisy_epochs = mean_noisy_epochs_df.to_numpy()

            return mean_psd, frequency, mean_noisy_epochs
                
    
    def plotting_psd(self, power_array, frequency_array, save_directory, save_as):
        plt.semilogy(frequency_array[0:626], power_array[0:626])
        #x, y = np.polyfit(frequency_array, power_array, 1)
        #plt.plot(x, y)
        plt.yscale('log')
        plt.xlim(0, 100)
        plt.ylim(10**-2, 10**5)
        plt.xlabel('frequency [Hz]')
        plt.ylabel('PSD [V**2/Hz]')
        os.chdir(save_directory)
        plt.savefig(str(save_as)+ 'wake_testing_thresholds.jpg')
        plt.clf()
       
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
        
        