
from itertools import combinations, product
import networkx as nx

def gen_dag(num_nodes, leaf_label):
    
    num_nodes += 1
    all_edges = list(combinations(range(leaf_label, num_nodes), 2))
    
    for p in product([None, 1, -1], repeat=len(all_edges)):
        G = nx.DiGraph()
        G.add_nodes_from(range(leaf_label, num_nodes))
        edges = [edge[::edge_dir] for edge, edge_dir in zip(all_edges, p) if edge_dir]
        G.add_edges_from(edges)
        if nx.is_directed_acyclic_graph(G):
            yield G


def topology_graph(root, leaf):
    
    graphs = list(gen_dag(root, leaf))
    toplogy = []
    
    for g in graphs:

        links = []
        p_counter = 0
        p_link = 0
        for (l,r) in g.edges():
            if l > r and (l,r) not in links:
                if p_link == l:
                    p_counter+=1
                if p_counter < 2:    
                    links.append((l, r))
                
                p_link = l
                
        if len(links) > 0 and links not in toplogy:
            toplogy.append(links)

    return toplogy        

