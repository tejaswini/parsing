from eisner_algo import EisnerAlgo
import numpy as np
from collections import defaultdict
import pprint

class Parser:


    def __init__(self, corpus_path, initial_values_path,
                 final_value_path,debug_mode):
        self.sentences = self.get_sentences(corpus_path)
        self.num_shapes = 3
        self.num_dir = 2
        self.num_adj = 2
        self.tag_dict = {'NP':0, 'NNP':1, 'VP':2, 'NN': 3, 'PP':4, 'VBZ':5, 'DT':6,
                         'IN':7, 'JJ':8, 'NNS':9, 'PRP':10, 'RB':11, 'VB':12, 'VBD':13, 'VBG':14, 'VBN':15, 'VBP':16, 'MD':17, 'CD':18, 'CC':19, 'EX':20, 'PDT':21, 'WP':22, 'POS':23, 'PRP$':24, 'RBR':25, 'RBS':26, 'JJR':27, 'TO':28, 'NNPS':29, 'RP':30, 'ROOT':31, 'JJS': 32, '$':33, 'WRB':34, 'WDT':35, 'LS':36, 'UH':37, '#':38, 'SYM':39, 'FW':40}
        key_size = len(self.tag_dict)
        self.counts = np.empty((self.num_shapes, self.num_dir, self.num_adj, key_size, key_size))
        self.counts_attach = np.empty((self.num_shapes, self.num_dir, self.num_adj, key_size))
        self.prob_attach = np.random.random(self.num_shapes * self.num_dir * self.num_adj * key_size * key_size).reshape([self.num_shapes, self.num_dir, self.num_adj, key_size, key_size])
        self.prob = np.random.random(self.num_shapes * self.num_dir * self.num_adj * key_size * key_size).reshape([self.num_shapes, self.num_dir, self.num_adj, key_size, key_size])
        np.seterr(divide='ignore', invalid='ignore')

#np.empty((self.num_shapes, self.num_dir, self.num_adj, key_size, key_size))
    

    def run_em(self):
        sum_probs = defaultdict(lambda: 1.0)
        eisner_algo = EisnerAlgo()
        for i in range(5):
            print "iteration ", i
            self.counts.fill(0.0000000)
            for sentence in self.sentences:
                if(sentence.strip() == ""):
                    continue
                sentence = "ROOT " + sentence
                print "sentence is " + sentence
                sentence = sentence.strip().split(' ')
                n = len(sentence)
                self.tag_indices = self.indices_of_tag_dict(sentence)
                eisner_algo.eisner_first_order(sentence)
                label_scores = self.construct_label_scores(sentence)
                marginals = eisner_algo.compute_marginals(label_scores)
#		sum_probs[i] += math.log(parsing_algo.total_potentials)
                edges = eisner_algo.graph.edges
                self.update_counts(marginals, edges, sentence)
#TODO:
            # if(sum_probs[i-1]!=1.0):
            #     assert sum_probs[i] > sum_probs[i-1], \
            #      "The prob are %r, %r"% (sum_probs[i],  sum_probs[i-1])

            self.prob = self.estimate_prob()
# TODO validate_multinomials(self.dep_multinomial_holder)


    def increment_counts(self, heads, marginals, sentence):
        n = len(sentence)

        print "heads"
        pprint.pprint(heads)
    
        shapes = heads / (n*n*2)
        x = heads - (shapes * n*n*2)
        direction = x / (n*n)

        print "shapes are"
        pprint.pprint(shapes)

        x = x%(n*n*2)
        is_adj = x / (n*n)
    
        x = x - (is_adj*n*n)
        row = x/n

        print "row is"
        pprint.pprint(row)

        column = x%n

        row = self.tag_indices[row]
    
        column = x%n
        column = self.tag_indices[column]

        self.counts[shapes.tolist(), direction.tolist(), is_adj.tolist(), row.tolist(), column.tolist()] += marginals


        print "indices of shapes are"
        pprint.pprint(np.where(shapes != 1))

        pprint.pprint(shapes[np.where(shapes != 1)])
                                   

    def update_counts(self, edge_marginals, edges, sentence):
        heads = np.array([],dtype=np.int64)
        marginals = []
        for edge in edges:
            marginals.append(edge_marginals[edge.id])
            heads = np.append(heads, [edge.head.label])

        self.increment_counts(heads, marginals, sentence)

    def indices_of_tag_dict(self, indices):
        return np.array([self.tag_dict[i] for i in indices])

    def estimate_prob(self):
        return np.divide(self.counts , self.counts.sum(axis=4, keepdims=True))

    def estimate_attachment(self):
        return 1

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
    parser = Parser("sample_data",
                    "data/harmonic_values_mult", "data/harmonic_final",
                    False)
    parser.run_em()
