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

def get_backpointer(hypergraph,back):
    to_examine = []
    path = []
    to_examine.append(hypergraph.root())
    while(len(to_examine)!=0):
        node = to_examine[0]
        to_examine = to_examine[1:]
        edge = back[node.id()]
        if(edge is None):
            continue
        path.append(edge)
        for node in edge.tail():
            to_examine.append(node)
    
    path.sort(key=lambda x:x.id())
    return ph.Path(hypergraph,path)



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

def outside_algo(hypergraph,weights,inside_chart,chart):
    # TODO check weights
    if(len(inside_chart) != len(hypergraph.nodes())):
        raise HypergraphException("Chart size doesn't match graph")
    edges = hypergraph.edges()

    for edge in reversed(edges):
        full_score = weights[edge]
        for node in edge.tail():
            full_score += inside_chart[node.id()]
        head_score = chart[edge.head().id()]

        for node in edge.tail():
            score= head_score + full_score - inside_chart[node.id()]
            if(score > chart[node.id()]):
                chart[node.id()] = score

    bias = weights.bias()
    for i in xrange(len(chart)):
        chart[i] +=bias
    return chart
        
        
