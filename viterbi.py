import pydecode.hyper as ph
import pydecode.display as display
import pprint

hyper1 = ph.Hypergraph()

def viterbi_path(hypergraph,weights,chart):
    chart,back=run_viterbi(hypergraph,weights,chart)
    


def run_viterbi(hypergraph,weights,chart):
    chart = []
    back= []
    
    for node in hypergraph.nodes():
        if(node.is_terminal()):
            chart[node.id()] = 0;

    for edge in hypergraph.edges():
        score = weights[edge]
        head_id = edge.head().id()

        for node in edge.tail():
            score += chart[node.id()]

        if(score > chart[head_id]):
            chart[head_id] = score
            back[head_id] = edge

    
    return chart,back

def run_inside_algo(hypergraph,weights,chart):
    chart = []
    
    for node in hypergraph.nodes():
        if(node.is_terminal()):
            chart[node.id()] = 0;

    for edge in hypergraph.edges():
        score = weights[edge]
        head_id = edge.head().id()

        for node in edge.tail():
            score += chart[node.id()]

    return chart
