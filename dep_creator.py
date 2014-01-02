from math import exp
from collections import defaultdict
from mult_holder import MultinomialHolder

class DepCreator:

    def __init__(self):
        self.mult_holder = MultinomialHolder()

    def add_entry(self, sentence):
        if len(sentence.split()) == 4:
             self.add_root_entry(sentence)
        else:
             self.add_dep_entry(sentence)

    def add_dep_entry(self, sentence):
        dep_type, tag1, symbol, tag2, colon, value = sentence.split()
        if "left" in dep_type:
          self.mult_holder.inc_counts(tag1, (tag2, "left"),
                                      exp(float(value)))
        if "right" in dep_type:
          self.mult_holder.inc_counts(tag2, (tag1, "right"),
                                      exp(float(value)))
    def add_root_entry(self, sentence):
        root, tag, colon, value = sentence.split()
        self.mult_holder.inc_counts(tag, ("*", "left"),
                                      exp(float(value)))
        self.mult_holder.inc_counts(tag, ("*", "right"),
                                      exp(float(value)))
