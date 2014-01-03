from math import exp
from collections import defaultdict
from mult_holder import MultinomialHolder

class ContStopCreator:

    def __init__(self):
        self.mult_holder = MultinomialHolder()
        self.stop = False
        self.cont = True

    def add_entry(self, sentence):
      dep_type, tag, child_det, colon, value = sentence.split()
      self.mult_holder.inc_counts(self.state(dep_type),
        (tag, self.direction(dep_type), self.is_adj(child_det)),
                                  exp(float(value)))

    def is_adj(self, child_det):
        return True if child_det == "nochild" else False

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
