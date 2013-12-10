import pydecode.hyper as ph
import pydecode.display as display
from collections import namedtuple, defaultdict
import random
import pydecode.chart as chart
import cPickle as pickle
import pprint
from pickle_handler import PickleHandler

class NodeType(namedtuple("NodeType", ["type", "dir", "span"])):

    def __str__(self):
        return "%s %s %d-%d" % (self.type, self.dir, self.span[0],
                                self.span[1])

class Arc(namedtuple(
        "Arc",
        ["head_word", "modifier_word","dir", "is_adj", "is_cont"])):
    def __str__(self):
        return "%s %s %s %s %d" % (
            self.head_word, self.modifier_word,
            self.dir, self.is_adj, self.is_cont)


class DepType(namedtuple("DepType", ["type", "dir", "head_word",
                         "mod_word"])):

    def __str(self):
        return "%s %s %s" % (self.type, self.dir, self.head_word)


class ParsingAlgo:

    def __init__(self, sentence, file_name):
        self.pickle_handler = PickleHandler(file_name)
        self.dep, self.cont, self.stop = \
            self.pickle_handler.init_all_dicts()
        self.Tri = "tri"
        self.Trap = "trap"
        self.TriStop = "triStop"
        self.Right = "right"
        self.Left = "left"
        self.c = chart.ChartBuilder(
                       lambda a: a, chart.HypergraphSemiRing,
                       build_hypergraph=True)

        self.words = ["*"] + sentence.split()
        self.hypergraph = None
        self.potentials = None

    def first_order(self):
        n = len(self.words)
    # Add terminal nodes.
        [self.c.init(NodeType(node_type, d, (s, s)))
        for s in range(n)
        for d in [self.Right, self.Left]
        for node_type in [self.Tri, self.TriStop, self.Trap]]

        for k in range(1, n):
            for s in range(n):
                t = k + s
                if t >= n:
                    break
                span = (s, t)

            # First create incomplete items.
                nodes = []
                for r in range(s,t):
                    if NodeType(self.TriStop, self.Right, (s, r)) \
                      in self.c and NodeType(self.Tri, self.Left,
                      (r+1, t)) in self.c:
                      nodes.append(self.c[NodeType(self.TriStop,
					       self.Right, (s, r))] * \
                 self.c[NodeType(self.Tri, self.Left, (r+1, t))] *
                 self.c.sr(Arc(self.words[t], self.words[s],
                    self.Left, self.is_adj(t, s),1)))

                self.c[NodeType(self.Trap, self.Left, span)] = \
                    self.c.sum(nodes)

                nodes = []
                for r in range(s,t):
                    if NodeType(self.Tri, self.Right, (s, r)) \
                      in self.c and NodeType(self.TriStop, self.Left,
                      (r+1, t)) in self.c:
                         nodes.append(self.c[NodeType(self.Tri,
					       self.Right, (s, r))] * \
                          self.c[NodeType(self.TriStop, self.Left,
					  (r+1, t))] * \
                            self.c.sr(Arc(self.words[s], self.words[t],
                            self.Right, self.is_adj(t, s),1)))

                

                self.c[NodeType(self.Trap, self.Right, span)] = \
                   self.c.sum(nodes)
            # Second create complete items.
                self.c[NodeType(self.Tri, self.Left, span)] = \
                       self.c.sum([self.c[NodeType(self.TriStop,
                       self.Left, (s, r))] *
                       self.c[NodeType(self.Trap, self.Left, (r, t))]\
                       * self.c.sr(Arc(self.words[t], "", self.Left,
                       self.is_adj(t, s), 1)) for r in range(s, t)])

                if (s == 0 and t == n-1) or s!=0:
                    self.c[NodeType(self.Tri, self.Right, span)] = \
                        self.c.sum([self.c[NodeType(self.Trap,
                          self.Right, (s, r))] *
                          self.c[NodeType(self.TriStop, self.Right,
                                           (r, t))] *
                          self.c.sr(Arc(self.words[s], "", self.Right\
                           ,self.is_adj(t, s), 1))
                           for r in range(s + 1, t + 1)])

                self.c[NodeType(self.TriStop, self.Left, span)] = \
                       self.c[NodeType(self.Tri,
                       self.Left, span)] * \
                       self.c.sr(Arc(self.words[t], "", self.Left,
                       self.is_adj(t, s), 0))

                if(NodeType(self.Tri, self.Right, span) in self.c):

                   self.c[NodeType(self.TriStop, self.Right, span)] = \
                          self.c[NodeType(self.Tri, self.Right,
                                           span)] * \
                          self.c.sr(Arc(self.words[s], "", self.Right,
                           self.is_adj(t, s), 0))

        return self.c

    def get_hypergraph(self):
        if(not self.c._done):
            self.first_order()
            self.hypergraph = self.c.finish()
        return self.hypergraph

    def get_potentials(self):
        self.get_hypergraph()
        self.potentials = ph.InsidePotentials(self.hypergraph). \
          build(self.build_potentials)

    def viterbi_potentials(self):
        return ph.ViterbiPotentials(parsing.hypergraph). \
            build(parsing.build_potentials)

    def best_path(self):
        viterbi_potentials = self.viterbi_potentials()
        return ph.best_path(parsing.hypergraph, viterbi_potentials)

    def best_edges(self):
        path = self.best_path()
        best_edges = path.edges
        depen = {}
        print "best path is"
        for edge in best_edges:
            label = str(edge.head.label)
            node_type, direct, span = label.split()
            span_first, span_end = span.split("-")
            print node_type, direct, span_first, span_end
            if node_type == "trap" and direct == "right":
                depen[self.words[int(span_end)], int(span_end)] = \
                    self.words[int(span_first)]
                
            if node_type == "trap" and direct == "left":
                depen[self.words[int(span_first)], int(span_first)] = \
                    self.words[int(span_end)]
        actual_tags = []

        for i,word in enumerate(self.words):
            if (word, i) not in depen:
                actual_tags.append(None)
            else:
                actual_tags.append(depen[word, i])

        pprint.pprint(actual_tags)

    def get_marginals(self):
        if self.potentials== None:
            self.get_potentials()
        marginal_values = \
            ph.compute_marginals(self.hypergraph, self.potentials)
        marginals = {}
        
        root_value = marginal_values[self.hypergraph.root]
        for node in self.hypergraph.nodes:
            marginals[node.label] = marginal_values[node] / root_value

        for edge in self.hypergraph.edges:
           marginals[edge.label] =  marginal_values[edge] / root_value

        return marginals


    def build_potentials(self, arc):
        if(arc.is_cont and arc.modifier_word!=''):
            x =  self.dep[arc.head_word, arc.modifier_word,
                            arc.dir, arc.is_adj] \
                * self.cont[arc.head_word, arc.dir, arc.is_adj]

            assert x > 1.000000123e-300, "%s,%s,%s,%s,%s"%(arc.head_word, arc.modifier_word, arc.dir, self.dep[arc.head_word, arc.modifier_word, arc.dir, arc.is_adj],self.cont[arc.head_word, arc.dir, arc.is_adj])
#            print "cont ", x, arc.head_word, arc.modifier_word, arc.dir
            return x
    # When head words is not empty, it means constit2
        elif(arc.is_cont == 0):
            x = self.stop[arc.head_word, arc.dir, arc.is_adj]

            assert x > 1.000000123e-300, "%s,%s,%s"%(arc.head_word, arc.dir, arc.is_adj)
#            print "stop " , x, arc.head_word, arc.dir
            return x
    # When the tuple does not have any values, 
      #it means trap to constit
        else:
            return 1

    def display(self):
        self.get_hypergraph()
        marginals = self.get_marginals()
#        base = marginals[self.hypergraph.root]
        # for edge in self.hypergraph.edges:
        #     expected_count =  marginals[edge].value / base.value
        #     label = self.hypergraph.label(edge)
        #     print self.hypergraph.label(edge), expected_count

        for node in self.hypergraph.nodes:
            print node.label, marginals[node.label]

#        self.c.show()

    def get_node(self, node_name):
        nodes = self.hypergraph.nodes
        node = filter(lambda x:node_name in x.label , nodes)
        return node

    def is_adj(self, pos1, pos2):
        return "adj" if abs(pos2-pos1) == 1 else "non-adj"

if __name__ == "__main__":
    sentence = "NNS JJ DT RB VBP RP NNP NN"
#    sentence =  "A B C E F G"
#    parsing = ParsingAlgo(sentence, "data/initial_values")
    parsing = ParsingAlgo(sentence, "tmp") #"data/harmonic_values")
    parsing.get_hypergraph()
    parsing.display()
#    display.HypergraphFormatter(parsing.hypergraph).to_ipython()
    best = parsing.best_path()
    print sentence
    parsing.best_edges()
    
