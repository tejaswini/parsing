from collections import namedtuple, defaultdict
import pprint

class Multinomial:

    def __init__(self):
        self.prob = defaultdict(float)
        self.counts = defaultdict(float)
        self.total = 0

    def inc_counts(self, instance, counts):
            self.counts[instance] += counts
            self.total += counts

    def estimate(self):
        self.prob = defaultdict(float)
        if(self.total == 0):
            return
        for instance in self.counts.keys():
          self.prob[instance] = \
              self.counts[instance] / self.total
        self.counts = defaultdict(float)
        self.total = 0.0
