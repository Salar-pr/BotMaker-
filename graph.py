import random
import itertools
import networkx as nx
import matplotlib.pyplot as plt

def is_valid_coloring(graph, coloring):     
    for u, v in graph.edges():
        if coloring[u] == coloring[v]:
            return False
    return True

def greedy_coloring(graph):
    coloring = {}
    for node in graph.nodes():
        adjacent_colors = {coloring.get(neighbor) for neighbor in graph.neighbors(node) if neighbor in coloring}
        coloring[node] = next(color for color in itertools.count() if color not in adjacent_colors)
    return coloring

def welsh_powell_coloring(graph):
    nodes = sorted(graph.nodes(), key=lambda x: graph.degree(x), reverse=True)
    coloring = {}
    color = 0
    
    for node in nodes:
        if node not in coloring:
            color += 1
            coloring[node] = color
            for neighbor in nodes:
                if neighbor not in coloring and not any(coloring.get(adj) == color for adj in graph.neighbors(neighbor)):
                    coloring[neighbor] = color
    
    return coloring
while True:
    # ایجاد گراف نمونه
    G = nx.Graph()
    n_node = int(input("enter count nodes: "))
    G.add_nodes_from(range(n_node))
    for i in range(n_node):
        for j in range(i+1, n_node):
            if random.random() < 0.3:
                G.add_edge(i, j)

    # انتخاب الگوریتم رنگ‌آمیزی
    algorithm = input("Choose algorithm (greedy/welsh-powell): ").strip().lower()

    if algorithm == "greedy":
        coloring_result = greedy_coloring(G)
    elif algorithm == "welsh-powell":
        coloring_result = welsh_powell_coloring(G)
    else:
        print("Invalid algorithm choice")
        exit()

    # print('Coloring:', coloring_result)
    # print('Valid:', is_valid_coloring(G, coloring_result))
    # print('K:', len(set(coloring_result.values())))

    # نمایش گراف
    color_map = [coloring_result[node] for node in G.nodes()]
    nx.draw(G, node_color=color_map, with_labels=True, font_weight='bold')
    plt.show()
