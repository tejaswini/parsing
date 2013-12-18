from math import exp
from collections import defaultdict

class DepCreator:

    def __init__(self):
        self.dep = defaultdict(float)

    def add_entry(self, sentence):
        dep_type, tag1, symbol, tag2, colon, value = sentence.split()
        if "left" in dep_type:
          self.dep[tag2, tag1, "left"] =  exp(float(value))
        if "right" in dep_type:
          self.dep[tag1, tag2, "right"] =  exp(float(value))

    def is_adj(self, child_det):
        return "adj" if child_det == "nochild" else "non-adj"

