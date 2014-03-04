import pprint
from dep_creator import DepCreator
from cont_creator import ContStopCreator
from root_creator import RootCreator
from pickle_handler import PickleHandler

class InitDict:
    def __init__(self,harmonic_file_name, root_val_file_name):
        self.harmonic_file_name = harmonic_file_name
        self.root_val_file_name = root_val_file_name
        self.dep_creator = DepCreator()
        self.stop_cont_creator = ContStopCreator()
        
    def sentences(self):
        sentences = []
        with open(self.harmonic_file_name,"r") as fp:
            sentences += fp.readlines()
        with open(self.root_val_file_name,"r") as fp:
            sentences += fp.readlines()
        return sentences

    def create_dict(self):
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

        self.dep_creator.mult_holder.estimate()
        self.stop_cont_creator.mult_holder.estimate()

if __name__ == "__main__":
    initializer = InitDict("data/harmonic", "data/root_val_file.txt")
    initializer.create_dict()
    pickle_handler = PickleHandler("data/harmonic_values_mult")
    dep_mult_list = initializer.dep_creator.mult_holder.mult_list
    stop_cont_mult_list = initializer.stop_cont_creator.\
            mult_holder.mult_list
    pickle_handler.write_to_pickle(dep_mult_list, stop_cont_mult_list)


