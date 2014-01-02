from math import exp
from collections import defaultdict
from mult_holder import MultinomialHolder

class ContStopCreator:

    def __init__(self):
        self.mult_holder = MultinomialHolder()
        self.stop = 0
        self.cont = 1

    def add_entry(self, sentence):
      dep_type, tag, child_det, colon, value = sentence.split()
      self.mult_holder.inc_counts(self.state(dep_type),
        (tag, self.direction(dep_type), self.is_adj(child_det)),
                                  exp(float(value)))

    def is_adj(self, child_det):
        return "adj" if child_det == "nochild" else "non-adj"

    def direction(self, dep_type):
        if "left" in dep_type:
            return "left"
        else:
            return "right"

    def state(self, dep_type):
        if "stop" in dep_type:
            return self.stop
        else:
            return self.cont    
