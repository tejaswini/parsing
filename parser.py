from parsing_hypergraph import ParsingAlgo
import pprint
from collections import defaultdict
import cPickle as pickle
from pickle_handler import PickleHandler

class Parser:

    def __init__(self, corpus_path, initial_values_path):
        self.sentences = self.get_sentences(corpus_path)
        self.initial_values_path = initial_values_path
        self.dep_counts = defaultdict(float)
        self.stop_counts = defaultdict(float)
        self.pickle_handler = PickleHandler(initial_values_path)
        self.dep, self.cont, self.stop = \
            self.pickle_handler.init_all_dicts()

    def run_em(self):
        for i in range(100):
            self.dep_counts = defaultdict(float)
            self.stop_counts = defaultdict(float)
            for sentence in self.sentences:
                parsing_algo = ParsingAlgo(sentence,
                                           self.initial_values_path)
                marginals = parsing_algo.get_marginals()
                nodes = parsing_algo.hypergraph.nodes
                self.update_counts(marginals, nodes,
                                   ["*"] + sentence.split())

            self.update_parameters()
            self.pickle_handler.write_to_pickle(self.dep,self.cont,self.stop)
            

    def update_counts(self, marginals, nodes, words):
        for node in nodes:
            node_type, direct, span = node.label.split()
            span = span.split("-")
            values  = self.get_head_word(direct,span,
                                                    words)
            head_word,modifier = values[0],values[1]
            adj = self.is_adj(int(span[1]), int(span[0]))
            if(node_type == "trap"):
                self.dep_counts[head_word, modifier, direct, adj] \
                    += marginals[node].value
            if(node_type == "triStop"):
                self.stop_counts[head_word, direct, adj] +=  \
                    marginals[node].value

    def get_head_word(self, direct, span, words):
        return (words[int(span[1])], words[int(span[0])]) \
            if direct=="left" else \
            (words[int(span[0])], words[int(span[1])])
                
    def update_parameters(self):
        for key in self.dep_counts.keys():
            values_trap = self.get_values_with_filter(key)
            total_trap = sum(values_trap)
            if(total_trap == 0):
                continue

            self.dep[key] = self.dep_counts[key] / total_trap
            stop_key = (key[0], key[2], key[3])
            self.stop[stop_key] = \
                self.stop_counts[stop_key] / total_trap
                
            self.cont[stop_key] = 1 - self.stop[stop_key]

    def get_values_with_filter(self, key):
        return map(self.dep_counts.get, filter(lambda k: k[0] == key[0] 
                   and key[2] == k[2] and k[3] == key[3], 
                                            self.dep_counts.keys()))

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

    def is_adj(self, pos1, pos2):
        return "adj" if abs(pos2-pos1) == 1 else "non-adj"

if __name__ == "__main__":
    parser = Parser("data/corpus.txt", "data/initial_values")
    parser.run_em()
    print "stop probalities are"
    pprint.pprint(parser.stop)
    print "dep probalities are"
    pprint.pprint(parser.dep)
    
    
