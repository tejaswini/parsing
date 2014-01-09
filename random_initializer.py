from pickle_handler import PickleHandler
import pprint
import random
from collections import defaultdict
from mult_holder import MultinomialHolder

class RandomInitializer:
    def __init__(self, dep_mult, stop_cont_mult):
        self.harmonic_dep_mult = dep_mult
        self.harmonic_stop_cont_mult = stop_cont_mult
        self.dep_mult_holder = MultinomialHolder()
        self.stop_cont_mult_holder = MultinomialHolder()

    def initialize_multinomials(self):
        self.initialize_dep()
        self.initialize_stop_mult_cont()
        total =  sum(self.dep_mult_holder.mult_list['VBZ', 'left'].prob.values())
        assert round(total,1) == 1.0, "sum is "+ str(total)
        total =  sum(self.dep_mult_holder.mult_list['NN', 'left'].prob.values())
        assert round(total,1) == 1.0, "sum is "+ str(total)

        
    def initialize_dep(self):
        for cond_key, mult in self.harmonic_dep_mult.iteritems():
            for prob_key in mult.prob:
                self.dep_mult_holder.\
                    inc_counts(prob_key, cond_key, random.random())

        self.dep_mult_holder.estimate()
        

    def initialize_stop_mult_cont(self):
        for cond_key, mult in self.harmonic_stop_cont_mult.iteritems():
            random_value = random.random()
            self.stop_cont_mult_holder.\
                    inc_counts(0, cond_key,random_value)
            self.stop_cont_mult_holder.\
                    inc_counts(1, cond_key,1 - random_value)

        self.stop_cont_mult_holder.estimate()

if __name__ == "__main__":
    pickle_handler = PickleHandler("data/dummy")
    dep_mult, stop_cont_mult = pickle_handler.init_all_dicts()
    random_init = RandomInitializer(dep_mult, stop_cont_mult)
    random_init.initialize_multinomials()
    pickle_handler = PickleHandler("data/randominit")
    pickle_handler.write_to_pickle(random_init.dep_mult_holder.mult_list, random_init.stop_cont_mult_holder.mult_list)
