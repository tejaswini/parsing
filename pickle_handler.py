import pprint
import cPickle as pickle

class PickleHandler:

    def __init__(self,file_name):
        self.file_name = file_name
        
    def write_to_pickle(self, dep_mult_list, stop_cont_mult_list, file_name):
		with open(file_name, "wb") as fp:
			pickle.dump(dep_mult_list, fp)
			pickle.dump(stop_cont_mult_list, fp)

    def write_prob_to_pickle(self, prob, file_name):
		with open(file_name, "wb") as fp:
			pickle.dump(prob, fp)

    def read_prob(self, file_name):
        with open(file_name, "rb") as fp:
            return pickle.load(fp)

    def init_all_dicts(self):
        with open(self.file_name, "rb") as fp:
            dep_mult = pickle.load(fp)
            stop_cont_mult = pickle.load(fp)

        return dep_mult, stop_cont_mult

if __name__ == "__main__":
   pickle_handler = PickleHandler("data/harmonic_values_numpy")
   dep,cont_stop = pickle_handler.init_all_dicts()
