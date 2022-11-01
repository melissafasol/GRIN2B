import sys 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts')
from preproc1_preparefiles import PrepareFiles, LoadFromStart


def br_seizure_files(br_file):
    '''function to reformat seizure brain states'''
    seizure_times_start = br_file.iloc[:, :1].to_numpy().astype(int)
    seizure_times_end = br_file.iloc[:, :1:2].to_numpy().astype(int)
    seizure_times_start_epochs = [epoch for sublist in seizure_times_start for epoch in sublist]
    seizure_times_end_epochs = [epoch for sublist in seizure_times_end for epoch in sublist]
    seizure_start_sample_rate = [int(element*250.4) for element in seizure_times_start_epochs]
    seizure_end_sample_rate = [int(element*250.4) for element in seizure_times_end_epochs]
    zipped_timevalues = list(zip(seizure_start_sample_rate , seizure_end_sample_rate)) 
    
    return zipped_timevalues  


class PrepareGRIN2B(PrepareFiles):
    
    def __init__(self, directory_path, animal_id):
        self.directory_path = directory_path
        self.animal_id = animal_id
        self.brain_1 = animal_id + '_BL1.pkl'
        self.brain_2 = animal_id + '_BL2.pkl'
        self.start_dict_1 = animal_id + '_1'
        self.start_dict_2 = animal_id + '_2'
        self.end_dict_1 = animal_id + '_1A'
        self.end_dict_2 = animal_id + '_2A'

    
    def get_end_times(self, end_times_GRIN2B_dict):
        end_time_1 = end_times_GRIN2B_dict[self.end_dict_1]
        end_time_2 = end_times_GRIN2B_dict[self.end_dict_2]
        return (end_time_1, end_time_2)

class LoadGRIN2B(LoadFromStart):

    def __init__(self, recording, start_time_1, start_time_2, end_time_1, end_time_2, channelnumber):
        self.recording = recording
        self.start_time_1 = start_time_1
        self.start_time_2 = start_time_2
        self.channelnumber = channelnumber
        self.end_time_1 = end_time_1
        self.end_time_2 = end_time_2
        
    def load_GRIN2B_from_start(self):
        data_1 = self.recording[self.channelnumber, self.start_time_1: self.end_time_1]
        data_2 = self.recording[self.channelnumber, self.start_time_2: self.end_time_2]
        return (data_1, data_2)
    
    