from collections import defaultdict

class StopContMultinomial:

    def __init__(self):
        self.stop_prob = defaultdict(float)
        self.cont_prob = defaultdict(float)
        self.stop_counts = defaultdict(float)
        self.total = 0

    def inc_counts(self, instance, counts):
        self.stop_counts[instance] += counts
        self.total += counts

    def estimate(self, dep_total):
        self.stop_prob = defaultdict(float)
        self.cont_prob = defaultdict(float)
        if(self.total == 0):
           self.stop_counts = defaultdict(float)
           return
        denom = self.total + dep_total
        
        for instance in self.stop_counts.keys():
          self.stop_prob[instance] = self.stop_counts[instance] / denom

          self.cont_prob[instance] = dep_total / denom
