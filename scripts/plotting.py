import os 
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_by_animal(dataframe_to_plot, genotype, sleepstage, save_path, plots_list, plotting_palette):
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
                animal_data = dataframe_to_plot[dataframe_to_plot["Animal_ID"] == plot[animal_idx]]
                sns.lineplot(data=animal_data, x='Frequency', y='Power', hue='Channel', ax=axs[col_idx], palette = plotting_palette)
                #axs[row_idx, col_idx].text(0.5, 0.5, plot[animal_idx], fontsize=12) #test that plt functions are rendering correctly 
                plt.suptitle(str(genotype) + ' ' + str(sleepstage), fontsize = 30, fontweight = 'bold') 
                sns.despine()
                plt.yscale('log')
                axs[0].set_xlim(1, 100)
                axs[1].set_xlim(1, 100)
                axs[0].set(xlabel = 'Frequency')
                axs[1].set(xlabel = 'Frequency')
                axs[0].set_ylim(10**-3, 10**5)
                axs[0].set(ylabel = 'PSD [V**2/Hz]')
            for row_idx in range(1):
                for col_idx in range(2):
                        axs[col_idx].set_title(plot[pos_idx_to_animal_idx(row_idx, col_idx)], 
                                                fontsize = 10, fontweight = 'bold')
        os.chdir(save_path)
        plt.savefig(str(genotype) + '_' + str(sleepstage) + '_' + str(plot) + '.jpg', bbox_inches = 'tight')


def plot_by_channel_region(df, sleepstage, save_path):
    
    somatosensory = df[df["Channel"].isin([0])] #, 7, 10, 15])]
    motor = df[df["Channel"].isin([2])] #, 3, 4, 11, 12, 13])]
    visual = df[df["Channel"].isin([5])] #, 6, 8, 9])]
    
    plot_list = [somatosensory, motor, visual]
    plot_labels = ['Somatosensory', 'Motor', 'Visual']
    label_list = [0,1, 2]
    
    for region_plot, plot_label, label_idx in zip(plot_list,plot_labels, label_list):
        fig, axs = plt.subplots(1,1, figsize=(15,10), sharex = True, sharey=True)
        order_plots = ['GRIN2B', 'WT']
        region_palette = ['orangered', 'teal']
        sns.lineplot(data=region_plot, x='Frequency', y='Power', hue ='Genotype', hue_order = order_plots, palette = region_palette)
        plt.suptitle(str(plot_labels[label_idx]) + ' ' + str(sleepstage), fontsize = 30, fontweight = 'bold') 
        plt.yscale('log')
        plt.xlim(1, 100)
        plt.xlabel('Frequency', fontsize=20)
        plt.ylim(10**-3, 10**5)
        plt.ylabel(ylabel = 'PSD [V**2/Hz]', fontsize=20)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize = 15)
        os.chdir(save_path)
        plt.savefig(str(plot_labels[label_idx]) + '_' + str(sleepstage) + '.jpg', bbox_inches = 'tight')
        plt.show()
        plt.clf()