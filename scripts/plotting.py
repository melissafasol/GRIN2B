import os 
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from GRIN2B_constants import channel_dict


class PlottingGRIN2B():
    
    lower_x_lim = 1
    upper_x_lim = 48
    x_ax_label = 'Frequency (Hz)'
    lower_y_lim = 10**-3
    upper_y_lim = 10**3
    y_ax_label = 'Power [V**2/Hz]'
    
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
        

    def plot_genotype_average_by_channel(self, data_to_plot, channel, sleepstage, save_directory):
    
            sns.set_style("white") 
            fig, axs = plt.subplots(1,1, figsize=(20,15), sharex = True, sharey=True)
            genotype_palette = ['teal', 'black']
            hue_order = ['GRIN2B', 'WT']
            sns.lineplot(data= data_to_plot, x='Frequency_2', y='Power',hue = 'Genotype', errorbar = ("se"),
            hue_order = hue_order, linewidth = 2, palette = genotype_palette)
            axs.set_yscale('log')
            tick_values = list(range(0, 54, 6))
            label_list = ['0', '6', '12', '18', '24', '30', '36', '42', '48']
            axs.set_xticks(ticks = tick_values, labels = label_list)
            
            #include an overall plot title 
            plt.suptitle('Channel ' + str(channel) + ' ' + str(sleepstage), y = 0.92, fontsize = 30) 
            sns.despine()
            sns.despine()
            axs.set_xlim(1, 49)
            axs.set_ylim(10**-1, 10**3)
            axs.set_xlabel("Frequency (Hz)", fontsize = 20)
            axs.set_ylabel("Power [V**2/Hz]", fontsize = 20)

            #customise the legend
            leg = plt.legend( loc = 'upper right', frameon = False)
            leg.set_title('Genotype',prop={'size':25})
            leg_lines = leg.get_lines()
            leg_texts = leg.get_texts()
            plt.setp(leg_lines[0], linewidth=6)
            plt.setp(leg_lines[1], linewidth=6)
            plt.setp(leg_texts, fontsize=20)

            #increase width of the x and y axis 
            for axis in ['bottom','left']:
                axs.spines[axis].set_linewidth(2)

            #update the fontsize of all characters on x and y axis
            plt.rcParams.update({'font.size': 20})

            #save figure 
            os.chdir(save_directory)
            plt.savefig('chan_' + str(channel) + '_' + str(sleepstage) + '.jpg')
            plt.savefig('chan_' + str(channel) + '_' + str(sleepstage) + '.svg')

    def genotype_sex_subplots(self, female_data, male_data, sleepstage, save_path) :
        sns.set_style("white") 
        fig, axs = plt.subplots(1,2, figsize=(20,10), sharex = True, sharey=True)
        genotype_palette = ['teal', 'black']
        hue_order_1 = ['Female GRIN2B Het', 'Female Wildtype']
        hue_order_2 = ['Male GRIN2B Het', 'Male Wildtype']


        sns.lineplot(data= female_data, x='Frequency_2', y='Power',hue = 'Gender', errorbar = ("se"),
                     hue_order = hue_order_1, linewidth = 2, palette = genotype_palette, ax = axs[0])
        sns.despine()

        #customise the legend for plot one 
        leg = axs[0].legend( loc = 'upper right', frameon = False)
        leg.set_title('Sex',prop={'size':25})
        leg_lines = leg.get_lines()
        leg_texts = leg.get_texts()
        plt.setp(leg_lines[0], linewidth=6)
        plt.setp(leg_lines[1], linewidth=6)
        plt.setp(leg_texts, fontsize=20)


        sns.lineplot(data = male_data, x='Frequency_2', y='Power', hue = 'Gender', errorbar = ('ci', 95),
                     hue_order = hue_order_2, linewidth = 2, palette = genotype_palette, ax = axs[1])
        tick_values = list(range(0, 54, 6))
        label_list = ['0', '6', '12', '18', '24', '30', '36', '42', '48']
        axs[1].set_xticks(ticks = tick_values, labels = label_list)
        sns.despine()


        #customise the legend for plot two 
        leg = axs[1].legend( loc = 'upper right', frameon = False)
        leg.set_title('Sex',prop={'size':25})
        leg_lines = leg.get_lines()
        leg_texts = leg.get_texts()
        plt.setp(leg_lines[0], linewidth=6)
        plt.setp(leg_lines[1], linewidth=6)
        plt.setp(leg_texts, fontsize=20)

        #specify axes details 
        axs[0].set_yscale('log')
        axs[1].set_yscale('log')
        axs[0].set_xlim(1, 48)
        axs[0].set_ylim(10**-1, 10**3)
        axs[1].set_xlim(1, 48)
        axs[1].set_ylim(10**-1, 10**3)
        axs[0].set_xlabel("Frequency (Hz)", fontsize = 20)
        axs[1].set_xlabel("Frequency (Hz)", fontsize = 20)
        axs[0].set_ylabel("Power [V**2/Hz]", fontsize = 20)

        #include an overall plot title 
        fig.suptitle('Overall Average ' + str(sleepstage), y = 0.96, fontsize = 30) 


        #increase width of the x and y axis 
        for axis in ['bottom','left']:
            axs[0].spines[axis].set_linewidth(2)
            axs[1].spines[axis].set_linewidth(2)

        #update the fontsize of all characters on x and y axis
        plt.rcParams.update({'font.size': 20})

        #save figure 
        os.chdir(save_path)
        plt.savefig('overall_average_' + str(sleepstage) + '_sex_subplots.jpg')
        plt.savefig('overall_average_' + str(sleepstage) + '_sex_subplots.svg')

    
    def bar_and_strip_plots(self, delta, theta, sigma, beta, gamma, sleepstage, save_directory):
        f, ax = plt.subplots(1,5, figsize=(10,10), sharey = True)
        sns.set_style("white")
        hue_order_palette = ['WT', 'GRIN2B']
        palette_stats = ['black', 'teal']
        pointplot_palette = ['white', 'white']
        sns.barplot(x= 'Frequency', y='Power', hue='Genotype',errorbar = ("se"), data = delta, width = 1.0,
                    hue_order = hue_order_palette, palette = palette_stats, ax = ax[0])
        sns.stripplot(x = 'Frequency', y = 'Power', hue = 'Genotype', data = delta, hue_order = hue_order_palette,
                      palette = pointplot_palette, edgecolor = 'k', sizes = (50, 50), dodge = True, linewidth = 1, ax = ax[0])
        ax[0].legend([],[], frameon=False)
        ax[0].set_yscale('log')
        ax[0].set(xlabel=None)
        ax[0].set(xticklabels=['Delta'])
        ax[0].set(ylabel = 'Power [V**2/Hz]')
        sns.barplot(x= 'Frequency', y='Power', hue='Genotype', errorbar = ("se"), data = theta, width = 1.0,
                    hue_order = hue_order_palette, palette = palette_stats, ax = ax[1])
        sns.stripplot(x = 'Frequency', y = 'Power', hue = 'Genotype', data = theta, hue_order = hue_order_palette,
                      palette = pointplot_palette, edgecolor = 'k', sizes = (50, 50), dodge = True, linewidth = 1, ax = ax[1])
        ax[1].legend([],[], frameon=False)
        ax[1].set_yscale('log')
        ax[1].set(xlabel=None)
        ax[1].set(xticklabels=['Theta'])
        ax[1].set(ylabel=None)
        sns.barplot(x= 'Frequency', y='Power', hue='Genotype', errorbar = ("se"), data = sigma, width = 1.0,
                    hue_order = hue_order_palette, palette = palette_stats, ax = ax[2])
        sns.stripplot(x = 'Frequency', y = 'Power', hue = 'Genotype', data = sigma, hue_order = hue_order_palette,
                      palette = pointplot_palette, edgecolor = 'k', sizes = (50, 50), dodge = True, linewidth = 1, ax = ax[2])
        ax[2].legend([],[], frameon=False)
        ax[2].set_yscale('log')
        ax[2].set(ylabel=None)
        ax[2].set(xlabel= 'Channel 2')
        ax[2].set(xticklabels=['Sigma'])
        sns.barplot(x= 'Frequency', y='Power', hue='Genotype', errorbar = ("se"), data = beta, width = 1.0,
                    hue_order = hue_order_palette, palette = palette_stats, ax = ax[3])
        sns.stripplot(x = 'Frequency', y = 'Power', hue = 'Genotype', data = beta, hue_order = hue_order_palette,
                      palette = pointplot_palette, edgecolor = 'k', sizes = (50, 50), dodge = True, linewidth = 1, ax = ax[3])
        ax[3].legend([],[], frameon=False)
        ax[3].set_yscale('log')
        ax[3].set(xlabel=None)
        ax[3].set(xticklabels=['Beta'])
        ax[3].set(ylabel=None)
        sns.barplot(x= 'Frequency', y='Power', hue='Genotype', errorbar = ("se"), data = gamma, width = 1.0,
                            hue_order = hue_order_palette, palette = palette_stats, ax = ax[4])
        sns.stripplot(x = 'Frequency', y = 'Power', hue = 'Genotype', data = gamma, hue_order = hue_order_palette,
                      palette = pointplot_palette, edgecolor = 'k', sizes = (50, 50), dodge = True, linewidth = 1, ax = ax[4])
        ax[4].legend([], [], frameon = False)
        ax[4].set_yscale('log')
        ax[4].set(xlabel=None)
        ax[4].set(xticklabels=['Gamma'])
        ax[4].set(ylabel=None)


        #sns.despine()
        plt.yscale('log')
        plt.ylim(10**-1, 10**3)
        plt.suptitle('Channel 2 ' + str(sleepstage), fontsize = 30, fontweight = 'bold')

        ax[0].spines['top'].set_visible(False)
        ax[0].spines['right'].set_visible(False)
        ax[0].spines['bottom'].set_visible(False)
        ax[0].spines['left'].set_visible(False)
        ax[1].spines['top'].set_visible(False)
        ax[1].spines['right'].set_visible(False)
        ax[1].spines['bottom'].set_visible(False)
        ax[1].spines['left'].set_visible(False)
        ax[2].spines['top'].set_visible(False)
        ax[2].spines['right'].set_visible(False)
        ax[2].spines['bottom'].set_visible(False)
        ax[2].spines['left'].set_visible(False)
        ax[3].spines['top'].set_visible(False)
        ax[3].spines['right'].set_visible(False)
        ax[3].spines['bottom'].set_visible(False)
        ax[3].spines['left'].set_visible(False)
        ax[4].spines['top'].set_visible(False)
        ax[4].spines['right'].set_visible(False)
        ax[4].spines['bottom'].set_visible(False)
        ax[4].spines['left'].set_visible(False)
        plt.rcParams.update({'font.size': 20})
        plt.rcParams["font.weight"] = "bold"


        #Legend
        custom_lines = [Line2D([0], [0], color = 'black', lw = 6),
                        Line2D([0], [0], color = 'teal', lw = 6)]
        labels = ['WT', 'GRIN2B']
        ax[4].legend(custom_lines, labels, frameon = False)

        os.chdir(save_directory)
        plt.savefig(str(sleepstage) + '_channel_2_bar_point_plot.jpg')
        plt.savefig(str(sleepstage) + '_channel_2_bar_point_plot.svg')
        plt.show()
