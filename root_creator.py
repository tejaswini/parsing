from math import exp
from collections import defaultdict

class RootCreator:

    def __init__(self):
        self.prob = defaultdict(float)

    def add_entry(self,sentence):
      root, tag, colon, value = sentence.split()
      # self.prob[tag] = exp(float(value))
      self.prob["*", tag, "left"] = exp(float(value))
      self.prob["*", tag, "right"] = exp(float(value))
