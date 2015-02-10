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
        self.tag_dict = {'NP':0, 'NNP':1, 'VP':2, 'NN': 3, 'PP':4, 'VBZ':5, 'DT':6,
                         'IN':7, 'JJ':8, 'NNS':9, 'PRP':10, 'RB':11, 'VB':12, 'VBD':13, 'VBG':14, 'VBN':15, 'VBP':16, 'MD':17, 'CD':18, 'CC':19, 'EX':20, 'PDT':21, 'WP':22, 'POS':23, 'PRP$':24, 'RBR':25, 'RBS':26, 'JJR':27, 'TO':28, 'NNPS':29, 'RP':30, '*':31, 'JJS': 32, '$':33, 'WRB':34, 'WDT':35, 'LS':36, 'UH':37, '#':38, 'SYM':39, 'FW':40}
        self.key_size = len(self.tag_dict)
        self.counts = np.empty((self.num_shapes, self.num_dir, self.num_adj, self.key_size, self.key_size))
        self.counts_attach = np.empty((self.num_dir, self.key_size, self.key_size))
        self.counts_cont = np.empty((self.num_dir, self.num_adj, self.key_size, self.stop_cont))
        self.pickle_handler = PickleHandler("data/harmonic_values_numpy")
        self.prob_attach, self.prob_cont = self.pickle_handler.init_all_dicts()
        # self.prob_attach = np.random.random(self.num_dir * self.key_size * self.key_size).reshape([self.num_dir, self.key_size, self.key_size])
        # self.prob_cont = np.random.random(self.num_dir * self.num_adj * self.stop_cont* self.key_size).reshape([self.num_dir, self.num_adj, self.key_size, self.stop_cont])
        self.prob = np.empty((self.num_shapes, self.num_dir, self.num_adj,
                              self.key_size, self.key_size))
        np.seterr(divide='ignore', invalid='ignore')
        self.constants = Constants()
        self.inter_number = 0


    def run_em(self):
        sum_probs = defaultdict(lambda: 1.0)
        eisner_algo = EisnerAlgo()
        for i in range(10):
            self.compute_prob()

            self.iteration = i
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
                eisner_algo.eisner_first_order(sentence)
                label_scores = self.constants.construct_label_scores(sentence,
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

# TODO validate_multinomials(self.dep_multinomial_holder)


    def increment_counts(self, heads, marginals, sentence):
        n = len(sentence)

        shapes = heads / (n*n*2)
        indices_needed = self.filter_stop_cont_indices(shapes)
        stop_cont = shapes[indices_needed]
        stop_cont /= 2

        x = heads - (shapes * n*n*2)
        direction = x / (n*n)

        x = x%(n*n*2)
        is_adj = x / (n*n)
    
        x = x - (is_adj*n*n)
        row = x/n

        row = self.tag_indices[row]
    
        column = x%n
        column = self.tag_indices[column]

        if(np.isnan(sum(marginals[indices_needed]))):
            pprint.pprint("marginals nan")
            pprint.pprint(marginals)

        self.counts_attach[direction[indices_needed].tolist(), row[indices_needed].tolist(), column[indices_needed].tolist()] += marginals[indices_needed]
        self.counts_cont[direction[indices_needed].tolist(), is_adj[indices_needed].tolist(), row[indices_needed].tolist(), stop_cont.tolist()] += marginals[indices_needed]

    def filter_stop_cont_indices(self, shapes):
        return np.where(shapes != 1)

    def stop_cont_values(self, shapes):
       return shapes / 2

    def compute_prob(self):
       shapes = np.tile(np.repeat(np.arange(self.num_shapes), \
               self.key_size * self.num_adj * self.num_dir),\
                            self.key_size)

       stop_cont = shapes[np.where(shapes != 1)]
       stop_cont /= 2

       directions = np.tile(np.repeat(np.arange(self.num_dir), self.num_adj),
                (self.num_shapes-1) * self.key_size * self.key_size)

       adj = np.tile(np.arange(self.num_adj), self.num_dir * (self.num_shapes - 1)*\
                           self.key_size * self.key_size)

       heads = np.repeat(np.arange(self.key_size), self.num_adj * self.num_dir * \
                         (self.num_shapes - 1) * self.key_size)

       modifiers = np.tile(np.repeat(np.arange(self.key_size), self.num_adj *\
                    self.num_dir * (self.num_shapes - 1)), self.key_size)

       self.prob[stop_cont.tolist(), directions.tolist(), adj.tolist(),
                 heads.tolist(), modifiers.tolist()] =\
                 self.prob_attach[directions.tolist(),
           heads.tolist(), modifiers.tolist()] * np.transpose(self.prob_cont[directions.tolist(),
           adj.tolist(), heads.tolist(), stop_cont.tolist()])

       self.prob[self.trap:self.tri_stop] = 1

    def update_counts(self, edge_marginals, edges, sentence):
        heads = np.array([], dtype=np.int64)
        marginals = np.array([], dtype=np.float64)
        for edge in edges:
            marginals = np.append(marginals, edge_marginals[edge.id])
            heads = np.append(heads, [edge.head.label])

        self.increment_counts(heads, marginals, sentence)

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

    def construct_label_scores(self, sentence):
       shapes = np.tile(np.repeat(np.arange(self.num_shapes), \
               self.tag_indices.size * self.num_adj * self.num_dir),\
                            self.tag_indices.size)

       directions = np.tile(np.repeat(np.arange(self.num_dir), self.num_adj),
                   self.num_shapes * self.tag_indices.size * self.tag_indices.size)

       adj = np.tile(np.arange(self.num_adj), self.num_dir * self.num_shapes *\
                           self.tag_indices.size * self.tag_indices.size)

       tags_row = np.repeat(self.tag_indices, self.num_adj * self.num_dir * \
                            self.num_shapes * self.tag_indices.size)

       tags_column = np.tile(np.repeat(self.tag_indices, self.num_adj *\
                           self.num_dir * self.num_shapes), self.tag_indices.size)

       return self.prob[shapes.tolist(), directions.tolist(), adj.tolist(), tags_row.tolist(), tags_column.tolist()]


if __name__ == "__main__":
    parser = Parser("data/sentences_train.txt",
                    "data/harmonic_values_numpy", "data/numpy_final",
                    False)
    parser.run_em()
