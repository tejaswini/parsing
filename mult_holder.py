from multinomial import Multinomial

class MultinomialHolder:

    def __init__(self):
        self.mult_list = {}

    def inc_counts(self, count_type, instance, cond_key, counts):
        if(cond_key not in self.mult_list):
            self.mult_list[cond_key] = Multinomial()

        self.mult_list[cond_key].inc_counts(count_type, instance,
                                            counts)

    def estimate(self):
        for key in self.mult_list.keys():
            self.mult_list[key].estimate()
