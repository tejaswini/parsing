import pprint
import cPickle as pickle

class InsideAlgo:
    def __init__(self,sentence):
        self.lconstit = {}
        self.rconstit = {}
        self.lconstit2 = {}
        self.rconstit2 = {}
        self.rtrap = {}
        self.combinations_rtrap = {}
        self.combinations_ltrap = {}
        self.combinations_rconstit = {}
        self.combinations_lconstit = {}
        self.combinations_rconstit2 = {}
        self.combinations_lconstit2 = {}
        self.ltrap = {}
        self.sentence = sentence
        self.words = self.sentence.split(" ")
        self.dep = {}
        self.cont = {}
        self.stop = {}
        self.init_all_dicts()
        
    def calculate_inside_prob(self,start_index,end_index):
        
        self.initialize_constit(start_index,end_index)
        for s in range(start_index,end_index):
            for t in range(s+1,end_index+1):
                for r in range(s,t):

                    is_adj = self.is_adjacent(s,t)

                    if((str(t),str(r+1)) in self.lconstit2 \
                           and (str(s),str(r)) in self.rconstit):
                        self.rtrap[str(s),str(t)] = self.rconstit[str(s),str(r)] * self.lconstit2[str(t),str(r+1)] * self.dep[self.words[s],self.words[t],"right",is_adj] * self.cont[self.words[s],"right",is_adj]

                        self.add_combination(self.combinations_rtrap,(str(s),str(t)),str(s) + "," + str(r) + "," + str(t))


                    if((str(t),str(r+1)) in self.lconstit and (str(s),str(r))  in self.rconstit2):
                        self.ltrap[str(t),str(s)] = self.rconstit2[str(s),str(r)] * self.lconstit[str(t),str(r+1)] * self.dep[self.words[t],self.words[s],"left",is_adj] * self.cont[self.words[t],"left",is_adj]
                        self.add_combination(self.combinations_ltrap,(str(t),str(s)),str(t) + "," + str(r) + "," + str(s))

                    if((str(r),str(s)) in self.lconstit2 and (str(t),str(r))  in self.ltrap):
                        self.lconstit[str(t),str(s)] = self.ltrap[str(t),str(r)] * self.lconstit2[str(r),str(s)]
                        self.lconstit2[str(t),str(s)] = self.lconstit[str(t),str(s)] * self.stop[self.words[t],"left",self.is_adjacent(s,t)]

                        self.add_combination(self.combinations_lconstit,(str(t),str(s)),str(t) + "," + str(r) + "," + str(s))
                        self.add_combination(self.combinations_lconstit2,(str(t),str(s)),str(t) + "," + str(s))

                        
                    if((str(t),str(s)) in self.ltrap and (str(s),str(s)) in self.lconstit2):
                        self.lconstit[str(t),str(s)] = self.ltrap[str(t),str(s)] * self.lconstit2[str(s),str(s)]
                        self.lconstit2[str(t),str(s)] = self.lconstit[str(t),str(s)] * self.stop[self.words[t],"left",self.is_adjacent(s,t)]

                        self.add_combination(self.combinations_lconstit,(str(t),str(s)),str(t) + "," + str(s) + "," + str(s))
                        self.add_combination(self.combinations_lconstit2,(str(t),str(s)),str(t) + "," + str(s))

                    
                    #This is for s<=r<t condition
                    if(s!=r and (str(s),str(r)) in self.rtrap and (str(r),str(t)) in self.rconstit2):
                        self.rconstit[str(s),str(t)] = self.rtrap[str(s),str(r)] * self.rconstit2[str(r),str(t)]
                        self.rconstit2[str(s),str(t)] = self.rconstit[str(s),str(t)] * self.stop[self.words[s],"right",self.is_adjacent(s,t)]

                        self.add_combination(self.combinations_rconstit,(str(s),str(t)),str(s) + "," + str(r) + "," + str(t))
                        self.add_combination(self.combinations_rconstit2,(str(s),str(t)),str(s) + "," + str(t))

                    
                #This is for  s<r<=t condition
                if((str(s),str(t)) in self.rtrap and (str(t),str(t)) in self.rconstit2):
                        self.rconstit[str(s),str(t)] = self.rtrap[str(s),str(t)] * self.rconstit[str(t),str(t)]
                        self.rconstit2[str(s),str(t)] = self.rconstit[str(s),str(t)] * self.stop[self.words[s],"right",self.is_adjacent(s,t)]

                        self.add_combination(self.combinations_rconstit,(str(s),str(t)),str(s) + "," + str(t) + "," + str(t))
                        self.add_combination(self.combinations_rconstit2,(str(s),str(t)),str(s) + "," + str(t))

                

    def is_adjacent(self,term_beg,term_end):
        return "adj" if (term_beg == term_end) else "non-adj"

    def init_all_dicts(self):
        with open("data/initial_values","rb") as fp:
             self.dep = pickle.load(fp)
             self.cont = pickle.load(fp)
             self.stop = pickle.load(fp)
 
    def initialize_constit(self,start_index,end_index):
        for i in range(start_index,end_index+1):
            self.lconstit[str(i),str(i)] = 0.5
            self.rconstit[str(i),str(i)] = 0.5
            self.lconstit2[str(i),str(i)] = self.lconstit[str(i),str(i)] * self.stop[self.words[i],"left","adj"]
            self.rconstit2[str(i),str(i)] = self.rconstit[str(i),str(i)] * self.stop[self.words[i],"right","adj"]

    def add_combination(self,comb_dict,key,value):
        combinations = []
        if(key in comb_dict):
            combinations = comb_dict[key]
        if(value not in combinations):
            combinations.append(value)
        comb_dict[key] = combinations

    def select_root(self):
        for root in range(0,len(self.words)):
            print "root is " + str(root)
            self.run_algo(0,root)
            self.run_algo(root,len(self.words)-1)

    def run_algo(self,start_index,end_index):
        max_length = (end_index - start_index + 1)
        for length in range(1,max_length):
            max_i = end_index-length + 1
            for i in range(start_index,max_i):
                self.calculate_inside_prob(i,i+length)
                
#        print "rconstit" 
#        pprint.pprint(self.rconstit)
        print "rconstit combinations"
        pprint.pprint(self.combinations_rconstit)
#        print "rconstit2" 
#        pprint.pprint(self.rconstit2)
        print "rconstit2 combinations"
        pprint.pprint(self.combinations_rconstit2)
#        print "rtrap" 
#        pprint.pprint(self.rtrap)
        print "rtrap combinations"
        pprint.pprint(self.combinations_rtrap)
#        print "lconstit" 
#        pprint.pprint(self.lconstit)
        print "lconstit combinations"
        pprint.pprint(self.combinations_rtrap)

        #pprint.pprint(self.lconstit2)
        print "lconstit2 combinations" 
        pprint.pprint(self.combinations_lconstit2)
        
        # print "ltrap" 
        # pprint.pprint(self.ltrap)

        print "ltrap combinations" 
        pprint.pprint(self.combinations_ltrap)

            
            
        


insidealgo = InsideAlgo("A B C D E F")
insidealgo.select_root()
#insidealgo.run_algo(0,2)
#insidealgo.run_algo(2,4)
#E F G H")
#insidealgo.calculate_inside_prob(0,1)
#insidealgo = InsideAlgo("A B C D E F G H")
#insidealgo.calculate_inside_prob(4,7)
