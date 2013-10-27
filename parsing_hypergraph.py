import pydecode.hyper as ph
import pydecode.display as display
from collections import namedtuple, defaultdict
import random
import pydecode.chart as chart
import cPickle as pickle
import pprint

random.seed(0)
Tri = "tri"
Trap = "trap"
Right = "right"
Left = "left"

def init_all_dicts():
    with open("data/initial_values","rb") as fp:
        dep = pickle.load(fp)
        cont = pickle.load(fp)
        stop = pickle.load(fp)

    return dep,cont,stop

dep,cont,stop = init_all_dicts()

class NodeType(namedtuple("NodeType", ["type", "dir", "span"])):
    def __str__(self):
        return "%s %s %d-%d"%(self.type, self.dir, self.span[0], self.span[1])

class Arc(namedtuple("Arc", ["head_word", "modifier_word","dir","is_adj","is_cont"])):
    def __str__(self):
        return "%s %s %s %s %d"%(self.head_word, self.modifier_word, self.dir, self.is_adj, self.is_cont)

def first_order(sentence, c):
    tokens = sentence.split()
    n = len(tokens)

    # Add terminal nodes.
    [c.init(NodeType(sh, d, (s, s)))
     for s in range(n)
     for d in [Right, Left]
     for sh in [Trap, Tri]]

    for k in range(1, n):
        for s in range(n):
            t = k + s
            if t >= n: break
            span = (s, t)

            # First create incomplete items.
            c[NodeType(Trap, Left, span)] = \
                c.sum([c[NodeType(Tri, Right, (s, r))] * c[NodeType(Tri, Left, (r+1, t))] * \
                   c.sr(Arc(tokens[t], tokens[s], Left, is_adj(t,s),1)) \
                       for r in range(s, t)])

            c[NodeType(Trap, Right, span)] = \
                c.sum([c[NodeType(Tri, Right, (s, r))] * c[NodeType(Tri, Left, (r+1, t))] \
                   * c.sr(Arc(tokens[s], tokens[t], Right, is_adj(t,s),1)) \
                         for r in range(s, t)])

            # Second create complete items.
            c[NodeType(Tri, Left, span)] = \
                c.sum([c[NodeType(Tri, Left, (s, r))] * \
                       c[NodeType(Trap, Left, (r, t))] * \
                c.sr(Arc(tokens[s], tokens[t], Right, is_adj(t,s),1)) \
                       for r in range(s, t)])

            c[NodeType(Tri, Right, span)] = \
                c.sum([c[NodeType(Trap, Right, (s, r))] * \
                     c[NodeType(Tri, Right, (r, t))] * \
                c.sr(Arc(tokens[s], tokens[t], Right, is_adj(t,s),1)) \
                      for r in range(s + 1, t + 1)])
    return c

def build_weights(arc):
    print "arc is"
    pprint.pprint(arc)
    if(arc.is_cont and arc.modifier_word!=''):
      return dep[arc.head_word,arc.modifier_word,arc.dir,arc.is_adj] * \
          cont[arc.head_word,arc.dir,arc.is_adj]
    # When head words is not empty, it means constit2
    elif(arc.is_cont==0):
        return stop[arc.head_word,arc.dir,arc.is_adj]
    # When the tuple does not have any values, it means trap to constit
    else:
      return 1 

def is_adj(pos1,pos2):
  return "adj" if abs(pos2-pos1)==1 else "non-adj"
                      
sentence  = "A B C"
c = chart.ChartBuilder(lambda a: a,
                       chart.HypergraphSemiRing,
                       build_hypergraph = True)
the_chart = first_order(sentence, c)
hypergraph = the_chart.finish()

weights = ph.Weights(hypergraph).build(build_weights)
max_marginals = ph.compute_max_marginals(hypergraph, weights)

for edge in hypergraph.edges:
    label = hypergraph.label(edge)
    print hypergraph.label(edge), build_weights(label)
    print max_marginals[edge]

print "nodes"

for node in hypergraph.nodes:
        print max_marginals[node]


