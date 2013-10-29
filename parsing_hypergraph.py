import pydecode.hyper as ph
import pydecode.display as display
from collections import namedtuple, defaultdict
import random
import pydecode.chart as chart
import cPickle as pickle
import pprint

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


class Parsing:

    def __init__(self, sentence, file_name):
        self.dep, self.cont, self.stop = \
            self.init_all_dicts("data/initial_values")
        self.Tri = "tri"
        self.Trap = "trap"
        self.TriStop = "triStop"
        self.Right = "right"
        self.Left = "left"
        self.c = chart.ChartBuilder(
                       lambda a: a, chart.HypergraphSemiRing,
                       build_hypergraph=True)

        self.words = sentence.split()
        self.hypergraph = None
        self.weights = None

    def init_all_dicts(self, file_name):
        with open(file_name, "rb") as fp:
            dep = pickle.load(fp)
            cont = pickle.load(fp)
            stop = pickle.load(fp)

        return dep, cont, stop

    def first_order(self):
        n = len(self.words)
    # Add terminal nodes.
        [self.c.init(NodeType(sh, d, (s, s)))
        for s in range(n)
        for d in [self.Right, self.Left]
        for sh in [self.Trap, self.Tri]]

        for k in range(1, n):
            for s in range(n):
                t = k + s
                if t >= n:
                    break
                span = (s, t)

            # First create incomplete items.
                self.c[NodeType(self.Trap, self.Left, span)] = \
                 self.c.sum(
                 [self.c[NodeType(self.Tri, self.Right, (s, r))] *
                 self.c[NodeType(self.Tri, self.Left, (r+1, t))] *
                 self.c.sr(Arc(self.words[t], self.words[s], self.Left,
                 self.is_adj(t, s),1)) for r in range(s, t)])

                self.c[NodeType(self.Trap, self.Right, span)] = \
                   self.c.sum(
                   [self.c[NodeType(self.Tri, self.Right, (s, r))] *
                   self.c[NodeType(self.Tri, self.Left, (r+1, t))] *
                   self.c.sr(Arc(self.words[s], self.words[t],
                   self.Right, self.is_adj(t, s),1))
                   for r in range(s, t)])

            # Second create complete items.
                self.c[NodeType(self.Tri, self.Left, span)] = \
                       self.c.sum([self.c[NodeType(self.Tri,
                       self.Left, (s, r))] *
                       self.c[NodeType(self.Trap, self.Left, (r, t))] *
                       self.c.sr(Arc(self.words[t], "", self.Left,
                       self.is_adj(t, s), 1)) for r in range(s, t)])

                self.c[NodeType(self.Tri, self.Right, span)] = \
                     self.c.sum([self.c[NodeType(self.Trap,
                           self.Right, (s, r))] *
                           self.c[NodeType(self.Tri, self.Right,
                                           (r, t))] *
                           self.c.sr(Arc(self.words[s], "", self.Right,
                           self.is_adj(t, s), 1))
                           for r in range(s + 1, t + 1)])
        return self.c        

    def get_hypergraph(self):
        if(not self.c._done):
            self.first_order()
            self.hypergraph = self.c.finish()
        return self.hypergraph

    def get_weights(self):
        self.get_hypergraph()
        return ph.Weights(self.hypergraph).build(self.build_weights)

    def get_marginals(self):
        weights = self.get_weights()
        print "got weights"
        return ph.compute_max_marginals(self.hypergraph, weights)

    def build_weights(self, arc):
        if(arc.is_cont and arc.modifier_word!=''):
            return self.dep[arc.head_word, arc.modifier_word, arc.dir, arc.is_adj] \
                * self.cont[arc.head_word, arc.dir, arc.is_adj]
    # When head words is not empty, it means constit2
        elif(arc.is_cont == 0):
            return self.stop[arc.head_word, arc.dir, arc.is_adj]
    # When the tuple does not have any values, it means trap to constit
        else:
            return 0

    def display(self):
        max_marginals = self.get_marginals()
        for edge in self.hypergraph.edges:
            label = self.hypergraph.label(edge)
            print self.hypergraph.label(edge), self.build_weights(label)
            print max_marginals[edge]

        print "nodes"

        for node in self.hypergraph.nodes:
            print max_marginals[node]

    def is_adj(self, pos1, pos2):
        return "adj" if abs(pos2-pos1) == 1 else "non-adj"

sentence = "A B C"
parsing = Parsing(sentence, "data/initial_values")
parsing.display()
#parsing.em_algorithm()
