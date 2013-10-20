import pprint
import pydecode.hyper as ph
import pydecode.display as display

c = {}
comb = {}
nodes = {}
hyper1 = ph.Hypergraph()
def eisners_algo(sentence):
    n = len(sentence.split(" "))
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
                edges = [([nodes[s,r,'right',1],nodes[r+1,t,'left',1]],convert_to_string([s,r,'right',1])) for r in range(s,t)]
                nodes[s,t,'left',0] = b.add_node(edges, label=convert_to_string([s,t,'left',0]))
                c[s,t,'right',0] = max([c[s,r,'right',1] + c[r + 1,t,'left',1] for r in range(s,t)])
                edges = [([nodes[s,r,'right',1],nodes[r+1,t,'left',1]],convert_to_string([s,r,'left',1])) for r in range(s,t)]
                nodes[s,t,'right',0] = b.add_node([([nodes[s,r,'right',1],nodes[r+1,t,'left',1]],convert_to_string([s,r,'right',1])) for r in range(s,t)], label=convert_to_string([s,t,'right',0]))

           # Second: create complete items
                c[s,t,'left',1] = max([c[s,r,'left',1] + c[r,t,'left',0] for r in range(s,t)])
                edges = [([nodes[s,r,'left',1],nodes[r,t,'left',0]],convert_to_string([s,r,'left',1])) for r in range(s,t)]
                nodes[s,t,'left',1] = b.add_node(edges,label=convert_to_string([s,t,'left',1]))
                c[s,t,'right',1] = max([c[s,r,'right',0] + c[r,t,'right',1] for r in range(s+1,t+1)])
                edges = [([nodes[s,r,'right',0],nodes[r,t,'right',1]],convert_to_string([s,r,'right',0])) for r in range(s+1,t+1)]
                nodes[s,t,'right',1] = b.add_node(edges,label=convert_to_string([s,t,'right',1]))
            

def convert_to_string(array):
   return  ",".join(map(str,array))

def is_adj(pos1,pos2):
   0 if pos2-pos1==1 else  1

def build_weights(label):
    head_word,modifier,direct,is_adj,is_cont=label 
    if(is_cont):
      return dep[head_word,modifier,direct,is_adj] * cont[head_word,is_adj]
    # When head word is not empty, it means constit2
    elif(head_word!=''):
        return stop[head_word,is_adj]
    # When the tuple does not have any values, it means trap to constit
    else:
      return 1 
        

eisners_algo("The dog barked")
pprint.pprint(c)    
pprint.pprint(hyper1.edges())
display.to_ipython(hyper1)
