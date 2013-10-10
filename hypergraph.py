import pprint
import cPickle as pickle
import pydecode.hyper as ph
import pydecode.display as display
import pprint

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
        self.words = sentence.split(" ")
        self.dep = {}
        self.cont = {}
        self.stop = {}
        self.init_all_dicts()
        self.nodes = {}
        self.hypergraph = ph.Hypergraph()
        self.b = self.hypergraph.builder()

        
    def calculate_inside_prob(self,start_index,end_index):
        
       # self.initialize_constit(start_index,end_index)
        for s in range(start_index,end_index):
            for t in range(s+1,end_index+1):
                combinations = {}
                for r in range(s,t):
                    is_adj = self.is_adjacent(s,t)

                    if((t,r+1) in self.lconstit2 and (s,r) in self.rconstit):
                        self.rtrap[s,t] = self.rconstit[s,r] * self.lconstit2[t,r+1] * self.dep[self.words[s],self.words[t],"right",is_adj] * self.cont[self.words[s],"right",is_adj]
                        self.add_combination_to_node(("rtrap",s,t),combinations,[("rconstit",s,r),("lconstit2",t,r+1)])
                        self.add_combination(self.combinations_rtrap,(s,t),str(s) + "," + str(r) + "," + str(t))


                    if((t,r+1) in self.lconstit and (s,r)  in self.rconstit2):
                        self.ltrap[t,s] = self.rconstit2[s,r] * self.lconstit[t,r+1] * self.dep[self.words[t],self.words[s],"left",is_adj] * self.cont[self.words[t],"left",is_adj]
                        self.add_combination_to_node(("ltrap",t,s),combinations,[("lconstit",t,r+1),("rconstit2",s,r)])
                        self.add_combination(self.combinations_ltrap,(t,s),str(t) + "," + str(r) + "," + str(s))

                    if((r,s) in self.lconstit2 and (t,r)  in self.ltrap):
                        self.lconstit[t,s] = self.ltrap[t,r] * self.lconstit2[r,s]
                        self.lconstit2[t,s] = self.lconstit[t,s] * self.stop[self.words[t],"left",self.is_adjacent(s,t)]

                        self.add_combination_to_node(("lconstit",t,s),combinations,[("ltrap",t,r),("lconstit2",r,s)])
                        self.add_combination_to_node(("lconstit2",t,s),combinations,[("lconstit2",r,s)])

                        self.add_combination(self.combinations_lconstit,(t,s),str(t) + "," + str(r) + "," + str(s))
                        self.add_combination(self.combinations_lconstit2,(t,s),str(t) + "," + str(s))

                        
                    if((t,s) in self.ltrap and (s,s) in self.lconstit2):
                        self.lconstit[t,s] = self.ltrap[t,s] * self.lconstit2[s,s]
                        self.lconstit2[t,s] = self.lconstit[t,s] * self.stop[self.words[t],"left",self.is_adjacent(s,t)]

                        self.add_combination_to_node(("lconstit",t,s),combinations,[("ltrap",t,s),("lconstit2",s,s)])
                        self.add_combination_to_node(("lconstit2",t,s),combinations,[("lconstit",t,s)])

                        self.add_combination(self.combinations_lconstit,(t,s),str(t) + "," + str(s) + "," + str(s))
                        self.add_combination(self.combinations_lconstit2,(t,s),str(t) + "," + str(s))

                    
                    # This is for s<=r<t condition
                    if(s!=r and (s,r) in self.rtrap and (r,t) in self.rconstit2):
                        self.rconstit[s,t] = self.rtrap[s,r] * self.rconstit2[r,t]
                        self.rconstit2[s,t] = self.rconstit[s,t] * self.stop[self.words[s],"right",self.is_adjacent(s,t)]

                        self.add_combination_to_node(("rconstit",s,t),combinations,[("rtrap",s,r),("rconstit2",r,t)])
                        self.add_combination_to_node(("rconstit2",s,t),combinations,[("rconstit",s,t)])

                        self.add_combination(self.combinations_rconstit,(s,t),str(s) + "," + str(r) + "," + str(t))
                        self.add_combination(self.combinations_rconstit2,(s,t),str(s) + "," + str(t))

                    
                # This is for  s<r<=t condition
                if((s,t) in self.rtrap and (t,t) in self.rconstit2):
                        self.rconstit[s,t] = self.rtrap[s,t] * self.rconstit[t,t]
                        self.rconstit2[s,t] = self.rconstit[s,t] * self.stop[self.words[s],"right",self.is_adjacent(s,t)]

                        self.add_combination_to_node(("rconstit",s,t),combinations,[("rtrap",s,t),("rconstit2",t,t)])
                        self.add_combination_to_node(("rconstit2",s,t),combinations,[("rconstit",s,t)])

                        self.add_combination(self.combinations_rconstit,(s,t),str(s) + "," + str(t) + "," + str(t))
                        self.add_combination(self.combinations_rconstit2,(s,t),str(s) + "," + str(t))

            self.create_nodes(combinations,s,t)

    def convert_to_label(self,key):
        label = ""
        for word in key:
            label += str(word) + ","
        return label[0:-1]


    def create_nodes(self,node_list,s,t):
        constit_nodes_list = {}
        node_order = [("ltrap",t,s),("lconstit",t,s),("lconstit2",t,s),("rtrap",s,t),("rconstit",s,t),("rconstit2",s,t)]
        # for key,combinations in node_list.iteritems():
        for key in node_order:
            combinations = node_list[key]
            if(key in self.nodes):
                continue
            tail_nodes = []

            for combination in combinations:            
                tail_node = self.create_tail_nodes(combination)
                if(tail_node != []):
                    tail_nodes.append(tail_node)
            label_text = self.convert_to_label(key)
            print "key is " + label_text
            pprint.pprint(tail_nodes)
            self.nodes[key] = self.b.add_node(tail_nodes,label = label_text)
            print "edges are"
            pprint.pprint(self.nodes[key].edges())

    def create_tail_nodes(self,combination):
        nodes = []
        for node_key in combination:
            if(node_key not in self.nodes):
                print "key " + self.convert_to_label(node_key) + " not found"
                return []
            nodes.append(self.nodes[node_key])
        return (nodes,nodes[0].label())

        
    def is_adjacent(self,term_beg,term_end):
        return "adj" if (term_beg == term_end) else "non-adj"

    def init_all_dicts(self):
        with open("/home/tejaswini/Columbia/hypergraph_code/initial_values","rb") as fp:
             self.dep = pickle.load(fp)
             self.cont = pickle.load(fp)
             self.stop = pickle.load(fp)
 
    def initialize_constit(self,start_index,end_index):
        for i in range(start_index,end_index+1):
            self.lconstit[i,i] = 0.5
            self.rconstit[i,i] = 0.5
            self.lconstit2[i,i] = self.lconstit[i,i] * self.stop[self.words[i],"left","adj"]
            self.add_terminal_node1(("lconstit",i,i))
            self.add_terminal_node1(("lconstit2",i,i))
            self.rconstit2[i,i] = self.rconstit[i,i] * self.stop[self.words[i],"right","adj"]
            self.add_terminal_node1(("rconstit",i,i))
            self.add_terminal_node1(("rconstit2",i,i))


    def add_terminal_node1(self,key):
        label_text = self.convert_to_label(key)
        if(key not in self.nodes):
            label_text = self.convert_to_label(key)
            self.nodes[key] = self.b.add_node(label =label_text)

    def add_combination_to_node(self,key,combinations,value):
        comb = []
        if(key in combinations):
              comb = combinations[key]
        comb.append(value)
        combinations[key] = comb


    def add_combination(self,comb_dict,key,value):
        combinations = []
        if(key in comb_dict):
            combinations = comb_dict[key]
#        if(value not in combinations):
        combinations.append(value)
        comb_dict[key] = combinations


    def run_algo(self,start_index,end_index):
        self.initialize_constit(start_index,end_index)
        max_length = (end_index - start_index + 1)
        for length in range(1,max_length):
            max_i = end_index-length + 1
            for i in range(start_index,max_i):
                self.calculate_inside_prob(i,i+length)
                
        # print "rconstit combinations"
        # pprint.pprint(self.combinations_rconstit)
        # print "rconstit2 combinations"
        # pprint.pprint(self.combinations_rconstit2)
        # print "rtrap combinations"
        # pprint.pprint(self.combinations_rtrap)
        # print "lconstit combinations"
        # pprint.pprint(self.combinations_rtrap)


        # print "lconstit2 combinations" 
        # pprint.pprint(self.combinations_lconstit2)
        
        # print "ltrap combinations" 
        # pprint.pprint(self.combinations_ltrap)
#        pprint.pprint(self.nodes)
#        pprint.pprint(self.nodes['ltrap',2,0].edges())
        # pprint.pprint(self.hypergraph.edges())
        # pprint.pprint(self.hypergraph.nodes())
        print "edges of hypergraph are"
        pprint.pprint(self.hypergraph.edges())
        display.to_ipython(self.hypergraph)
            
            
        


insidealgo = InsideAlgo("A B C D")
insidealgo.run_algo(0,2)

