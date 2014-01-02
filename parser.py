from parsing_hypergraph import ParsingAlgo
from mult_holder import MultinomialHolder
import pprint
from collections import defaultdict
import cPickle as pickle
from pickle_handler import PickleHandler

class Parser:

    def __init__(self, corpus_path, initial_values_path):
        self.sentences = self.get_sentences(corpus_path)
        self.initial_values_path = initial_values_path
        self.pickle_handler = PickleHandler(self.initial_values_path)
        dep_mult_list, stop_mult_list =\
            self.pickle_handler.init_all_dicts()
        self.stop_multinomial_holder = MultinomialHolder()
        self.stop_multinomial_holder.mult_list = stop_mult_list
        self.dep_multinomial_holder = MultinomialHolder()
        self.dep_multinomial_holder.mult_list = dep_mult_list


    def run_em(self):
        sum_probs = defaultdict(float)
        for i in range(10):
            print "iteration ", i
            for sentence in self.sentences:
                if(sentence.strip() == ""):
                    continue
                parsing_algo = ParsingAlgo(sentence,
			 self.dep_multinomial_holder.mult_list,
                               self.stop_multinomial_holder.mult_list)
                marginals = parsing_algo.get_marginals()
		sum_probs[i] += parsing_algo.total_potentials
                edges = parsing_algo.hypergraph.edges
                self.update_counts(marginals, edges)

            # assert sum_probs[i] > sum_probs[i-1], \
            #   "The prob are %r, %r"% (sum_probs[i],  sum_probs[i-1])

            self.update_parameters()

	pickle_hand = PickleHandler("tmp")
	pickle_hand.write_to_pickle(self.dep_multinomial_holder.\
           mult_list, self.stop_multinomial_holder.mult_list)
	pprint.pprint(sum_probs)

    def update_counts(self, marginals, edges):
        # state var indicates if head word is taking more children (1)
            # or stopped taking children (0)
        for edge in edges:
            arc = edge.label
            if arc.is_cont and arc.modifier_word != '---':
                self.stop_multinomial_holder.inc_counts(1,
                     (arc.head_word, arc.dir, arc.is_adj),
                                                 marginals[arc])
                self.dep_multinomial_holder.inc_counts(arc.\
                   modifier_word,(arc.head_word, arc.dir),
                                                 marginals[arc])

            if arc.is_cont == 0:
                self.stop_multinomial_holder.\
                    inc_counts(0, (arc.head_word, arc.dir, arc.is_adj),
                               marginals[arc])

    def update_parameters(self):
	self.dep_multinomial_holder.estimate()
        self.stop_multinomial_holder.estimate()

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences


if __name__ == "__main__":
    parser = Parser("one_sent", "data/harmonic_values_mult")
    parser.run_em()
