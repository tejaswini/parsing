from collections import defaultdict
from parsing_hypergraph import ParsingAlgo
import pprint
from pickle_handler import PickleHandler
from mult_holder import MultinomialHolder

class ParallelEvaluator:

    def __init__(self, corpus_path, dep_path, dep_mult_holder_array,
                 stop_mult_holder_array, no_of_instances):
        self.sentences = self.get_sentences(corpus_path)
        self.dep_index = self.get_sentences(dep_path)
        self.dep_mult_holder_array = dep_mult_holder_array
        self.stop_mult_holder_array = stop_mult_holder_array
        self.undirected_depen = defaultdict(int)
        self.directed_depen = defaultdict(int)
        self.directed_accuracy = []
        self.undirected_accuracy = []
        self.no_of_instances = no_of_instances
        self.total_deps = 0

    def reinitialize(self, dep_mult_holder_array,
                     stop_mult_holder_array, no_of_instances):
        self.directed_accuracy = []
        self.undirected_accuracy = []
        self.stop_mult_holder_array = stop_mult_holder_array
        self.dep_mult_holder_array = dep_mult_holder_array
        self.no_of_instances = no_of_instances
        

    def evaluate_sentences(self):
        for i, sentence in enumerate(self.sentences):
            actual_dep = self.dep_index[i].strip()
            actual_dep = actual_dep.split(" ")
            if len(sentence.split()) != len(actual_dep):
                   continue
            self.total_deps += len(sentence.split(" "))
            parsing_algo = ParsingAlgo(sentence.strip(), \
              self.dep_mult_holder_array[0].mult_list,
                            self.stop_mult_holder_array[0].mult_list)
            for instance in range(self.no_of_instances):
                parsing_algo.recompute_marginals(\
                    self.dep_mult_holder_array[instance].mult_list,
                    self.stop_mult_holder_array[instance].mult_list)
                depen = parsing_algo.best_edges()
                self.evaluate_accuracy(depen, actual_dep,
                                       sentence, instance)
        for instance in range(self.no_of_instances):
            self.directed_accuracy.append(\
                float(self.directed_depen[instance]) / self.total_deps)
            self.undirected_accuracy.append(\
                float(self.undirected_depen[instance]) /\
                    self.total_deps)

    def evaluate_accuracy(self, depen, actual_dep, sentence, inst_num):
        sent_acc = 0
        incorrect_dep_key = ("")
        words = sentence.split()
        for key, value in depen.iteritems():
            pos_tag, index = key[0], key[1]
            dep_tag, dep_index = value[0], value[1]
            if(int(actual_dep[index-1]) == dep_index):
                self.directed_depen[inst_num] += 1
                self.undirected_depen[inst_num] += 1
            else:
              if(dep_index!=0 \
                     and int(actual_dep[dep_index-1]) == index):
                self.undirected_depen[inst_num] += 1

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

if __name__ == "__main__":
        pickle_handler = PickleHandler("data/dummy_final")
        dep_mult, stop_cont_mult = pickle_handler.init_all_dicts()
        dep_mult_array = []
        stop_mult_array = []
        mult_holder = MultinomialHolder()
        mult_holder.mult_list = dep_mult
        dep_mult_array.append(mult_holder)
        mult_holder = MultinomialHolder()
        mult_holder.mult_list = stop_cont_mult
        stop_mult_array.append(mult_holder)

        pickle_handler = PickleHandler("data/random_final")
        dep_mult, stop_cont_mult = pickle_handler.init_all_dicts()
        mult_holder = MultinomialHolder()
        mult_holder.mult_list = dep_mult
        dep_mult_array.append(mult_holder)
        mult_holder = MultinomialHolder()
        mult_holder.mult_list = stop_cont_mult
        stop_mult_array.append(mult_holder)
        
        parallel_evaluator = ParallelEvaluator("data/sentences_dev.txt",  "data/dep_index_dev.txt", dep_mult_array, stop_mult_array, 2)

        parallel_evaluator.evaluate_sentences()
        pprint.pprint(parallel_evaluator.undirected_accuracy)
        pprint.pprint(parallel_evaluator.directed_accuracy)
