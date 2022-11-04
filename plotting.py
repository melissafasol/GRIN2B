import os 
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_seizures_mutant(dataframe_to_plot, genotype, sleepstage, save_path):
    mutant_list_1 = [131, 130, 129, 228]
    mutant_list_2 = [227, 229, 373, 138]
    mutant_list_3 =  [ 137, 139, 236, 237]
    mutant_list_4 = [  239, 241, 364, 367]
    mutant_list_5 = [368, 424, 433, 228]
    
    plots_list = [mutant_list_1, mutant_list_2, mutant_list_3, mutant_list_4, mutant_list_5]
    
    
    def pos_idx_to_animal_idx(row_idx, col_idx):
        return row_idx * 2 + col_idx
    
    for plot in plots_list:
        sns.set_style("white") 
        fig, axs = plt.subplots(2,2, figsize=(30,20), sharex = True, sharey=True)
        print(plot)
        for row_idx in range(2):
            for col_idx in range(2):
                animal_idx = pos_idx_to_animal_idx(row_idx, col_idx)
                animal_data = dataframe_to_plot[dataframe_to_plot["Animal_ID"] == plot[animal_idx]]
                sns.lineplot(data=animal_data, x='Frequency', y='Power', hue='Channel', ax=axs[row_idx, col_idx])
                #axs[row_idx, col_idx].text(0.5, 0.5, plot[animal_idx], fontsize=12) #test that plt functions are rendering correctly 
                plt.suptitle(str(genotype) + ' ' + str(sleepstage), fontsize = 30, fontweight = 'bold') 
                sns.despine()
                plt.yscale('log')
                axs[1, 0].set_xlim(1, 100)
                axs[1, 1].set_xlim(1, 100)
                axs[1, 0].set(xlabel = 'Frequency')
                axs[1, 1].set(xlabel = 'Frequency')
                axs[1, 1].set_xlim(1, 100)
                axs[0, 0].set_ylim(10**-2, 10**5)
                axs[1, 1].set_ylim(10**-2, 10**5)
                axs[0,0].set(ylabel = 'PSD [V**2/Hz]')
                axs[1,0].set(ylabel = 'PSD [V**2/Hz]')
            for row_idx in range(2):
                for col_idx in range(2):
                        axs[row_idx, col_idx].set_title(plot[pos_idx_to_animal_idx(row_idx, col_idx)], 
                                                fontsize = 10, fontweight = 'bold')
        os.chdir(save_path)
        plt.savefig(str(genotype) + '_' + str(sleepstage) + '_' + str(plot) + '.jpg', bbox_inches = 'tight')


def plot_wt(dataframe_to_plot, genotype, sleepstage, save_path, plots_list):
    '''plots list is a list of 5 lists with animal ids'''
    
    def pos_idx_to_animal_idx(row_idx, col_idx):
        return row_idx * 2 + col_idx
    
    for plot in plots_list:
        sns.set_style("white") 
        fig, axs = plt.subplots(1,2, figsize=(30,10), sharex = True, sharey=True)
        print(plot)
        for row_idx in range(1):
            for col_idx in range(2):
                animal_idx = pos_idx_to_animal_idx(row_idx, col_idx)
                print(animal_idx)
                animal_data = dataframe_to_plot[dataframe_to_plot["Animal_ID"] == plot[animal_idx]]
                print(animal_data)
                sns.lineplot(data=animal_data, x='Frequency', y='Power', hue='Channel', ax=axs[col_idx])
                #axs[row_idx, col_idx].text(0.5, 0.5, plot[animal_idx], fontsize=12) #test that plt functions are rendering correctly 
                plt.suptitle(str(genotype) + ' ' + str(sleepstage), fontsize = 30, fontweight = 'bold') 
                sns.despine()
                plt.yscale('log')
                axs[0].set_xlim(1, 100)
                axs[1].set_xlim(1, 100)
                axs[0].set(xlabel = 'Frequency')
                axs[1].set(xlabel = 'Frequency')
                axs[0].set_ylim(10**-2, 10**5)
                axs[0].set(ylabel = 'PSD [V**2/Hz]')
            for row_idx in range(1):
                for col_idx in range(2):
                        axs[col_idx].set_title(plot[pos_idx_to_animal_idx(row_idx, col_idx)], 
                                                fontsize = 10, fontweight = 'bold')
        os.chdir(save_path)
        plt.savefig(str(genotype) + '_' + str(sleepstage) + '_' + str(plot) + '.jpg', bbox_inches = 'tight')

   