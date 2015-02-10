from math import exp
from collections import defaultdict
from constants import Constants
import numpy as np

class ContStopCreator:

    def __init__(self):
        self.constants = Constants()
        self.prob_cont = np.zeros(self.constants.num_dir * self.constants.\
           num_adj * self.constants.stop_cont* self.constants.key_size).reshape([\
           self.constants.num_dir, self.constants.num_adj, self.constants.key_size,
           self.constants.stop_cont])

    def add_entry(self, sentence):
      dep_type, tag, child_det, colon, value = sentence.split()
      self.prob_cont[self.direction(dep_type), self.is_adj(child_det),
          self.constants.tag_dict[tag], self.state(dep_type)] +=  exp(float(value))

    def is_adj(self, child_det):
        return self.constants.adj if child_det == "nochild" else \
            self.constants.non_adj

    def direction(self, dep_type):
        if "left" in dep_type:
            return self.constants.left
        else:
            return self.constants.right

    def state(self, dep_type):
        if "stop" in dep_type:
            return self.constants.stop
        else:
            return self.constants.cont    
