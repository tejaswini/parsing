from parsing_hypergraph import ParsingAlgo
from multinomial_holder import MultinomialHolder
from cont_stop_mult_holder import ContStopMultHolder
from dep_mult_holder import DepMultinomialHolder
import pprint
from collections import defaultdict
import cPickle as pickle
from pickle_handler import PickleHandler

class Parser:

    def __init__(self, corpus_path, initial_values_path):
        self.sentences = self.get_sentences(corpus_path)
        self.initial_values_path = initial_values_path
        self.pickle_handler = PickleHandler(self.initial_values_path)
        self.dep, self.cont, self.stop = \
            self.pickle_handler.init_all_dicts()
 	self.cont_stop_multinomial_holder = ContStopMultHolder()
        self.dep_multinomial_holder = DepMultinomialHolder()

    def run_em(self):
        sum_probs = defaultdict(float)
        for i in range(10):
            print "iteration ", i
            for sentence in self.sentences:
                if(sentence.strip() == ""):
                    continue
                parsing_algo = ParsingAlgo(sentence,
			 self.dep, self.stop, self.cont)
                marginals = parsing_algo.get_marginals()
		sum_probs[i] += parsing_algo.total_potentials
                edges = parsing_algo.hypergraph.edges
                self.update_counts(marginals, edges)

            assert sum_probs[i] > sum_probs[i-1], \
                "The prob are %r, %r"% (sum_probs[i],  sum_probs[i-1])

            self.update_parameters()
            
	    self.append_dicts(self.dep,
		   self.dep_multinomial_holder.dep_mult_list, "prob")
	    self.append_dicts(self.stop,
		   self.cont_stop_multinomial_holder.\
                                 cont_stop_mult_list, "stop_prob")
            self.append_dicts(self.cont,
                   self.cont_stop_multinomial_holder.\
                                  cont_stop_mult_list, "cont_prob")

            self.cont_stop_multinomial_holder = ContStopMultHolder()
            self.dep_multinomial_holder = DepMultinomialHolder()

	pickle_hand = PickleHandler("tmp")
	pickle_hand.write_to_pickle(self.dep, self.cont, self.stop)
	pprint.pprint(sum_probs)

    def update_counts(self, marginals, edges):
        # state var indicates if head word is taking more children (1)
            # or stopped taking children (0)
        for edge in edges:
            head_word, mod_word, direct, adj, state =\
                                   str(edge.label).split()

            if state == "1" and mod_word != '---':
                self.dep_multinomial_holder.inc_counts((head_word,
		   mod_word, direct), (head_word, direct, adj),
                                               marginals[edge.label])
                self.cont_stop_multinomial_holder.\
                    inc_cont_counts((head_word, direct, adj),
                                      marginals[edge.label])

            if state == "1" and mod_word == '---':
                self.cont_stop_multinomial_holder.\
                    inc_cont_counts((head_word, direct, adj),
                                    marginals[edge.label])
		
            if state == "0":
                self.cont_stop_multinomial_holder.\
                    inc_stop_counts((head_word, direct, adj),
                                  marginals[edge.label])

    def update_parameters(self):
	self.dep_multinomial_holder.estimate()
        self.cont_stop_multinomial_holder.estimate()
        self.dep = defaultdict(float)
        self.stop = defaultdict(float)
        self.cont = defaultdict(float)


    def append_dicts(self, hash_table, mult_list, dict_name):
        for key, multinomial in mult_list.iteritems():
    		for prob_key, value in eval("multinomial."+ \
                              dict_name + ".iteritems()"):
                    hash_table[prob_key] = value
		
    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

if __name__ == "__main__":
    parser = Parser("one_sent", "data/harmonic_values_all")
    parser.run_em()
