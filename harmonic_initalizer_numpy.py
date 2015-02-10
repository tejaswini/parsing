from dep_initializer_numpy import DepCreator
from stop_cont_initializer_numpy import ContStopCreator
import numpy as np
from pickle_handler import PickleHandler

class HarmonicInitializer:
    def __init__(self,harmonic_file_name, root_val_file_name):
        self.harmonic_file_name = harmonic_file_name
        self.root_val_file_name = root_val_file_name
        self.dep_creator = DepCreator()
        self.stop_cont_creator = ContStopCreator()
        np.seterr(divide='ignore', invalid='ignore')

    def sentences(self):
        sentences = []
        with open(self.harmonic_file_name,"r") as fp:
            sentences += fp.readlines()
        with open(self.root_val_file_name,"r") as fp:
            sentences += fp.readlines()
        return sentences

    def initialize_harmonic_values(self):
        sentences = self.sentences()
        for sent in sentences:
            if "attach" in sent:
                self.dep_creator.add_entry(sent)
            if "continue" in sent:
                self.stop_cont_creator.add_entry(sent)
            if "stop" in sent:
                self.stop_cont_creator.add_entry(sent)
            if "root" in sent:
                self.dep_creator.add_entry(sent)

if __name__ == "__main__":
    initializer = HarmonicInitializer("data/harmonic", "data/root_val_file.txt")
    initializer.initialize_harmonic_values()
    pickle_handler = PickleHandler("data/harmonic_values_numpy")
    dep_mult_list = initializer.dep_creator.counts_attach
    stop_cont_mult_list = initializer.stop_cont_creator.counts_cont
    pickle_handler.write_to_pickle(dep_mult_list, stop_cont_mult_list, "data/harmonic_values_numpy")
