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
        self.weights = None
        self.sentence = None

    def eisner_first_order(self, sentence):
        self.sentence = sentence
        n = len(sentence)
        coder = np.arange((self.num_shapes * self.num_dir * n * n),
                dtype=np.int64).reshape([self.num_shapes, self.num_dir, n, n])
        self.out = np.arange(n * n * self.num_shapes * self.num_dir * 2,
                 dtype=np.int64).reshape([self.num_shapes, self.num_dir, 2, n, n])
        chart = pydecode.ChartBuilder(coder, self.out)

        chart.init(np.diag(coder[self.tri, self.right]).copy())
        chart.init(np.diag(coder[self.tri, self.left, 1:, 1:]).copy())

        for direction in range(self.num_dir):
            for tri, triStop, index in zip(np.diag(coder[self.tri, direction]),
                        np.diag(coder[self.tri_stop, direction]), range(n)):

               if(index == 0):
                    continue

               chart.set(triStop, [[tri]], labels=[np.int64(self.out[self.tri_stop,
                                         direction, self.adj, index, index])])

        for k in range(1, n):
            for s in range(n):
                t = k + s
                if t >= n:
                    break

            # First create incomplete items.
                out_ind = np.zeros([t-s], dtype=np.int64)
                if s!=0:
                    label_indices = self.compute_label_indices(self.trap,
                                     self.left, t , s)
                    
                    chart.set_t(coder[self.trap, self.left,  s,  t],
                            coder[self.tri_stop,  self.right, s,  s:t],
                            coder[self.tri,  self.left,  s+1:t+1, t],
                            labels=label_indices)

                label_indices = self.compute_label_indices(self.trap, self.right,
                                                           s, t)
                chart.set_t(coder[self.trap, self.right, s, t],
                        coder[self.tri,  self.right, s,  s:t],
                        coder[self.tri_stop,  self.left,  s+1:t+1, t],
                        labels= label_indices)

                if s!=0:
                    label_indices = self.compute_label_indices(self.tri, self.left,
                                                           t, s)

                    chart.set_t(coder[self.tri,  self.left,  s, t],
                            coder[self.tri_stop,  self.left,  s, s:t],
                            coder[self.trap, self.left,  s:t, t])
                    
                    label_indices = self.compute_label_indices(self.tri_stop,
                                     self.left, s, t)

                    chart.set(coder[self.tri_stop, self.left,  s, t],
                        [[coder[self.tri,  self.left, s, t]]],
                        labels= label_indices)


                label_indices = self.compute_label_indices(self.tri,
                                     self.right, s, t)

                chart.set_t(coder[self.tri,  self.right, s, t],
                        coder[self.trap, self.right, s,  s+1:t+1],
                        coder[self.tri_stop,  self.right, s+1:t+1, t])
            
                if s!=0 or (s==0 and t==n-1):
                    label_indices = self.compute_label_indices(self.tri_stop,
                                     self.right, s, t)

                    chart.set(coder[self.tri_stop, self.right,  s, t],
                        [[coder[self.tri,  self.right, s, t]]],
                        labels=label_indices)

        self.graph = chart.finish()
        return self.graph

    def compute_weights(self, label_scores):
        if self.weights == None:
            self.weights = pydecode.transform(self.graph, label_scores)
        return self.weights
            
    def compute_marginals(self, label_scores):
        self.compute_weights(label_scores)
        edge_marginals = pydecode.marginals(self.graph, self.weights)
        return edge_marginals

    def best_path(self, label_scores):
        self.compute_weights(label_scores)
        return pydecode.best_path(self.graph, self.weights)

    def best_edges(self, label_scores):
        path = self.best_path(label_scores)
        best_edges = path.edges
        heads = np.array([], dtype=np.int64)

        for edge in best_edges:
            heads = np.append(heads, edge.head.label)

        shapes, direction, head, modifier =\
            self.get_indices_of_heads(heads, len(self.sentence))

        right_indices = np.where(direction == 0)
        left_indices = np.where(direction == 1)

        depen = np.full(modifier.size, -1)
        temp_mod = modifier[right_indices] - 1
        depen[temp_mod.tolist()] = head[right_indices].tolist()
        temp_mod = modifier[left_indices] - 1
        depen[temp_mod.tolist()] = head[left_indices].tolist()
        return depen

    def get_indices_of_heads(self, heads, n):
        shapes = heads / (n*n*2)
        indices = np.where(shapes == 1)

        x = heads - (shapes * n*n*2)
        direction = x / (n*n)

        x = x%(n*n*2)
        is_adj = x / (n*n)
    
        x = x - (is_adj*n*n)
        row = x/n

        column = x%n

        return shapes[indices], direction[indices], row[indices], column[indices]

    def compute_label_indices(self, shape, direction, head, mod):
        indices = np.tile([shape, direction, 0, head, mod], abs(head-mod)).\
            reshape(abs(head-mod), 5)
        indices[:,2] = self.compute_adj(head, mod)
        if(indices.shape[0] == 1):
            return np.array([self.out[indices[0,0], indices[0,1], indices[0,2],
                                      indices[0, 3], indices[0, 4]]])
        return self.out[indices[:,0].tolist(),indices[:,1].tolist(),
              indices[:,2].tolist(), indices[:,3].tolist(), indices[:,4].tolist()]

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


