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
        self.pickle_handler = PickleHandler(self.initial_values_path)
        self.dep, self.cont, self.stop = \
            self.pickle_handler.init_all_dicts()
        # as we rewrite the probabilities each time, we use tmp instea\
        # of the original probabilities
        self.initial_values_path = "tmp"
        self.pickle_handler = PickleHandler(self.initial_values_path)
        self.pickle_handler.write_to_pickle(self.dep,
                                            self.cont,self.stop)

    def run_em(self):
        for i in range(10):
            print "iteration ", i
            if(i>5):
                stop_counts = self.stop_counts
                dep_counts = self.dep_counts
                with open("params"+str(i), "wb") as fp:
                    pickle.dump(stop_counts, fp)
                    pickle.dump(dep_counts, fp)

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
#            pprint.pprint(self.stop_counts)
#            pprint.pprint(self.dep_counts)
            self.pickle_handler.write_to_pickle(self.dep,self.cont,self.stop)

    def display_hash(hash_table):
        for key,value in hash_table.iteritems():
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
                self.dep_counts[head_word, modifier, direct, adj] \
                    += marginals[node.label]
            if(node_type == "triStop"):
                self.stop_counts[head_word, direct, adj] +=  \
                    marginals[node.label]

    def get_head_word(self, direct, span, words):
        return (words[int(span[1])], words[int(span[0])]) \
            if direct=="left" else \
            (words[int(span[0])], words[int(span[1])])

    def update_parameters(self):
        self.dep = defaultdict(float)
        self.stop = defaultdict(float)
        self.cont = defaultdict(float)
        for key in self.dep_counts.keys():
            values_trap = self.get_values_with_filter(key, self.dep_counts)
            total_trap = sum(values_trap)

            if(total_trap == 0):
                continue

            self.dep[key] = self.dep_counts[key] / total_trap
            # if(key == ('DT', 'NNS', 'left', 'non-adj')):
            #     print "total_trap", total_trap
            #     print "dep",self.dep[key],"dep_counts",self.dep_counts[key]

            assert self.dep[key] <= 1, "%s,%s"%(self.dep_counts[key],total_trap)

            stop_key = (key[0], key[2], key[3])
            self.stop[stop_key] = \
                self.stop_counts[stop_key] / (total_trap + self.stop_counts[stop_key])

            # if(stop_key == ('DT', 'left', 'non-adj')):
            #     print "stop value", self.stop[stop_key]
            #     print "stop count",self.stop_counts[stop_key],"denom", (total_trap + self.stop_counts[stop_key])

            assert self.stop[stop_key] <= 1, "%s,%s"%(self.stop_counts[stop_key],total_trap)

            self.cont[stop_key] = total_trap / \
                (total_trap + self.stop_counts[stop_key])
#1 - self.stop[stop_key]

        for key in self.dep_counts.keys():
            values_prob = self.get_values_with_filter(key, self.dep)
            values = self.get_values_with_filter(key, self.dep_counts)
            total_prob = sum(values_prob)
            assert total_prob <=1.001, "%s,%s,%s,%s,%s"%(key,total_prob,values,self.dep_counts[key],values_prob)

    def get_values_with_filter(self, key, hash_table):
       return [val for key2,val in hash_table.iteritems()
               if key[0] == key2[0] and key[2] == key2[2]
                  and key2[3] == key[3]]
               

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

    def is_adj(self, pos1, pos2):
        return "adj" if abs(pos2-pos1) == 1 else "non-adj"

if __name__ == "__main__":
    parser = Parser("data/corpus.txt", "data/harmonic_values") #"data/initial_values")
    parser.run_em()
    # print "stop probalities are"
    # pprint.pprint(parser.stop)
    # print "stop probalities are"
    # pprint.pprint(parser.cont)
    # print "dep probalities are"
    # pprint.pprint(parser.dep)
