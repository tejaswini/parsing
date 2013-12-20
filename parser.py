from parsing_hypergraph import ParsingAlgo
from multinomial_holder import MultinomialHolder
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
        # as we rewrite the probabilities each time, we use tmp instea\
        # of the original probabilities
 	self.dep_multinomial_holder = MultinomialHolder()
	self.stop_multinomial_holder = MultinomialHolder()

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
		sum_probs[i] +=  \
		    parsing_algo.total_potentials
                nodes = parsing_algo.hypergraph.nodes
                self.update_counts(marginals, nodes,
                                   ["*"] + sentence.split())

            self.update_parameters()
	    self.append_dicts(self.dep,
			    self.dep_multinomial_holder)
	    self.append_dicts(self.stop,
			  self.stop_multinomial_holder)
	pickle_hand = PickleHandler("tmp")
	pickle_hand.write_to_pickle(self.dep, self.cont, self.stop)
	pprint.pprint(sum_probs)

    def display_hash(hash_table):
        for key, value in hash_table.iteritems():
            print key,value
            

    def update_counts(self, marginals, nodes, words):
        for node in nodes:
            node_type, direct, span = str(node.label).split()
            span = span.split("-")
            values  = self.get_head_word(direct,span,
                                                    words)
            head_word, modifier = values[0], values[1]
            adj = self.is_adj(int(span[1]), int(span[0]))
            if(node_type == "trap"):
                self.dep_multinomial_holder.inc_counts((head_word,
		   modifier, direct), (head_word, direct), marginals[node.label])
		
            if(node_type == "triStop"):
                self.stop_multinomial_holder.inc_counts((head_word,
		   direct, adj), (head_word,direct, adj),
                                  marginals[node.label])

    def get_head_word(self, direct, span, words):
        return (words[int(span[1])], words[int(span[0])]) \
            if direct == "left" else \
            (words[int(span[0])], words[int(span[1])])

    def update_parameters(self):
	self.dep_multinomial_holder.estimate()
	self.stop_multinomial_holder.estimate()

    def append_dicts(self, hash_table, mult_holder):
        for key, multinomial in  \
	    mult_holder.mult_list.iteritems():
    		for prob_key, value in multinomial.prob.iteritems():
			hash_table[prob_key] = value
		
    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

    def is_adj(self, pos1, pos2):
        return "adj" if abs(pos2-pos1) == 1 else "non-adj"

if __name__ == "__main__":
    parser = Parser("data/corpus.txt", "data/harmonic_values")
    parser.run_em()
