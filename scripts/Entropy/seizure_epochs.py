'''This script is to extract seizure indices and look at epochs prior to seizures'''

import os 
import sys
import numpy as np 
import pandas as pd 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/GRIN2B/scripts')
from GRIN2B_constants import start_time_GRIN2B_baseline, end_time_GRIN2B_baseline, br_animal_IDs, GRIN_het_IDs

class SeizurePreparation():
    
    def __init__(self, animal_id, seizure_directory, normal_directory):
        self.animal_id = animal_id
        self.brain_1 = animal_id + '_BL1.pkl'
        self.brain_2 = animal_id + '_BL2.pkl'
        self.start_dict_1 = animal_id + '_1'
        self.start_dict_2 = animal_id + '_2'
        self.end_dict_1 = animal_id + '_1A'
        self.end_dict_2 = animal_id + '_2A'
        self.seizure_directory = seizure_directory
        self.normal_directory = normal_directory

    def time_values(self):
        os.chdir(self.seizure_directory)
        seiz_br_1 = pd.read_csv('GRIN2B_' + str(self.animal_id) + '_BL1_Seizures.csv')
        seiz_br_2 = pd.read_csv('GRIN2B_' + str(self.animal_id) + '_BL1_Seizures.csv')
        os.chdir(self.normal_directory)
        norm_br_1 = pd.read_pickle(str(self.animal_id) + '_BL1.pkl')
        norm_br_2 = pd.read_pickle(str(self.animal_id) + '_BL2.pkl')
        
        seiz_start_1 = [int(value) for value in seiz_br_1['sec_start'].tonumpy()]
        seiz_start_2 = [int(value) for value in seiz_br_2['sec_start'].tonumpy()]
        seiz_end_1 = [int(value) for value in seiz_br_1['sec_end'].tonumpy()]
        seiz_end_2 = [int(value) for value in seiz_br_2['sec_end'].tonumpy()]

        return seiz_start_1, seiz_start_2, seiz_end_1, seiz_end_2
    
    def round_to_multiple(self, number, multiple):
        return multiple*round(number/multiple)
    
    