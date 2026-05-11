import os
import kmapper as km
from sklearn.cluster import DBSCAN
from sklearn.manifold import MDS
import numpy as np

def generate_mapper_graph(window_data, distance_matrix, tickers, output_filename="market_map.html"):
    stock_data=window_data.T.to_numpy()
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    mapper = km.KeplerMapper(verbose=1)
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    lens = mapper.fit_transform(distance_matrix, projection=mds)
    graph = mapper.map(
        lens,
        stock_data,
        clusterer=DBSCAN(eps=0.4, min_samples=2, metric="correlation"),
        cover=km.Cover(n_cubes=15, perc_overlap=0.3)
    )
    mapper.visualize(
        graph,
        path_html=output_filename,
        title="S&P 500 Vietoris-Rips Correlation Metric Space",
        custom_tooltips=np.array(tickers)
    )
    print(f"Success: graph saved. Open '{output_filename} in your web browser")