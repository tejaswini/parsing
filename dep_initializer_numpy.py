from math import exp
from collections import defaultdict
from constants import Constants
import numpy as np

class DepCreator:

    def __init__(self):
        self.constants = Constants()
        self.counts_attach = np.zeros(self.constants.num_dir *\
             self.constants.key_size * self.constants.key_size).reshape([\
             self.constants.num_dir, self.constants.key_size,
             self.constants.key_size])


    def add_entry(self, sentence):
        if len(sentence.split()) == 4:
             self.add_root_entry(sentence)
        else:
             self.add_dep_entry(sentence)

    def add_dep_entry(self, sentence):
        dep_type, tag1, symbol, tag2, colon, value = sentence.split()
        if "left" in dep_type:
           self.counts_attach[self.constants.left, self.constants.tag_dict[tag2],
                   self.constants.tag_dict[tag1]] =  exp(float(value))
        if "right" in dep_type:
            self.counts_attach[self.constants.right, self.constants.tag_dict[tag1],
                   self.constants.tag_dict[tag2]] =  exp(float(value))

    def add_root_entry(self, sentence):
        root, tag, colon, value = sentence.split()
        self.counts_attach[self.constants.left, self.constants.tag_dict["*"],
                           self.constants.tag_dict[tag]] =  exp(0)
        self.counts_attach[self.constants.right, self.constants.tag_dict["*"],
                           self.constants.tag_dict[tag]] =  exp(float(value))
