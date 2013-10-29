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
                self.counts[node_type,direct,head_word,modifier] += \
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
        pprint.pprint(keys)
        

    def get_values_with_filter(self, key):
        map(self.counts.get, filter(lambda k: k, mydict.keys() ) )
        

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences
        
        
    
parser = Parser("data/corpus.txt", "data/initial_values")
parser.run_em()
