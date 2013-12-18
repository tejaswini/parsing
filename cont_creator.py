from math import exp
from collections import defaultdict

class ContStopCreator:

    def __init__(self):
        self.prob = defaultdict(float)

    def add_entry(self, sentence):
      cont_type, tag, child_det, colon, value = sentence.split()
      if "left" in cont_type:
          self.prob[tag, "left", self.is_adj(child_det)] = \
              exp(float(value))
      if "right" in cont_type:
          self.prob[tag, "right", self.is_adj(child_det)] = \
              exp(float(value))

    def is_adj(self, child_det):
        return "adj" if child_det == "nochild" else "non-adj"
