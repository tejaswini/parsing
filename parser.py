from parsing_hypergraph import ParsingAlgo
import pprint
from collections import defaultdict
import cPickle as pickle

class Parser:

    def __init__(self, corpus_path, initial_values_path):
        self.sentences = self.get_sentences(corpus_path)
        self.initial_values_path = initial_values_path
        self.counts = defaultdict(float)
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
            if(node_type == "trap"):
                self.counts[node_type, direct, head_word, modifier] += \
                    marginals[node]
            else:
                self.counts[node_type,direct,head_word] +=  \
                    marginals[node]

    def get_head_word(self, direct,span,words):
        if direct=="left" :
            return words[int(span[1])], words[int(span[0])]
        return words[int(span[0])], words[int(span[1])]
                
    def update_parameters(self):
        keys = self.dep.keys()
        # pprint.pprint(keys)
        # print "counts"
        # pprint.pprint(self.counts.keys())
        for key in keys:
            key = keys[0]
            values_trap = self.get_values_with_filter(key ,"trap")
            total_trap = sum(values_trap)
            if(total_trap == 0):
                continue

            self.dep[key] = \
                self.counts[("trap", key[2], key[0], key[1])] / total_trap
            values_tri_stop = self.get_values_with_filter(key ,"tri")
            total_tri_stop = sum(values_tri_stop)

            self.cont[key] = total_trap / total_trap + total_tri_stop
                
            self.stop[key] = 1 - self.cont[key]
            
        

    def get_values_with_filter(self, key, node_type):
        return map(self.counts.get, filter(lambda k: k[2] == key[0] \
                   and key[2] == k[1] and k[0] == "trap", 
                                               self.counts.keys() ) )
        

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences
        
        
    
parser = Parser("data/corpus.txt", "data/initial_values")
parser.run_em()
