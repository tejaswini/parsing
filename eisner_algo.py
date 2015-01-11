import pydecode
import numpy as np
import pprint
from collections import defaultdict

class EisnerAlgo:

    def __init__(self):
        self.num_shapes = 3
        self.tri=0; self.trap = 1;self.tri_stop=2;
        self.adj = 1; self.non_adj = 0
        self.num_dir = 2
        self.right = 0; self.left = 1
        self.graph = None
        self.out = []

    def eisner_first_order(self, sentence):
        n = len(sentence)
        coder = np.arange((self.num_shapes * self.num_dir * n * n), dtype=np.int64) \
        .reshape([self.num_shapes, self.num_dir, n, n])
        self.out = np.arange(n * n * self.num_shapes * self.num_dir * 2, dtype=np.int64).reshape([self.num_shapes, self.num_dir, 2, n, n])
        chart = pydecode.ChartBuilder(coder, self.out)

        chart.init(np.diag(coder[self.tri, self.right]).copy())
        chart.init(np.diag(coder[self.tri, self.left, 1:, 1:]).copy())

        for direction in range(self.num_dir):
            for tri, triStop, index in zip(np.diag(coder[self.tri, direction, 1:, 1:]), np.diag(coder[self.tri_stop, direction, 1:, 1:]), range(1,n)):

                chart.set(triStop, [[tri]], labels=[np.int64(self.out[2, direction, 0, index, index])])

        for k in range(1, n):
            for s in range(n):
                t = k + s
                if t >= n:
                    break

            # First create incomplete items.
                out_ind = np.zeros([t-s], dtype=np.int64)
                if s != 0:
                    label_indices = self.compute_label_indices(1, self.left, t, s)
                    chart.set_t(coder[self.trap, self.left,  s,  t],
                            coder[self.tri_stop,  self.right, s,  s:t],
                            coder[self.tri,  self.left,  s+1:t+1, t],
                            labels=label_indices)

                label_indices = self.compute_label_indices(1, self.right, s, t)

                chart.set_t(coder[self.trap, self.right, s, t],
                        coder[self.tri,  self.right, s,  s:t],
                        coder[self.tri_stop,  self.left,  s+1:t+1, t],
                        labels= label_indices)

                if s != 0:
                    out_ind.fill(self.out[0, self.left, 0, t, t])
                    chart.set_t(coder[self.tri,  self.left,  s, t],
                            coder[self.tri_stop,  self.left,  s, s:t],
                            coder[self.trap, self.left,  s:t, t],
                            labels= label_indices)


                    out_ind.fill(self.out[2, self.left, self.adj, t, t])
                    chart.set(coder[self.tri_stop, self.left,  s, t],
                        [[coder[self.tri,  self.left, s, t]]],
                        labels= out_ind)


                out_ind.fill(self.out[0, self.right, self.adj, s, s])
                chart.set_t(coder[self.tri,  self.right, s, t],
                        coder[self.trap, self.right, s,  s+1:t+1],
                        coder[self.tri_stop,  self.right, s+1:t+1, t],
                        labels= label_indices)
            
                if s!=0 or (s==0 and t==n-1):
                    out_ind.fill(self.out[2, self.right, self.adj, s, s])
                    chart.set(coder[self.tri_stop, self.right,  s, t],
                        [[coder[self.tri,  self.right, s, t]]],
                        labels=out_ind)

        self.graph = chart.finish()
        return self.graph

    def compute_marginals(self, label_scores):
        weights = pydecode.transform(self.graph, label_scores)
        edge_marginals = pydecode.marginals(self.graph, weights)
        return edge_marginals

    def compute_label_indices(self, shape, direction, head, mod):
        indices = np.tile([shape, direction, 0, head, mod], abs(head-mod)).\
            reshape(abs(head-mod), 5)
        indices[:,2] = self.compute_adj(head, mod)
        if(indices.shape[0] == 1):
            return np.array([self.out[indices[0,0], indices[0,1], indices[0,2], indices[0, 3], indices[0, 4]]])
        return self.out[indices[:,0].tolist(),indices[:,1].tolist(), indices[:,2].tolist(), indices[:,3].tolist(), indices[:,4].tolist()]
        

    def compute_adj(self, head, mod):
        if(head > mod):
            split  =  np.arange(mod, head)
        else:
            split = np.arange(head, mod)

        vfunc = np.vectorize(self.is_adj)
        return vfunc(head, split)

    def is_adj(self, head,  split):
        if abs(head - split) <=1:
            return self.adj
        else:
            return self.non_adj


