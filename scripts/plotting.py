import os 
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from GRIN2B_constants import channel_dict


class PlottingGRIN2B():
    
    lower_x_lim = 1
    upper_x_lim = 48
    x_ax_label = 'Frequency (Hz)'
    lower_y_lim = 10**-3
    upper_y_lim = 10**3
    y_ax_label = 'PSD [V**2/Hz]'
    
    def __init__(self):
        pass


    def plot_by_animal(self, dataframe_to_plot, genotype, sleepstage, save_path, plots_list, plotting_palette):
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
                    axs[0].set_xlim(PlottingGRIN2B.lower_x_lim, PlottingGRIN2B.upper_x_lim)
                    axs[1].set_xlim(PlottingGRIN2B.lower_x_lim, PlottingGRIN2B.upper_x_lim)
                    axs[0].set(xlabel = PlottingGRIN2B.x_ax_label)
                    axs[1].set(xlabel = PlottingGRIN2B.x_ax_label)
                    axs[0].set_ylim(PlottingGRIN2B.lower_y_lim, PlottingGRIN2B.upper_y_lim)
                    axs[0].set(ylabel = PlottingGRIN2B.y_ax_label)
                for row_idx in range(1):
                    for col_idx in range(2):
                            axs[col_idx].set_title(plot[pos_idx_to_animal_idx(row_idx, col_idx)], 
                                                fontsize = 10, fontweight = 'bold')
            os.chdir(save_path)
            plt.savefig(str(genotype) + '_' + str(sleepstage) + '_' + str(plot) + '.jpg', bbox_inches = 'tight')


    def plot_by_channel_region(self, df, sleepstage, save_path):
        somatosensory = df[df["Channel"].isin([7])] #0, 7, 10, 15])]
        motor = df[df["Channel"].isin([3])] #2, 3, 4, 11, 12, 13])]
        visual = df[df["Channel"].isin([6])] #5, 6, 8, 9])]
        plot_list = [somatosensory, motor, visual]
        plot_labels = ['Somatosensory'] #, 'Motor', 'Visual']
        label_list = [0,1, 2]
    
        for region_plot, plot_label, label_idx in zip(plot_list,plot_labels, label_list):
            fig, axs = plt.subplots(1,1, figsize=(15,10), sharex = True, sharey=True)
            order_plots = ['GRIN2B', 'WT']
            region_palette = ['orangered', 'teal']
            sns.lineplot(data=region_plot, x='Frequency', y='Power', hue ='Genotype', hue_order = order_plots,  ci= 95, palette = region_palette)
            plt.suptitle(str(plot_labels[label_idx]) + ' ' + str(sleepstage), fontsize = 30, fontweight = 'bold') 
            plt.yscale('log')
            plt.xlim(PlottingGRIN2B.lower_x_lim, PlottingGRIN2B.upper_x_lim)
            plt.xlabel(PlottingGRIN2B.x_ax_label, fontsize=20)
            plt.ylim(PlottingGRIN2B.lower_y_lim, PlottingGRIN2B.upper_y_lim)
            plt.ylabel(ylabel = PlottingGRIN2B.y_ax_label, fontsize=20)
            plt.xticks(fontsize=15)
            plt.yticks(fontsize = 15)
            os.chdir(save_path)
            plt.savefig(str(plot_labels[label_idx]) + '_' + str(sleepstage) + '.jpg', bbox_inches = 'tight')
            plt.show()
            plt.clf()
        

    def plot_genotype_average_by_channel(self, data, channel, region, sleepstage, save_path):
    
            sns.set_style("white") 
            fig, axs = plt.subplots(1,1, figsize=(20,15), sharex = True, sharey=True)
            genotype_palette = ['teal', 'black']
            hue_order = ['GRIN2B', 'WT']
            sns.lineplot(data=data, x='Frequency', y='Power', hue='Genotype', hue_order = hue_order, 
                     palette = genotype_palette, linewidth = 2)
            plt.suptitle(str(sleepstage) + ' Average ' + str(region) + ' (Channel ' + str(channel) + ')', fontsize = 30, fontweight = 'bold') 
            sns.despine()
            plt.yscale('log')
            axs.set_xlim(PlottingGRIN2B.lower_x_lim, PlottingGRIN2B.upper_x_lim)
            axs.set(xlabel = PlottingGRIN2B.x_ax_label)
            axs.set_ylim(PlottingGRIN2B.lower_y_lim, PlottingGRIN2B.upper_y_lim)
            axs.set(ylabel = PlottingGRIN2B.y_ax_label)
            for axis in ['bottom','left']:
                axs.spines[axis].set_linewidth(2)
            plt.rcParams.update({'font.size': 15})
            os.chdir(save_path)
            plt.savefig(str(channel) + '_' + str(sleepstage) + '.jpg')
            plt.show()
            plt.clf()