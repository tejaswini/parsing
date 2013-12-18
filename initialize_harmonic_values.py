import pprint
from dep_creator import DepCreator
from cont_creator import ContStopCreator
from root_creator import RootCreator
from pickle_handler import PickleHandler

class InitDict:
    def __init__(self,file_name):
        self.file_name = file_name
        self.dep_creator = DepCreator()
        self.cont_creator = ContStopCreator()
        self.stop_creator = ContStopCreator()
        self.root_creator = RootCreator()
        
    def sentences(self):
        sentences = []
        with open(self.file_name,"r") as fp:
            sentences = fp.readlines()
        return sentences

    def create_dict(self):
        sentences = self.sentences()
        for sent in sentences:
            if "attach" in sent:
                self.dep_creator.add_entry(sent)
            if "continue" in sent:
                self.cont_creator.add_entry(sent)
            if "stop" in sent:
                self.stop_creator.add_entry(sent)
            if "root" in sent:
                self.root_creator.add_entry(sent)
        # * needs Cont values
        self.cont_creator.prob["*", "left", "adj"] = 0.0001
        self.cont_creator.prob["*", "left", "non-adj"] = 0.0001
        self.cont_creator.prob["*", "right", "adj"] = 0.9999
        self.cont_creator.prob["*", "right", "non-adj"] = 0.0001
        self.stop_creator.prob["*", "left", "adj"] = 0.9999
        self.stop_creator.prob["*", "left", "adj"] = 0.9999
        self.stop_creator.prob["*", "right", "adj"] = 0.0001
        self.stop_creator.prob["*", "right", "non-adj"] = 0.9999
        

if __name__ == "__main__":
    initializer = InitDict("harmonic")
    initializer.create_dict()
    initializer.dep_creator.dep.update(initializer.root_creator.prob)
    pickle_handler = PickleHandler("data/harmonic_values")
    dep = initializer.dep_creator.dep
    stop = initializer.stop_creator.prob
    cont = initializer.cont_creator.prob
    pickle_handler.write_to_pickle(dep, cont, stop)


