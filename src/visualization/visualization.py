import os

import kmapper as km
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.manifold import MDS

from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_mapper_graph(window_data, distance_matrix, tickers, output_filename="market_map.html"):
    stock_data = window_data.T.to_numpy()
    os.makedirs(os.path.dirname(output_filename), exist_ok=True) if os.path.dirname(output_filename) else None
    mapper = km.KeplerMapper(verbose=1)
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
    lens = mapper.fit_transform(distance_matrix, projection=mds)
    graph = mapper.map(
        lens,
        stock_data,
        clusterer=DBSCAN(eps=0.4, min_samples=2, metric="correlation"),
        cover=km.Cover(n_cubes=15, perc_overlap=0.3),
    )
    mapper.visualize(
        graph,
        path_html=output_filename,
        title="S&P 500 Vietoris-Rips Correlation Metric Space",
        custom_tooltips=np.array(tickers),
    )
    logger.info("Success: graph saved. Open '%s' in your web browser", output_filename)