import pprint
from pickle_handler import PickleHandler
from parsing_hypergraph import ParsingAlgo

class Evaluator:

    def __init__(self, corpus_path, dep_path, dep_mult_holder,\
                     cont_stop_mult_holder):
        self.sentences = self.get_sentences(corpus_path)
        self.dep_index = self.get_sentences(dep_path)
        self.dep_mult_holder = dep_mult_holder
        self.cont_stop_mult_holder = cont_stop_mult_holder
        self.directed_depen = 0
        self.undirected_depen = 0
        self.total_deps = 0

    def evaluate_sentences(self):
        for i,sentence in enumerate(self.sentences):
            self.total_deps += len(sentence.split(" "))
            parsing_algo = ParsingAlgo(sentence.strip(), \
                      self.dep_mult_holder, self.cont_stop_mult_holder)
            depen = parsing_algo.best_edges()
            actual_dep = self.dep_index[i].strip()
            self.evaluate_accuracy(depen, actual_dep.split(" "), \
                                   sentence)
        print "correct depen is " + str(self.directed_depen)
        print "total depen is " + str(self.total_deps)
        print "accuracy is " + \
              str(float(self.directed_depen) / self.total_deps)

    def evaluate_accuracy(self, depen, actual_dep, sentence):
        for key, value in depen.iteritems():
            pos_tag, index = key[0], key[1]
            dep_tag, dep_index = value[0], value[1]
            if(int(actual_dep[index-1]) == int(dep_index)):
                self.directed_depen += 1

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

if __name__ == "__main__":
    pickle_handler = PickleHandler("data/final_100")
    dep_mult_holder, cont_stop_mult_holder =\
          pickle_handler.init_all_dicts()
    evaluator = Evaluator("data/sentences_train_100.txt",
        "data/dep_index_train_100.txt",dep_mult_holder,
                          cont_stop_mult_holder)
    evaluator.evaluate_sentences()
