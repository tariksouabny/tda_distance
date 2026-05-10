import gudhi
import numpy as np

points = np.random.rand(20, 3)  # 20 points in 3D
rips = gudhi.RipsComplex(points=points, max_edge_length=0.5)
simplex_tree = rips.create_simplex_tree(max_dimension=2)

# Print simplices
for simplex in simplex_tree.get_skeleton(2):
    print(simplex)

# Optional plotting: 1-skeleton graph
import networkx as nx
import matplotlib.pyplot as plt

edges = [tuple(simplex[0]) for simplex in simplex_tree.get_skeleton(1) if len(simplex[0])==2]
G = nx.Graph()
G.add_edges_from(edges)
nx.draw(G, with_labels=True)
plt.show()