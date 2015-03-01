import pprint
from pickle_handler import PickleHandler
from collections import defaultdict
import cPickle as pickle
from eisner_algo import EisnerAlgo
from constants import Constants

class Evaluator:

    def __init__(self, corpus_path, dep_path, prob_attach,\
                     prob_cont):
        self.sentences = self.get_sentences(corpus_path)
        self.dep_index = self.get_sentences(dep_path)
        self.prob_attach = prob_attach
        self.prob_cont = prob_cont
        self.directed_depen = 0
        self.undirected_depen = 0
        self.total_deps = 0
        self.incorrect_sent = []
        self.incorrect_dep = defaultdict(int)
        self.constants = Constants()
        self.prob = self.constants.compute_prob(self.prob_attach, self.prob_cont)

    def evaluate_sentences(self):
        for i,sentence in enumerate(self.sentences):
            actual_dep = self.dep_index[i].strip()
            if len(sentence.split()) != len(actual_dep.split()):
                   continue
            
            print "sentence is " + sentence
            sentence = "* " + sentence
            sent = sentence
            sentence = sentence.strip().split(" ")
            self.total_deps += len(sentence)
            eisner_algo = EisnerAlgo()
            eisner_algo.eisner_first_order(sentence)
            tag_indices = self.constants.indices_of_tag_dict(sentence)
            
            label_scores = self.constants.construct_label_scores(sentence,
                                                    tag_indices, self.prob)
            eisner_algo.compute_marginals(label_scores)
            depen = eisner_algo.best_edges(label_scores)
            self.evaluate_accuracy(depen, actual_dep.split(" "), \
                                   sent)

        print "correct depen is " + str(self.directed_depen)
        print "total depen is " + str(self.total_deps)
        print "directed accuracy is " + \
              str(float(self.directed_depen) / self.total_deps)
        print "undirected accuracy is " + \
              str(float(self.undirected_depen) / self.total_deps)

    def evaluate_accuracy(self, depen, actual_dep, sentence):
        print "actual dep is"
        pprint.pprint(actual_dep)
        print "depen is"
        pprint.pprint(depen)
        sent_acc = 0
        incorrect_dep_key = ("")
        words = sentence
        for index in range(1,len(depen)):
            if(int(actual_dep[index - 1]) == depen[index]):
                sent_acc += 1
                self.directed_depen += 1
                self.undirected_depen += 1
            else:
                if(int(actual_dep[depen[index] - 1]) == index):
                    self.undirected_depen += 1
                    sent_acc += 1
                else:
                  word = words[index-1]
                  # incorrect_dep = ("ROOT" if actual_dep[index] == 0\
                  #                      else words[index-1])
                  # correct_dep = ("ROOT" if int(actual_dep[index])\
                  #     == 0  else words[(int(actual_dep[index-1]) - 1)])
                  # incorrect_dep_key = (word,incorrect_dep, correct_dep)
      
        if(sent_acc <= 2 and len(actual_dep) >= 2):
            self.incorrect_sent.append(sentence)
            self.incorrect_dep[incorrect_dep_key] += 1

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

    def write_to_file(self, file_name, data):
        with open(file_name, "wb") as fp:
            fp.writelines(("%s\n" % line for line in data))

if __name__ == "__main__":
    pickle_handler = PickleHandler("data/numpy_final")
    prob_attach, prob_cont =  pickle_handler.init_all_dicts()

    evaluator = Evaluator("data/sentences_dev.txt",
       "data/dep_index_dev.txt", prob_attach, prob_cont)

    evaluator.evaluate_sentences()
    evaluator.write_to_file("incorrect_sent_rule",
                           evaluator.incorrect_sent)

    with open("incorrect_dep_dict_new", "wb") as fp:
        pickle.dump(evaluator.incorrect_dep, fp)
