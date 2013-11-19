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
#                print span

            # First create incomplete items.
                self.c[NodeType(self.Trap, self.Left, span)] = \
                 self.c.sum(
                 [self.c[NodeType(self.TriStop, self.Right, (s, r))] *
                 self.c[NodeType(self.Tri, self.Left, (r+1, t))] *
                 self.c.sr(Arc(self.words[t], self.words[s],
                    self.Left, self.is_adj(t, s),1))\
                      for r in range(s, t)])


                self.c[NodeType(self.Trap, self.Right, span)] = \
                   self.c.sum(
                   [self.c[NodeType(self.Tri, self.Right, (s, r))] *
                  self.c[NodeType(self.TriStop, self.Left, (r+1, t))] *
                   self.c.sr(Arc(self.words[s], self.words[t],
                   self.Right, self.is_adj(t, s),1))
                   for r in range(s, t)])

                if(span[0] == 0 and span[1] == 1):
                   pprint.pprint(self.c[NodeType(self.Trap, self.Right, span)])
               
            # Second create complete items.
                self.c[NodeType(self.Tri, self.Left, span)] = \
                       self.c.sum([self.c[NodeType(self.TriStop,
                       self.Left, (s, r))] *
                       self.c[NodeType(self.Trap, self.Left, (r, t))]\
                       * self.c.sr(Arc(self.words[t], "", self.Left,
                       self.is_adj(t, s), 1)) for r in range(s, t)])

                if (s == 0 and t == n) or s!=0:
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

    def get_weights(self):
        self.get_hypergraph()
        self.weights = ph.InsideWeights(self.hypergraph).\
          build(self.build_weights)

    def viterbi_weights(self):
        return ph.ViterbiWeights(parsing.hypergraph).\
            build(parsing.build_weights)

    def best_path(self):
        viterbi_weights = self.viterbi_weights()
        return ph.best_path(parsing.hypergraph, viterbi_weights)

    def best_edges(self):
        path = self.best_path()
        best_edges = path.edges
        depen = {}
        print "best path is"
        for edge in best_edges:
            node_type, direct, span =  edge.head.label.split()
            span_first, span_end = span.split("-")
            print node_type, direct, span_first, span_end
            if node_type == "trap" and direct == "right":
                depen[self.words[int(span_end)]] = \
                    self.words[int(span_first)]
                
            if node_type == "trap" and direct == "left":
                depen[self.words[int(span_first)]] = \
                    self.words[int(span_end)]


        pprint.pprint(depen)

        actual_tags = []

        for word in self.words:
            if word not in depen:
                actual_tags.append(None)
            else:
                actual_tags.append(depen[word])

        pprint.pprint(actual_tags)

    def get_marginals(self):
        if self.weights== None:
            self.get_weights()
        return ph.compute_marginals(self.hypergraph, self.weights)

    def build_weights(self, arc):
        if(arc.is_cont and arc.modifier_word!=''):
            return self.dep[arc.head_word, arc.modifier_word,
                            arc.dir, arc.is_adj] \
                * self.cont[arc.head_word, arc.dir, arc.is_adj]
    # When head words is not empty, it means constit2
        elif(arc.is_cont == 0):
            return self.stop[arc.head_word, arc.dir, arc.is_adj]
    # When the tuple does not have any values, 
      #it means trap to constit
        else:
            return 1

    def display(self):
        self.get_hypergraph()
        marginals = self.get_marginals()
        base = marginals[self.hypergraph.root]
        # for edge in self.hypergraph.edges:
        #     expected_count =  marginals[edge].value / base.value
        #     label = self.hypergraph.label(edge)
        #     print self.hypergraph.label(edge), expected_count

        for node in self.hypergraph.nodes:
            print node.label, marginals[node].value

    def get_node(self, node_name):
        nodes = self.hypergraph.nodes
        node = filter(lambda x:node_name in x.label , nodes)
        return node

    def is_adj(self, pos1, pos2):
        return "adj" if abs(pos2-pos1) == 1 else "non-adj"

if __name__ == "__main__":
    sentence = "A B C"
#    sentence = "D B C A E"
    parsing = ParsingAlgo(sentence, "data/initial_values")
    parsing.get_hypergraph()
    parsing.display()
    # display.HypergraphFormatter(parsing.hypergraph).to_ipython()
    best = parsing.best_path()
    parsing.best_edges()
    
