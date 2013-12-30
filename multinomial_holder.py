from dep_multinomial import DepMultinomial
from cont_stop_multinomial import StopContMultinomial
from memory_profiler import profile
import pprint

class MultinomialHolder:

    def __init__(self):
        #dep_mult_list_adj keeps track of dep along with adj
        #dep_mult_list tracks only dep
        self.dep_mult_list = {}
        self.dep_mult_list_adj = {}
        self.stop_mult_list = {}

    def inc_dep_counts(self, instance, cond_key, counts):
        if(cond_key[0:-1] not in self.dep_mult_list):
            self.dep_mult_list[cond_key[0:-1]] = DepMultinomial()

        if(cond_key not in self.dep_mult_list_adj):
            self.dep_mult_list_adj[cond_key] = DepMultinomial()

        self.dep_mult_list_adj[cond_key].inc_counts(instance, counts)
        self.dep_mult_list[cond_key[0:-1]].\
            inc_counts(instance, counts)
            
    def inc_stop_counts(self, instance, cond_key, counts):
        if(cond_key not in self.stop_mult_list):
            self.stop_mult_list[cond_key] = StopContMultinomial()
        self.stop_mult_list[cond_key].inc_counts(instance, counts)

    def estimate(self):
        self.estimate_dep()
        self.estimate_stop()

    def estimate_dep(self):
        for key in self.dep_mult_list.keys():
            self.dep_mult_list[key].estimate()

        for key in self.dep_mult_list_adj.keys():
            self.dep_mult_list_adj[key].estimate()

    def estimate_stop(self):
        for key in self.stop_mult_list.keys():
            dep_total = 0

            if(key in self.dep_mult_list_adj):
                dep_total = self.dep_mult_list_adj[key].total

            self.stop_mult_list[key].estimate(dep_total)

        #A key might not be found in stop, but might have cont.
        # In this case, cont =1 and stop =0

        keys = list(set(self.dep_mult_list_adj.keys()) - \
                 set(self.stop_mult_list.keys()))

        for key in keys:
            self.stop_mult_list[key] = StopContMultinomial()
            self.stop_mult_list[key].inc_counts(key, 0)
            self.stop_mult_list[key].\
                estimate(self.dep_mult_list_adj[key].total)
