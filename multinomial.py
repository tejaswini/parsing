from collections import namedtuple, defaultdict
import pprint

class InstanceKey(namedtuple("InstanceKey", ["head_word", "modifier",
                                             "dir", "adj"])):

    def __str__(self):
        return "%s %s %s-%s" % (self.head_word, self.modifier,
                                self.dir, self.adj)

# The stop and cont prob are conditioned on head_word, dir and adj
# dep prob is conditioned on head_word, modifier and dir
# Hence we need different counts for cont and dep
class Multinomial:

    def __init__(self):
        self.prob = defaultdict(lambda : defaultdict(float))
        self.counts = defaultdict(float)
        self.total = defaultdict(int)

    def inc_counts(self, count_type, instance, counts):
            self.counts[count_type, instance] += counts
            self.total[count_type] += counts

    def estimate(self):
        total = 0

        for key in self.total.keys():
            total += self.total[key]
            self.prob[key] = defaultdict(float)
        
        for key in self.counts.keys():
          event_type = key[0]
          instance = key[1]
          self.prob[event_type][instance] = \
              self.counts[event_type, instance] / total

        print "total is "
        pprint.pprint(total)
        print "prob is "
        pprint.pprint(self.prob)
