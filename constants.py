import numpy as np

class Constants:

    def __init__(self):
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
        self.cont = 0; self.stop = 1
        self.right = 0; self.left = 1
        self.adj = 1; self.non_adj = 0

    def indices_of_tag_dict(self, indices):
        return np.array([self.tag_dict[i] for i in indices])

    def construct_label_scores(self, sentence, tag_indices, prob):
       shapes = np.tile(np.repeat(np.arange(self.num_shapes), \
                tag_indices.size * self.num_adj * self.num_dir), tag_indices.size)

       directions = np.tile(np.repeat(np.arange(self.num_dir), self.num_adj),
                   self.num_shapes * tag_indices.size * tag_indices.size)

       adj = np.tile(np.arange(self.num_adj), self.num_dir * self.num_shapes *\
                           tag_indices.size * tag_indices.size)

       tags_row = np.repeat(tag_indices, self.num_adj * self.num_dir * \
                            self.num_shapes * tag_indices.size)

       tags_column = np.tile(np.repeat(tag_indices, self.num_adj *\
                           self.num_dir * self.num_shapes), tag_indices.size)

       return prob[shapes.tolist(), directions.tolist(), adj.tolist(), tags_row.tolist(), tags_column.tolist()]



