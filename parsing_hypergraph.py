import pprint
import pydecode.hyper as ph
import pydecode.display as display
import cPickle as pickle


c = {}
comb = {}
nodes = {}
hyper1 = ph.Hypergraph()

def init_all_dicts():
    with open("data/initial_values","rb") as fp:
        dep = pickle.load(fp)
        cont = pickle.load(fp)
        stop = pickle.load(fp)

    return dep,cont,stop

dep,cont,stop = init_all_dicts()

pprint.pprint(dep)
pprint.pprint(cont)
pprint.pprint(stop)

def eisners_algo(sentence):
    words = sentence.split(" ")
    n = len(words)
    with hyper1.builder() as b:
        for s in xrange(n):
            c[s,s,'right',1] = c[s,s,'left',1] = 0.5
            nodes[s,s,'right',1] = b.add_node(label = convert_to_string([s,s,'right',1]))
            nodes[s,s,'left',1] = b.add_node(label = convert_to_string([s,s,'left',1]))

        for k in range(1,n+1):
            for s in xrange(n):
                t=s+k
                if t >= n:
                    continue
                print "s is" + str(s) + " t is " + str(t)
                # First: create incomplete items
                c[s,t,'left',0] =  max([c[s,r, 'right', 1] + c[r+1,t,'left',1] for r in range(s,t)])
                edges = [([nodes[s,r,'right',1],nodes[r+1,t,'left',1]],(words[t],words[s],'left',is_adj(t,s),1)) for r in range(s,t)]
                nodes[s,t,'left',0] = b.add_node(edges, label=convert_to_string([s,t,'left',0]))
                
                c[s,t,'right',0] = max([c[s,r,'right',1] + c[r + 1,t,'left',1] for r in range(s,t)])
                edges = [([nodes[s,r,'right',1],nodes[r+1,t,'left',1]],(words[s],words[t],'right',is_adj(s,t),1)) for r in range(s,t)]
                nodes[s,t,'right',0] = b.add_node(edges, label=convert_to_string([s,t,'right',0]))

                # Second: create complete items
                c[s,t,'left',1] = max([c[s,r,'left',1] + c[r,t,'left',0] for r in range(s,t)])
                edges = [([nodes[s,r,'left',1],nodes[r,t,'left',0]],(words[t],words[s],'left',is_adj(t,s),1)) for r in range(s,t)]
                nodes[s,t,'left',1] = b.add_node(edges,label=convert_to_string([s,t,'left',1]))
                
                c[s,t,'right',1] = max([c[s,r,'right',0] + c[r,t,'right',1] for r in range(s+1,t+1)])
                edges = [([nodes[s,r,'right',0],nodes[r,t,'right',1]],(words[s],words[t],'right',is_adj(s,t),1)) for r in range(s+1,t+1)]
                nodes[s,t,'right',1] = b.add_node(edges,label=convert_to_string([s,t,'right',1]))

                c[s,t,'left',2] = c[s,t,'left',1]
                edges = [([nodes[s,r,'left',1]],(words[t],'','left',is_adj(t,s),1)) for r in range(s,t)]
                nodes[s,t,'left',2] = b.add_node(edges,label=convert_to_string([s,t,'left',2]))
                
                c[s,t,'right',2] = c[s,t,'right',1]
                edges = [([nodes[s,r,'right',1]],(words[s],'','right',is_adj(s,t),1)) for r in range(s+1,t+1)]
                nodes[s,t,'right',2] = b.add_node(edges,label=convert_to_string([s,t,'right',2]))

            

def convert_to_string(array):
   return  ",".join(map(str,array))

def is_adj(pos1,pos2):
  return "adj" if pos2-pos1==1 else "non-adj"

def build_weights(label):
    head_word,modifier,direct,is_adj,is_cont=label 
    if(is_cont and modifier!=''):
      pprint.pprint(label)
      return dep[head_word,modifier,direct,is_adj] * cont[head_word,direct,is_adj]
    # When head words is not empty, it means constit2
    elif(is_cont==0):
        return stop[head_word,direct,is_adj]
    # When the tuple does not have any values, it means trap to constit
    else:
      return 1 
        
#eisners_algo("The dog barked")
eisners_algo("A B C")
pprint.pprint(c)    
pprint.pprint(hyper1.edges())
weights = ph.Weights(hyper1,build_weights)
path,chart = ph.best_path(hyper1, weights)


best = weights.dot(path)


for edge in hyper1.edges():
    label = hyper1.label(edge)
    print hyper1.label(edge), build_weights(label)

display.to_ipython(hyper1)
