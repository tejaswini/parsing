import pydecode
import numpy as np
import pprint
from collections import defaultdict

class EisnerAlgo:

    def __init__(self):
        self.num_shapes = 3
        self.tri=0; self.trap = 1;self.tri_stop=2;
        self.num_dir = 2
        self.right = 0; self.left = 1
        self.sentence = "NP VP PP"
        self.graph = None


    def eisner_first_order(self, n):
        coder = np.arange((self.num_shapes * self.num_dir * n * n), dtype=np.int64) \
        .reshape([self.num_shapes, self.num_dir, n, n])
        out = np.arange(n * n * self.num_shapes * self.num_dir * 2, dtype=np.int64).reshape([self.num_shapes, self.num_dir, 2, n, n])
        chart = pydecode.ChartBuilder(coder, out)

        chart.init(np.diag(coder[self.tri, self.right]).copy())
        chart.init(np.diag(coder[self.tri, self.left, 1:, 1:]).copy())

        for direction in range(self.num_dir):
            for tri, triStop, index in zip(np.diag(coder[self.tri, direction, 1:, 1:]), np.diag(coder[self.tri_stop, direction, 1:, 1:]), range(1,n)):
#                print "out[index,index,2]" + str(out[2, direction, 0, index, index])
                chart.set(triStop, [[tri]], labels=[np.int64(out[2, direction, 0, index, index])])

        for k in range(1, n):
            for s in range(n):
                t = k + s
                if t >= n:
                    break

            # First create incomplete items.
                out_ind = np.zeros([t-s], dtype=np.int64)
                if s != 0:
                    out_ind.fill(out[1, self.left, 0,  t, s])
#                    print "label is out[t,s,1]" + str(out[1, self.left, 0, t, s])
                    chart.set_t(coder[self.trap, self.left,  s,  t],
                            coder[self.tri_stop,  self.right, s,  s:t],
                            coder[self.tri,  self.left,  s+1:t+1, t],
                            labels=out_ind)



                out_ind.fill(out[1, self.right, 0, s, t])
#                print "label is out[s,t,1]" + str(out[1, self.right, 0, s, t])
                chart.set_t(coder[self.trap, self.right, s, t],
                        coder[self.tri,  self.right, s,  s:t],
                        coder[self.tri_stop,  self.left,  s+1:t+1, t],
                        labels=out_ind)


                if s != 0:
                    out_ind.fill(out[0, self.left, 0, t, t])
#                    print "label is out[t,s,0]" + str(out[0, self.left, 0, t, t])
                    chart.set_t(coder[self.tri,  self.left,  s, t],
                            coder[self.tri_stop,  self.left,  s, s:t],
                            coder[self.trap, self.left,  s:t, t],
                            labels=out_ind)

                    out_ind.fill(out[2, self.left, 0, t, t])
#                    print "label is out[t,t,2]" + str(out[2, self.left, 0, t, t])
                    chart.set(coder[self.tri_stop, self.left,  s, t],
                        [[coder[self.tri,  self.left, s, t]]],
                        labels=out_ind)

                out_ind.fill(out[0, self.right, 0, s, s])
#                print "label is out[s,t,0]" + str(out[0, self.right, 0, s, s])
                chart.set_t(coder[self.tri,  self.right, s, t],
                        coder[self.trap, self.right, s,  s+1:t+1],
                        coder[self.tri_stop,  self.right, s+1:t+1, t],
                        labels=out_ind)
            
                if s!=0 or (s==0 and t==n-1):
                    out_ind.fill(out[2, self.right, 0, s, s])
#                    print "label is out[s,s,2]" + str(out[2, self.right, 0, s, s])
                    chart.set(coder[self.tri_stop, self.right,  s, t],
                        [[coder[self.tri,  self.right, s, t]]],
                        labels=out_ind)

        self.graph = chart.finish()
        # print "graph is"
        # pprint.pprint(self.graph)
        return self.graph

    def compute_marginals(self, label_scores):
        weights = pydecode.transform(self.graph, label_scores)
        edge_marginals = pydecode.marginals(self.graph, weights)
        return edge_marginals

