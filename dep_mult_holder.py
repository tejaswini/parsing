from dep_multinomial import DepMultinomial
from cont_stop_multinomial import StopContMultinomial
from memory_profiler import profile
import pprint

class DepMultinomialHolder:

    def __init__(self):
        self.dep_mult_list = {}

    def inc_counts(self, instance, cond_key, counts):
        if(cond_key not in self.dep_mult_list):
            self.dep_mult_list[cond_key] = DepMultinomial()

        self.dep_mult_list[cond_key].inc_counts(instance, counts)

    def estimate(self):
        for key in self.dep_mult_list.keys():
            self.dep_mult_list[key].estimate()
