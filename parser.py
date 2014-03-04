from parsing_hypergraph import ParsingAlgo
from mult_holder import MultinomialHolder
import pprint
from collections import defaultdict
import cPickle as pickle
from pickle_handler import PickleHandler
import math

class Parser:

    def __init__(self, corpus_path, initial_values_path,
                 final_value_path,debug_mode):
        self.sentences = self.get_sentences(corpus_path)
        self.debug_mode = debug_mode
        self.final_value_path = final_value_path
        self.pickle_handler = PickleHandler(initial_values_path)
        dep_mult_list, stop_mult_list =\
            self.pickle_handler.init_all_dicts()
        self.stop_multinomial_holder = MultinomialHolder()
        self.stop_multinomial_holder.mult_list = stop_mult_list
        self.dep_multinomial_holder = MultinomialHolder()
        self.dep_multinomial_holder.mult_list = dep_mult_list

    def run_em(self):
        sum_probs = defaultdict(lambda: 1.0)
        for i in range(10):
            print "iteration ", i
            for sentence in self.sentences:
                if(sentence.strip() == ""):
                    continue
                parsing_algo = ParsingAlgo(sentence,
			 self.dep_multinomial_holder.mult_list,
                               self.stop_multinomial_holder.mult_list)
                marginals = parsing_algo.get_marginals()
		sum_probs[i] += math.log(parsing_algo.total_potentials)
                edges = parsing_algo.hypergraph.edges
                self.update_counts(marginals, edges)

            if(sum_probs[i-1]!=1.0):
                assert sum_probs[i] > sum_probs[i-1], \
                 "The prob are %r, %r"% (sum_probs[i],  sum_probs[i-1])

            self.update_parameters()
            self.validate_multinomials(self.dep_multinomial_holder)
            self.validate_multinomials(self.stop_multinomial_holder)

	pickle_hand = PickleHandler(self.final_value_path)
	pickle_hand.write_to_pickle(self.dep_multinomial_holder.\
           mult_list, self.stop_multinomial_holder.mult_list)
	pprint.pprint(sum_probs)
    

    def update_counts(self, marginals, edges):
        for edge in edges:
            arc = edge.label
            if arc.is_cont and arc.modifier_word != "":
                self.stop_multinomial_holder.inc_counts(arc.is_cont,
                     (arc.head_word, arc.dir, arc.is_adj),
                                                 marginals[edge.id])
                self.dep_multinomial_holder.inc_counts(arc.\
                   modifier_word,(arc.head_word, arc.dir),
                                                 marginals[edge.id])

            if not arc.is_cont:
                self.stop_multinomial_holder.\
                 inc_counts(arc.is_cont,
                 (arc.head_word, arc.dir, arc.is_adj),
                            marginals[edge.id])

    def update_parameters(self):
	self.dep_multinomial_holder.estimate()
        self.stop_multinomial_holder.estimate()

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

    def validate_multinomials(self, multinomial_holder):
        for key, mult in multinomial_holder.mult_list.iteritems():
            if(self.debug_mode):
                print key
                pprint.pprint(mult.prob)

            total = sum(mult.prob.values())
            assert round(total, 1) == 1.0 or round(total, 1) == 0 ,\
               "The mult for " + str(key) + " is not totalling to 1 "\
               + str(total)

if __name__ == "__main__":
    parser = Parser("data/sentences_train.txt",
                    "data/harmonic_values_mult", "data/harmonic_final",
                    False)
    parser.run_em()
