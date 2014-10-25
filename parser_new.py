from eisner_algo import EisnerAlgo
import numpy as np
from collections import defaultdict
import pprint

class Parser:

    def __init__(self, corpus_path, initial_values_path,
                 final_value_path,debug_mode):
        self.sentences = self.get_sentences(corpus_path)
        print "size of sentences " + str(len(self.sentences))
        # self.debug_mode = debug_mode
        # self.final_value_path = final_value_path
        # self.pickle_handler = PickleHandler(initial_values_path)
        # dep_mult_list, stop_mult_list =\
        #     self.pickle_handler.init_all_dicts()
        # self.stop_multinomial_holder = MultinomialHolder()
        # self.stop_multinomial_holder.mult_list = stop_mult_list
        # self.dep_multinomial_holder = MultinomialHolder()
        # self.dep_multinomial_holder.mult_list = dep_mult_list
        self.num_shapes = 3
        self.num_dir = 2
        self.tag_dict = {'NP':0, 'NNP':1, 'VP':2, 'NN': 3, 'PP':4, 'VBZ':5, 'DT':6,
                         'IN':7, 'JJ':8, 'NNS':9, 'PRP':10, 'RB':11, 'VB':12, 'VBD':13, 'VBG':14, 'VBN':15, 'VBP':16, 'MD':17, 'CD':18, 'CC':19, 'EX':20, 'PDT':21, 'WP':22, 'POS':23, 'PRP$':24, 'RBR':25, 'RBS':26, 'JJR':27, 'TO':28, 'NNPS':29, 'RP':30, 'ROOT':31, 'JJS': 32, '$':33, 'WRB':34, 'WDT':35, 'LS':36, 'UH':37, '#':38, 'SYM':39, 'FW':40}
        key_size = len(self.tag_dict)
        print "key size is " + str(key_size)
        pprint.pprint(self.tag_dict)
        print "value for JJR" + str(self.tag_dict['JJR'])
        self.counts = np.empty((self.num_shapes, self.num_dir, 2, key_size, key_size))
        self.counts.fill(0.00001)

    def run_em(self):
        sum_probs = defaultdict(lambda: 1.0)
        for i in range(1):
            print "iteration ", i
            for sentence in self.sentences:
                if(sentence.strip() == ""):
                    continue
                eisner_algo = EisnerAlgo()
                sentence = "ROOT " + sentence
                print "sentence is" + sentence
                eisner_algo.eisner_first_order(len(sentence.split(' ')))
                marginals = eisner_algo.compute_marginals(np.random.random(3*3*3*2*2))
#		sum_probs[i] += math.log(parsing_algo.total_potentials)
                edges = eisner_algo.graph.edges
                # print edges
                # pprint.pprint(edges)
                self.update_counts(marginals, edges, sentence)

            # if(sum_probs[i-1]!=1.0):
            #     assert sum_probs[i] > sum_probs[i-1], \
            #      "The prob are %r, %r"% (sum_probs[i],  sum_probs[i-1])

            self.estimate()
#            self.validate_multinomials(self.dep_multinomial_holder)
#            self.validate_multinomials(self.stop_multinomial_holder)

	# pickle_hand = PickleHandler(self.final_value_path)
	# pickle_hand.write_to_pickle(self.dep_multinomial_holder.\
        #    mult_list, self.stop_multinomial_holder.mult_list)
	# pprint.pprint(sum_probs)


    def increment_counts(self, edges, marginals, sentence):
#        print "edges are"
 #       pprint.pprint(edges)
        n = len(sentence.split(" "))

        tag_indices = self.indices_of_tag_dict(sentence.strip().split(" "))

#        print "indices are"
#        pprint.pprint(tag_indices)
    
        count_indices = np.zeros((edges.size, 5))
    
        shapes = edges / (n*n*2*2)
        count_indices[:,0] = shapes
        x = edges - (shapes * n*n*2*2)
        direction = x / (n*n*2)
        count_indices[:,1] = direction

        x = x%(n*n*2)
        is_adj = x / (n*n)
        count_indices[:,2] = is_adj
    
        x = x - (is_adj*16)
        row = x/n
        count_indices[:,3] = tag_indices[row]
    
        column = x%n
        count_indices[:,4] = tag_indices[column]

        self.counts[count_indices[:,0].tolist(), count_indices[:,1].tolist(), count_indices[:,2].tolist(), count_indices[:,3].tolist(), count_indices[:,4].tolist()] += marginals


#        print "count_indices"
#        pprint.pprint(count_indices)

#        print "counts is"
#        pprint.pprint(self.counts)

    
    def update_counts(self, edge_marginals, edges, sentence):
        marginal_values = defaultdict(float)
        for edge in edges:
            marginal_values[edge.label] += edge_marginals[edge.id]

            labels = np.array(marginal_values.keys())
#            pprint.pprint(labels)
            marginals = np.array(marginal_values.values())
#            pprint.pprint(marginals)
            
            self.increment_counts(labels, marginals, sentence)

    def indices_of_tag_dict(self, indices):
        return np.array([self.tag_dict[i] for i in indices])

    def estimate(self):
#        print "estimate"
    #    pprint.pprint(counts.sum(axis=4, keepdims=True))
        return  self.counts / self.counts.sum(axis=4, keepdims=True)

    def get_sentences(self, file_path):
        sentences = []
        with open(file_path,"r") as fp:
            sentences = fp.readlines()
        return sentences[0:5]

    def validate_multinomials(self, multinomial_holder):
        for key, mult in multinomial_holder.mult_list.iteritems():
            if(self.debug_mode):
                print key
                pprint.pprint(mult.prob)

            total = sum(mult.prob.values())
            assert round(total, 1) == 1.0 or round(total, 1) == 0 ,\
               "The mult for " + str(key) + " is not totalling to 1 "\
               + str(total)

if __name__ == "__main__":
    parser = Parser("data/sentences_train.txt",
                    "data/harmonic_values_mult", "data/harmonic_final",
                    False)
    parser.run_em()
