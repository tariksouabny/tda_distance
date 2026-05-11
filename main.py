import pandas as pd
import matplotlib.pyplot as plt
import persim
from ripser import ripser
import os

from src.data.data_engine import get_sp500_tickers, get_data_df
from src.features.tda_math import get_distance_matrix
from src.visualization.visualization import generate_mapper_graph
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_tda_pipeline():
    logger.info("--- Starting S&P 500 TDA Pipeline ---")
    crash_eve_date = '2020-04-19'
    lookback = 40
    os.makedirs("outputs/figures", exist_ok=True) # check if the outputs/figures folder exists
    universe = get_sp500_tickers()
    data_df = get_data_df(universe, start_date="2018-01-01", end_date="2020-03-01")
    valid_tickers = data_df.columns.tolist()
    logger.info(f"\nCalculating distance matrix for {crash_eve_date}...")
    distance_matrix = get_distance_matrix(data_df, target_date=crash_eve_date, lookback=lookback)
    logger.info("\nComputing Persistent Homology...")
    tda_results = ripser(distance_matrix, maxdim=1, distance_matrix=True)
    diagrams = tda_results['dgms']
    # fig 1. persistence diagram
    logger.info("Plotting Persistence Diagram...")
    plt.figure(figsize=(8, 6))
    persim.plot_diagrams(diagrams, show=False)
    plt.title(f"S&P 500 Persistence Diagram: {crash_eve_date}")
    plt.savefig(f"outputs/figures/persistence_diagram_{crash_eve_date}.png")
    plt.show(block=False) # block=False lets the script keep running while the chart is open
    plt.pause(3)
    # fig 2. topological network
    try:
        end_idx = data_df.index.get_indexer([pd.to_datetime(crash_eve_date)], method='ffill')[0]
    except KeyError:
        end_idx = len(data_df) - 1
    window_data = data_df.iloc[end_idx - lookback : end_idx]
    html_filename = f"outputs/figures/sp500_topology_{crash_eve_date}.html"    
    generate_mapper_graph(window_data, distance_matrix, valid_tickers, output_filename=html_filename)
    plt.close('all')
    logger.info("\n--- Pipeline Complete! ---")

if __name__ == "__main__":
    run_tda_pipeline()