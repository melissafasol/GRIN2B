import sys 

sys.path.insert(0, '/home/melissa/PROJECT_DIRECTORIES/taini_main/scripts')
from preproc1_preparefiles import PrepareFiles, LoadFromStart

sample_rate = 250.4


def br_seizure_files(br_file, sample_rate):
    '''function to reformat seizure brain states'''
    seizure_times_start = br_file.iloc[:, 0:1].to_numpy().astype(int)
    seizure_times_end = br_file.iloc[:, 1:2].to_numpy().astype(int)
    seizure_times_start_epochs = [epoch for sublist in seizure_times_start for epoch in sublist]
    seizure_times_end_epochs = [epoch for sublist in seizure_times_end for epoch in sublist]
    seizure_start_sample_rate = [int(element*sample_rate) for element in seizure_times_start_epochs]
    seizure_end_sample_rate = [int(element*sample_rate) for element in seizure_times_end_epochs]
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
    

def one_second_timebins(zipped_timevalues,  epoch_length):

    function_timebins = lambda epoch_start, epoch_end: list(range(epoch_start, epoch_end, epoch_length))
    
    new_epoch_times = [list(map(lambda epoch: function_timebins(int(epoch[0]), int(epoch[1])), (zipped_timevalues)))]

    new_time_array = [time_start for epoch in new_epoch_times for time_start in epoch]
    one_second_timebins = [time_start for epoch in new_time_array for time_start in epoch]
    return one_second_timebins


def removing_seizure_epochs(seizure_br_file, wake_br_file):
    
    def round_to_multiple(number, multiple):
        return multiple*round(number/multiple)
    
    wake_states = wake_br_file[wake_br_file['brainstate'] == 0]
    start_times = wake_states.iloc[:,1:2].to_numpy()
    wake_start = [int(epoch) for sublist in start_times for epoch in sublist]
    
    seizure_times_start = seizure_br_file.iloc[:, 0:1].to_numpy().astype(int)
    seizure_times_start_epochs = [epoch for sublist in seizure_times_start for epoch in sublist]
    testing_multiples = [round_to_multiple(i, 5) for i in seizure_times_start_epochs] 
    
    matching_epochs = []
    for seizure_epoch in testing_multiples:
        if seizure_epoch in wake_start:
            matching_epochs.append(seizure_epoch)
            
    return matching_epochs