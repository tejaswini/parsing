from collections import defaultdict

class StopContMultinomial:

    def __init__(self):
        self.stop_prob = defaultdict(float)
        self.cont_prob = defaultdict(float)
        self.stop_counts = defaultdict(float)
        self.cont_counts = defaultdict(float)
        self.stop_total = 0
        self.cont_total = 0

    def inc_stop_counts(self, instance, counts):
        self.stop_counts[instance] += counts
        self.stop_total += counts

    def inc_cont_counts(self, instance, counts):
        self.cont_counts[instance] += counts
        self.cont_total += counts


    def estimate(self):
        # self.stop_prob = defaultdict(float)
        # self.cont_prob = defaultdict(float)
        denom = self.stop_total + self.cont_total

        for instance in self.stop_counts.keys():
          self.stop_prob[instance] = self.stop_counts[instance] / denom
          self.cont_prob[instance] = self.cont_total / denom

        keys = list(set(self.cont_counts.keys()) - \
                        set(self.stop_counts.keys()))

        for instance in keys:
          self.stop_prob[instance] = self.stop_counts[instance] / denom
          self.cont_prob[instance] = self.cont_total / denom
            

