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
        self.stop_prob = defaultdict(float)
        self.dep_prob = defaultdict(float)
        self.cont_prob = defaultdict(float)
        self.cont_counts = defaultdict(float)
        self.cont_counts_dep = defaultdict(float)
        self.stop_counts = defaultdict(float)
        self.cont_total = 0
        self.cont_total_dep = 0
        self.stop_total = 0

    def inc_counts(self, count_type, instance, counts):
        if count_type == "stop":
            self.stop_counts[instance] += counts
            self.stop_total += counts
        else:
            cont_key = self.get_cont_key(instance)
            dep_key = self.get_dep_key(instance)
            self.cont_counts[cont_key] += counts
            self.cont_counts_dep[dep_key] += counts
            self.cont_total += counts
            self.cont_total_dep += counts


    def estimate(self):
        total = self.cont_total + self.stop_total
        
        for instance in self.cont_counts_dep.keys():
          self.dep_prob[instance] = self.cont_counts_dep[instance] /\
                 self.cont_total_dep

        for instance in self.stop_counts.keys():
          self.stop_prob[instance] = self.stop_counts[instance] / total
          self.cont_prob[instance] = self.cont_counts[instance] / total

        keys = list(set(self.cont_counts.keys()) - \
                        set(self.stop_counts.keys()))

        for instance in keys:
          self.cont_prob[instance] = self.cont_counts[instance] / total
          self.stop_prob[instance] = self.stop_counts[instance] / total

    def get_cont_key(self, key):
        inst_key = InstanceKey(key[0], key[1], key[2], key[3])
        return (inst_key.head_word, inst_key.dir, inst_key.adj)


    def get_dep_key(self, key):
        inst_key = InstanceKey(key[0], key[1], key[2], key[3])
        return (inst_key.head_word, inst_key.modifier, inst_key.dir)



