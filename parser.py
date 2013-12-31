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
        self.dep, self.cont, self.stop = \
            self.pickle_handler.init_all_dicts()
        self.stop_multinomial_holder = MultinomialHolder()
        self.dep_multinomial_holder = MultinomialHolder()

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

            print "appending dep"
	    self.append_dicts(self.dep_multinomial_holder,
                              self.dep, "0")
            print "appending stop"
	    self.append_dicts(self.stop_multinomial_holder,
                              self.stop, "0")
            print "appending cont"
            self.append_dicts(self.stop_multinomial_holder,
                              self.cont, "1")

            self.stop_multinomial_holder = MultinomialHolder()
            self.dep_multinomial_holder = MultinomialHolder()

	pickle_hand = PickleHandler("tmp")
	pickle_hand.write_to_pickle(self.dep, self.cont, self.stop)
	pprint.pprint(sum_probs)

    def update_counts(self, marginals, edges):
        # state var indicates if head word is taking more children (1)
            # or stopped taking children (0)
        for edge in edges:
            head_word, mod_word, direct, adj, state = \
                                   str(edge.label).split()

            if state == "1" and mod_word != '---':
                self.stop_multinomial_holder.inc_counts(1, (head_word,
		   direct, adj), (head_word, direct, adj),
                                               marginals[edge.label])

                self.dep_multinomial_holder.inc_counts(0, (head_word,
		   mod_word, direct), (head_word, direct, adj),
                                               marginals[edge.label])

            if state == "0":
                self.stop_multinomial_holder.\
                    inc_counts(0, (head_word, direct, adj),
                      (head_word, direct, adj), marginals[edge.label])

    def update_parameters(self):
	self.dep_multinomial_holder.estimate()
        self.stop_multinomial_holder.estimate()
        self.dep = defaultdict(float)
        self.stop = defaultdict(float)
        self.cont = defaultdict(float)


    def append_dicts(self, multinomial_holder, hash_table, dict_name):
        for key, multinomial in \
                multinomial_holder.mult_list.iteritems():
    		for prob_key, value in eval("multinomial.prob[int("+ \
                              dict_name + ")]" + ".iteritems()"):
                    hash_table[prob_key] = value
		
    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

if __name__ == "__main__":
    parser = Parser("one_sent", "data/harmonic_values_all")
    parser.run_em()
