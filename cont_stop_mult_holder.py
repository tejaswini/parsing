from dep_multinomial import DepMultinomial
from cont_stop_multinomial import StopContMultinomial
from memory_profiler import profile
import pprint

class ContStopMultHolder:

    def __init__(self):
        self.cont_stop_mult_list = {}

    def inc_stop_counts(self, instance, counts):
        if(instance not in self.cont_stop_mult_list):
            self.cont_stop_mult_list[instance] = StopContMultinomial()
        self.cont_stop_mult_list[instance].\
            inc_stop_counts(instance, counts)

    def inc_cont_counts(self, instance, counts):
        if(instance not in self.cont_stop_mult_list):
            self.cont_stop_mult_list[instance] = StopContMultinomial()
        self.cont_stop_mult_list[instance].\
            inc_cont_counts(instance, counts)

    def estimate(self):
        for key in self.cont_stop_mult_list.keys():
            self.cont_stop_mult_list[key].estimate()
