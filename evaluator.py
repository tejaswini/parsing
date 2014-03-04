import pprint
from pickle_handler import PickleHandler
from parsing_hypergraph import ParsingAlgo
from collections import defaultdict
import cPickle as pickle

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
        self.incorrect_sent = []
        self.incorrect_dep = defaultdict(int)

    def evaluate_sentences(self):
        for i,sentence in enumerate(self.sentences):
            actual_dep = self.dep_index[i].strip()
            if len(sentence.split()) != len(actual_dep.split()):
                   continue

            self.total_deps += len(sentence.split(" "))
            parsing_algo = ParsingAlgo(sentence.strip(), \
                      self.dep_mult_holder, self.cont_stop_mult_holder)
            depen = parsing_algo.best_edges()
            self.evaluate_accuracy(depen, actual_dep.split(" "), \
                                   sentence)
        print "correct depen is " + str(self.directed_depen)
        print "total depen is " + str(self.total_deps)
        print "directed accuracy is " + \
              str(float(self.directed_depen) / self.total_deps)
        print "undirected accuracy is " + \
              str(float(self.undirected_depen) / self.total_deps)

    def evaluate_accuracy(self, depen, actual_dep, sentence):
        sent_acc = 0
        incorrect_dep_key = ("")
        words = sentence.split()
        for key, value in depen.iteritems():
            pos_tag, index = key[0], key[1]
            dep_tag, dep_index = value[0], value[1]
            if(int(actual_dep[index-1]) == dep_index):
                sent_acc += 1
                self.directed_depen += 1
                self.undirected_depen += 1
            else:
              if(dep_index!=0 \
                     and int(actual_dep[dep_index-1]) == index):
                self.undirected_depen += 1
                sent_acc += 1
              else:
                  word = words[index-1]
                  incorrect_dep = ("ROOT" if dep_index == 0\
                                       else words[dep_index-1])
                  correct_dep = ("ROOT" if int(actual_dep[index-1])\
                      == 0  else words[(int(actual_dep[index-1]) - 1)])
                  incorrect_dep_key = (word,incorrect_dep, correct_dep)
      
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
    pickle_handler = PickleHandler("data/harmonic_final")
    dep_mult_holder, cont_stop_mult_holder =\
          pickle_handler.init_all_dicts()
    evaluator = Evaluator("data/sentences_train.txt",
       "data/dep_index_train.txt", dep_mult_holder,
                          cont_stop_mult_holder)

    evaluator.evaluate_sentences()
    evaluator.write_to_file("incorrect_sent_rule",
                           evaluator.incorrect_sent)

    with open("incorrect_dep_dict_new", "wb") as fp:
        pickle.dump(evaluator.incorrect_dep, fp)
