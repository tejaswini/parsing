from parsing_hypergraph import ParsingAlgo
from mult_holder import MultinomialHolder
import pprint
import cPickle as pickle
from pickle_handler import PickleHandler
from random_initializer import RandomInitializer
from evaluator import Evaluator
from collections import defaultdict
import math
from parallel_evaluator import ParallelEvaluator

class ParallelParser:

    def __init__(self, corpus_path, no_of_iterations, no_of_instances,
                 random_initializer, parallel_evaluator):
        self.dep_mult_holder_array = []
        self.stop_mult_holder_array = []
        self.no_of_iterations = no_of_iterations
        self.no_of_instances = no_of_instances
        self.random_initializer = random_initializer
        self.sentences = self.get_sentences(corpus_path)
        self.parallel_evaluator = parallel_evaluator
        self.likelihood = defaultdict(lambda : defaultdict((float)))

    def generate_multinomials(self):
        for i in range(self.no_of_instances):
            dep_mult_holder, stop_cont_mult_holder =\
                random_initializer.initialize_multinomials()
            self.dep_mult_holder_array.append(dep_mult_holder)
            self.stop_mult_holder_array.append(stop_cont_mult_holder)

    def run_em(self):
        for i in range(self.no_of_iterations):
            print "iteration is ", i
            for sentence in self.sentences:
                parsing_algo = ParsingAlgo(sentence,
                        self.dep_mult_holder_array[1].mult_list,
                        self.stop_mult_holder_array[1].mult_list)
                parsing_algo.get_hypergraph()

                for instance in range(self.no_of_instances):
                    marginals = parsing_algo.recompute_marginals(\
                       self.dep_mult_holder_array[instance].mult_list,
                       self.stop_mult_holder_array[instance].mult_list)
                    self.likelihood[i][instance] += math.log(\
                        parsing_algo.total_potentials)
                    edges = parsing_algo.hypergraph.edges
                    self.update_counts(marginals, edges, instance)
            if(i>0):
                for instance in range(self.no_of_instances):
                   assert self.likelihood[i][instance] >=\
                   self.likelihood[i-1][instance] ,"iteration is "\
                    + str(i) + " instance is " + instance

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

    def print_final_likelihood(self):
        final_likelihood = []
        for i in range(self.no_of_instances):
            final_likelihood.append(self.likelihood[self.no_of_iterations - 1][i])
        print "final likelihood is"
        pprint.pprint(final_likelihood)

    def evaluate_sent(self):
        parallel_evaluator.dep_mult_holder_array =\
            self.dep_mult_holder_array
        parallel_evaluator.stop_mult_holder_array =\
            self.stop_mult_holder_array
        parallel_evaluator.no_of_instances = self.no_of_instances
        parallel_evaluator.evaluate_sentences()
        print "undirected"
        pprint.pprint(parallel_evaluator.undirected_accuracy)
        print "directed"
        pprint.pprint(parallel_evaluator.directed_accuracy)

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

if __name__ == "__main__":
    pickle_handler = PickleHandler("data/dummy")
    dep_mult, stop_cont_mult = pickle_handler.init_all_dicts()
    random_initializer = RandomInitializer(dep_mult, stop_cont_mult)
    parallel_evaluator = ParallelEvaluator("data/sentences_train.txt",
          "data/dep_index_train.txt", [], [], 0)
    parser = ParallelParser("data/sentences_train.txt", 10, 60,
               random_initializer, parallel_evaluator)

    parser.generate_multinomials()
    parser.run_em()
    parser.evaluate_sent()
    parser.print_final_likelihood()
