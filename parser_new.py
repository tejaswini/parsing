from eisner_algo import EisnerAlgo
import numpy as np
from collections import defaultdict
import pprint
from pickle_handler import PickleHandler
from constants import Constants

class Parser:

    def __init__(self, corpus_path, initial_values_path,
                 final_value_path,debug_mode):
        self.sentences = self.get_sentences(corpus_path)
        self.trap = 1
        self.tri_stop = 2
        self.tri = 0
        self.num_shapes = 3
        self.num_dir = 2
        self.num_adj = 2
        self.stop_cont = 2
        self.constants = Constants()
        self.tag_dict = self.constants.tag_dict
        self.key_size = len(self.tag_dict)
        self.counts = np.empty((self.num_shapes, self.num_dir, self.num_adj, self.key_size, self.key_size))
        self.counts_attach = np.empty((self.num_dir, self.key_size, self.key_size))
        self.counts_cont = np.empty((self.num_dir, self.num_adj, self.key_size, self.stop_cont))
        self.pickle_handler = PickleHandler("data/harmonic_values_numpy")
        self.prob_attach, self.prob_cont = self.pickle_handler.init_all_dicts()
        self.prob = np.empty((self.num_shapes, self.num_dir, self.num_adj,
                              self.key_size, self.key_size))
        self.prob.fill(-1)
        np.seterr(divide='ignore', invalid='ignore')

    def run_em(self):
        sum_probs = defaultdict(lambda: 1.0)
        eisner_algo = EisnerAlgo()
        for i in range(10):

            self.iteration = i
            self.prob = self.constants.compute_prob(self.prob_attach,
                                                    self.prob_cont)
            print "iteration ", i
            self.counts_attach.fill(0.0000000)
            self.counts_cont.fill(0.0000000)

            for sentence in self.sentences:
                if(sentence.strip() == ""):
                    continue
                sentence = "* " + sentence
                print "sentence is " + sentence
                sentence = sentence.strip().split(' ')
                n = len(sentence)
                self.tag_indices = self.constants.indices_of_tag_dict(sentence)
                eisner_algo.reset_values()
                eisner_algo.eisner_first_order(sentence)
                label_scores = self.constants.construct_label_scores(\
                    self.tag_indices, self.prob)
                marginals = eisner_algo.compute_marginals(label_scores)
#		sum_probs[i] += math.log(parsing_algo.total_potentials)
                edges = eisner_algo.graph.edges
                self.update_counts(marginals, edges, sentence)

#TODO:
            # if(sum_probs[i-1]!=1.0):
            #     assert sum_probs[i] > sum_probs[i-1], \
            #      "The prob are %r, %r"% (sum_probs[i],  sum_probs[i-1])
            self.estimate_prob()
        self.pickle_handler.write_to_pickle(self.prob_attach, self.prob_cont,
                                                 "data/numpy_final")


# TODO validate_multinomials(self.dep_multinomial_holder)


    def increment_counts(self, heads, marginals, sentence, tails_for_head):
        n = len(sentence)
        shapes, direction, row, column = self.constants.get_indices(heads, n)
        adj = self.compute_adj_for_heads(heads, tails_for_head, shapes,
                                         direction, n)


        indices_needed = self.filter_stop_cont_indices(shapes)
        stop_cont = shapes[indices_needed] / 2

        direction = direction[indices_needed]
        row = row[indices_needed]
        column = column[indices_needed]
        
        right_indices = np.where(direction == self.constants.right)
        left_indices = np.where(direction == self.constants.left)

        heads1 = np.zeros(row.size, dtype=np.int64)
        heads1[right_indices] = row[right_indices]
        heads1[left_indices] = column[left_indices]

        mod = np.zeros(row.size, dtype=np.int64)
        mod[right_indices] = column[right_indices]
        mod[left_indices] = row[left_indices]
        
        if(np.isnan(sum(marginals[indices_needed]))):
            pprint.pprint("marginals nan")
            pprint.pprint(marginals)

        self.counts_attach[direction.tolist(), heads1.tolist(), mod.tolist()] +=\
                                          marginals[indices_needed]
        self.counts_cont[direction.tolist(), adj[indices_needed].tolist(), heads1.tolist(), stop_cont.tolist()] += marginals[indices_needed]

    def compute_adj_for_heads(self, heads, tails_for_head, shapes_head,direction_head, n):
        adj = np.array([], dtype=np.int64)
        for index, head in enumerate(heads):
            tails = tails_for_head[head]
            shapes, direction, row, column = self.constants.get_indices(tails, n)

            if(shapes_head[index] == 1):
                if(direction_head[index] == self.constants.left):

                     adj_value = self.constants.is_adj(row[1], column[0])
                     adj = np.append(adj, adj_value)
                else:
                     adj_value = self.constants.is_adj(row[0], column[1])
                     adj = np.append(adj, adj_value)

            elif (shapes_head[index] == 2 or shapes_head[index] == 0) and\
                              row[0] == column[0]:
                adj = np.append(adj, self.constants.adj)
            else:
                adj = np.append(adj, self.constants.non_adj)

        return adj
                    

    def filter_stop_cont_indices(self, shapes):
        return np.where(shapes != 1)

    def stop_cont_values(self, shapes):
       return shapes / 2

    def update_counts(self, edge_marginals, edges, sentence):
        heads = np.array([], dtype=np.int64)
        tails_for_heads = {}
        marginals = np.array([], dtype=np.float64)
        for edge in edges:
            marginals = np.append(marginals, edge_marginals[edge.id])
            heads = np.append(heads, [edge.head.label])
            tails = np.array([], dtype=np.int64)
            for tail in edge.tail:
               tails = np.append(tails, tail.label)
            tails_for_heads[edge.head.label] = tails

        self.increment_counts(heads, marginals, sentence, tails_for_heads)

    def indices_of_tag_dict(self, indices):
        return np.array([self.tag_dict[i] for i in indices])

    def estimate_prob(self):
       self.prob_attach =  np.divide(self.counts_attach, self.counts_attach.sum(axis=2, keepdims=True))
       self.prob_cont = np.divide(self.counts_cont, self.counts_cont.sum(axis=3, keepdims=True))
       self.prob_attach = np.nan_to_num(self.prob_attach)
       self.prob_cont = np.nan_to_num(self.prob_cont)

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences

if __name__ == "__main__":
    parser = Parser("data/sentences_train.txt",
                    "data/harmonic_values_numpy", "data/numpy_final",
                    False)
    parser.run_em()
