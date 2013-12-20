from multinomial import Multinomial
import pprint

class MultinomialHolder:

    def __init__(self):
        self.mult_list = {}

    def inc_counts(self, instance, cond_key, counts):
        if(cond_key not in self.mult_list):
            multinomial = Multinomial()
            self.mult_list[cond_key] = multinomial
        else:
            self.mult_list[cond_key].inc_counts(instance, counts)

    def estimate(self):
        for key in self.mult_list.keys():
            self.mult_list[key].estimate()
