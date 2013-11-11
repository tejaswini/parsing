import pprint
import cPickle as pickle

class PickleHandler:

    def __init__(self,file_name,):
        self.file_name = file_name
        
    def write_to_pickle(self,dep,cont,stop):
		with open(self.file_name, "wb") as fp:
			pickle.dump(dep,fp)
			pickle.dump(cont,fp)
			pickle.dump(stop,fp)

    def init_all_dicts(self):
        with open(self.file_name, "rb") as fp:
            dep = pickle.load(fp)
            cont = pickle.load(fp)
            stop = pickle.load(fp)

        return dep, cont, stop

if __name__ == "__main__":
   pickle_handler = PickleHandler("data/initial_values")
   dep,cont,stop = pickle_handler.init_all_dicts("data/initial_values")
   pprint.pprint(dep)

