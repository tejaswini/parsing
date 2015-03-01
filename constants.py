import numpy as np
import pprint

class Constants:

    def __init__(self):
        self.trap = 1
        self.tri_stop = 2
        self.tri = 0
        self.num_shapes = 3
        self.num_dir = 2
        self.num_adj = 2
        self.stop_cont = 2
        self.tag_dict = {'NNP':0, 'NN': 1, 'VBZ':2, 'DT':3,
                         'IN':4, 'JJ':5, 'NNS':6, 'PRP':7, 'RB':8, 'VB':9, 'VBD':10, 'VBG':11, 'VBN':12, 'VBP':13, 'MD':14, 'CD':15, 'CC':16, 'EX':17, 'PDT':18, 'WP':19, 'POS':20, 'PRP$':21, 'RBR':22, 'RBS':23, 'JJR':24, 'TO':25, 'NNPS':26, 'RP':27, '*':28, 'JJS': 29, '$':30, 'WRB':31, 'WDT':32, 'LS':33, 'UH':34, '#':35, 'SYM':36, 'FW':37}
        self.key_size = len(self.tag_dict)
        self.cont = 0; self.stop = 1
        self.right = 0; self.left = 1
        self.adj = 1; self.non_adj = 0

    def indices_of_tag_dict(self, sentence):
        return np.array([self.tag_dict[word] for word in sentence])

    def construct_label_scores(self, sentence, tag_indices, prob):

       label_scores = np.empty((self.num_shapes, self.num_dir, self.num_adj,
                              tag_indices.size, tag_indices.size))
       label_scores.fill(0.00)

       print "tag indices"
       pprint.pprint(tag_indices)
       
       shapes = np.repeat(np.arange(self.num_shapes), self.num_adj * self.num_dir*\
                tag_indices.size * tag_indices.size)

       directions = np.tile(np.repeat(np.arange(self.num_dir), self.num_adj *\
                      tag_indices.size * tag_indices.size), self.num_shapes)

       adj = np.tile(np.repeat(np.arange(self.num_adj), tag_indices.size *\
                          tag_indices.size), self.num_dir * self.num_shapes)

       row = np.tile(np.repeat(np.arange(tag_indices.size), tag_indices.size), 
                      self.num_adj * self.num_dir * self.num_shapes)

       column = np.tile(np.arange(tag_indices.size), self.num_adj *\
                           self.num_dir * self.num_shapes * tag_indices.size)

       tags_row = np.tile(np.repeat(tag_indices, tag_indices.size), self.num_adj *\
                         self.num_dir * self.num_shapes)
       
       tags_column = np.tile(tag_indices, self.num_adj * self.num_dir *\
                                 self.num_shapes * tag_indices.size)

       label_scores[shapes.tolist(), directions.tolist(), adj.tolist(), row.tolist(), column.tolist()] = prob[shapes.tolist(), directions.tolist(), adj.tolist(), tags_row.tolist(), tags_column.tolist()]

       return label_scores

    def filter_stop_cont_indices(self, shapes):
        return np.where(shapes != 1)


    def compute_prob(self, prob_attach, prob_cont):

       prob = np.empty((self.num_shapes, self.num_dir, self.num_adj,
                              self.key_size, self.key_size))
       prob.fill(-1)
 
       shapes = np.repeat(np.arange(self.num_shapes), \
               self.key_size * self.num_adj * self.num_dir * self.key_size)
       print "shapes " + str(shapes.size)
       filtered_indices = self.filter_stop_cont_indices(shapes)

       stop_cont = shapes[np.where(shapes != 1)]
       stop_cont /= 2

       directions = np.tile(np.repeat(np.arange(self.num_dir), self.num_adj *\
                        self.key_size * self.key_size) , self.num_shapes)

       adj = np.tile(np.repeat(np.arange(self.num_adj), self.key_size *\
                        self.key_size), self.num_dir * self.num_shapes)
       
       heads = np.tile(np.repeat(np.arange(self.key_size), self.key_size),
                       self.num_adj * self.num_dir * self.num_shapes)

       modifiers = np.tile(np.arange(self.key_size), self.num_adj *\
                    self.num_dir * self.num_shapes * self.key_size)

       prob[shapes[filtered_indices].tolist(), directions[filtered_indices].tolist(), adj[filtered_indices].tolist(),
                 heads[filtered_indices].tolist(), modifiers[filtered_indices].tolist()] =\
                 prob_attach[directions[filtered_indices].tolist(),
           heads[filtered_indices].tolist(), modifiers[filtered_indices].tolist()] * np.transpose(prob_cont[directions[filtered_indices].tolist(),
           adj[filtered_indices].tolist(), heads[filtered_indices].tolist(), stop_cont.tolist()])

       prob[self.trap:self.tri_stop] = 1
#       self.pickle_handler.write_prob_to_pickle(prob, "data/prob"+str(self.iteration))
       return prob
