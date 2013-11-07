from parsing_hypergraph import ParsingAlgo
import pprint
from collections import defaultdict
import cPickle as pickle

class Parser:

    def __init__(self, corpus_path, initial_values_path):
        self.sentences = self.get_sentences(corpus_path)
        self.initial_values_path = initial_values_path
        self.cont_counts = defaultdict(float)
        self.dep_counts = defaultdict(float)
        self.dep, self.cont, self.stop = \
            self.init_all_dicts(initial_values_path)
        
    def init_all_dicts(self, file_name):
        with open(file_name, "rb") as fp:
            dep = pickle.load(fp)
            cont = pickle.load(fp)
            stop = pickle.load(fp)

        return dep, cont, stop

        
    def run_em(self):
        for sentence in self.sentences:
            parsing_algo = ParsingAlgo(sentence,
                                       self.initial_values_path)
            marginals = parsing_algo.get_marginals()
            nodes = parsing_algo.get_hypergraph_nodes()
            self.update_counts(marginals, nodes,
                               ["*"] + sentence.split())
#            pprint.pprint(self.counts)

        self.update_parameters()

    def update_counts(self, marginals, nodes, words):
        for node in nodes:
            node_type, direct, span = node.label.split()
            span = span.split("-")
            head_word,modifier = self.get_head_word(direct,span,
                                                    words)
            adj = self.is_adj(int(span[1]), int(span[0]))
            if(node_type == "trap"):
                self.dep_counts[head_word, modifier, direct, adj] += \
                    marginals[node]
            if(node_type == "triStop"):
                self.stop_counts[head_word, direct, adj] +=  \
                    marginals[node]

    def get_head_word(self, direct, span, words):
        if direct=="left" :
            return words[int(span[1])], words[int(span[0])]
        return words[int(span[0])], words[int(span[1])]
                
    def update_parameters(self):
        keys = self.dep_count.keys()
        for key in keys:
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
        return 1 if abs(pos2-pos1) == 1 else 0

        
        
    
parser = Parser("data/corpus.txt", "data/initial_values")
parser.run_em()
