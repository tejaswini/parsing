from pickle_handler import PickleHandler
import pprint
import random
from collections import defaultdict
from mult_holder import MultinomialHolder

class RandomInitializer:
    def __init__(self, dep_mult, stop_cont_mult):
        self.harmonic_dep_mult = dep_mult
        self.harmonic_stop_cont_mult = stop_cont_mult

    def initialize_multinomials(self):
        dep_mult_holder = self.initialize_dep()
        stop_cont_mult_holder = self.initialize_stop_mult_cont()
        return dep_mult_holder, stop_cont_mult_holder
        
    def initialize_dep(self):
        dep_mult_holder = MultinomialHolder()
        for cond_key, mult in self.harmonic_dep_mult.iteritems():
            for prob_key in mult.prob:
                dep_mult_holder.\
                    inc_counts(prob_key, cond_key, random.random())

        dep_mult_holder.estimate()
        return dep_mult_holder

    def initialize_stop_mult_cont(self):
        stop_cont_mult_holder = MultinomialHolder()
        for cond_key, mult in self.harmonic_stop_cont_mult.iteritems():
            random_value = random.random()
            stop_cont_mult_holder.\
                    inc_counts(0, cond_key,random_value)
            stop_cont_mult_holder.\
                    inc_counts(1, cond_key,1 - random_value)

        stop_cont_mult_holder.estimate()
        return stop_cont_mult_holder

if __name__ == "__main__":
    pickle_handler = PickleHandler("data/dummy")
    dep_mult, stop_cont_mult = pickle_handler.init_all_dicts()
    random_init = RandomInitializer(dep_mult, stop_cont_mult)
    random_init.initialize_multinomials()
    pickle_handler = PickleHandler("data/random_init")
    pickle_handler.write_to_pickle(random_init.dep_mult_holder.\
          mult_list, random_init.stop_cont_mult_holder.mult_list)
