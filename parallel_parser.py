from parsing_hypergraph import ParsingAlgo
from mult_holder import MultinomialHolder
import pprint
import cPickle as pickle
from pickle_handler import PickleHandler
from random_initializer import RandomInitializer
from evaluator import Evaluator

class ParallelParser:

    def __init__(self, corpus_path, no_of_instances,
                 random_initializer, eval_corpus, gold_dep):
        self.dep_mult_holder_array = []
        self.stop_mult_holder_array = []
        self.no_of_instances = no_of_instances
        self.random_initializer = random_initializer
        self.sentences = self.get_sentences(corpus_path)
        self.eval_corpus = eval_corpus
        self.gold_dep = gold_dep
        self.log_likelihood = []

    def generate_multinomials(self):
        for i in range(self.no_of_instances):
            dep_mult_holder, stop_cont_mult_holder =\
                random_initializer.initialize_multinomials()
            self.dep_mult_holder_array.append(dep_mult_holder)
            self.stop_mult_holder_array.append(stop_cont_mult_holder)

    def run_em(self):
        for i in range(10):
            print "iteration is ", i
            for sentence in self.sentences:
                parsing_algo = ParsingAlgo(sentence,
                        self.dep_mult_holder_array[0].mult_list,
                        self.stop_mult_holder_array[0].mult_list)

                for instance in range(self.no_of_instances):
                    marginals = parsing_algo.recompute_marginals(\
                       self.dep_mult_holder_array[instance].mult_list,
                       self.stop_mult_holder_array[instance].mult_list)
                    edges = parsing_algo.hypergraph.edges
                    self.update_counts(marginals, edges, instance)
            self.update_parameters()

    def update_counts(self, marginals, edges, instance_number):
        for edge in edges:
            arc = edge.label
            if arc.is_cont and arc.modifier_word != "":
                self.stop_mult_holder_array[instance_number].\
                    inc_counts(arc.is_cont,
                     (arc.head_word, arc.dir, arc.is_adj),
                                                 marginals[edge.id])
                self.dep_mult_holder_array[instance_number].\
                    inc_counts(arc.\
                   modifier_word,(arc.head_word, arc.dir),
                                                 marginals[edge.id])

            if not arc.is_cont:
                self.stop_mult_holder_array[instance_number].\
                 inc_counts(arc.is_cont,
                 (arc.head_word, arc.dir, arc.is_adj),
                            marginals[edge.id])

    def update_parameters(self):
        for instance in range(self.no_of_instances):
            self.dep_mult_holder_array[instance].estimate()
            self.stop_mult_holder_array[instance].estimate()

    def evaluate_sent(self):
        for instance in range(self.no_of_instances):
            evaluator = Evaluator(self.eval_corpus, self.gold_dep,
            self.dep_mult_holder_array[instance].mult_list,
            self.stop_mult_holder_array[instance].mult_list)
            evaluator.evaluate_sentences()

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

if __name__ == "__main__":
    pickle_handler = PickleHandler("data/dummy")
    dep_mult, stop_cont_mult = pickle_handler.init_all_dicts()
    random_initializer = RandomInitializer(dep_mult, stop_cont_mult)
    parser = ParallelParser("data/sentences_train.txt", 5,
       random_initializer, "data/sentences_train.txt",
       "data/dep_index_train.txt")
    parser.generate_multinomials()
    parser.run_em()
    parser.evaluate_sent()
