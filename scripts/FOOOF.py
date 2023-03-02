import os 
import pandas as pd 
import numpy as np
import fooof
from fooof import FOOOF
from fooof.core.io import save_fm, load_json
from fooof.core.reports import save_report_fm

from GRIN2B_constants import br_animal_IDs

#path to power results 
folder_path = 'home/melissa/RESULTS/GRIN2B/Power/REM/'
sleepstage = ''
results_path = ''
channel_nums = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]

fm = FOOOF()
frequency_range = [0.2,50]
frequency_values = np.arange(0.2, 48.2, 0.2)
fooof_df_overall = []

#load results folder
os.chdir(folder_path)
REM = pd.read_csv('baseline_REM_power.csv')

for animal in br_animal_IDs:
    anim_df = REM.loc[REM['Animal_ID'] == int(animal)]
    for channel in channel_nums:
        df = anim_df.loc[anim_df['Channel'] == channel]
        freq_of_int = df.loc[(0.1 <= df['Frequency']) & (df['Frequency'] < 48.2)]
        power_values = freq_of_int['Power'].to_numpy()
        fm.report(frequency_values, power_values, frequency_range)
        aperiodic_values = fm.aperiodic_params_
        fooof_dict = {'Animal_ID': [animal], 'Channel': [channel], 'Offset': [aperiodic_values[0]],
                      'Exponent': [aperiodic_values[1]]}
        fooof_df = pd.DataFrame(data = fooof_dict)
        fooof_df_overall.append(fooof_df)

overall_fooof = pd.concat(fooof_df_overall)
overall_fooof.to_csv(results_path + 'overall_fooof_' + str(sleepstage) + '.csv')
