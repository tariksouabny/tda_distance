import pandas as pd
import matplotlib.pyplot as plt
import persim
from ripser import ripser
import os

# Import your custom modules
from src.data.data_engine import get_sp500_tickers, get_data_df
from src.data.data_engine import get_distance_matrix
from src.visualization.visualization import generate_mapper_graph

def run_tda_pipeline():
    print("--- Starting S&P 500 TDA Pipeline ---")
    
    # 1. Configuration
    crash_eve_date = '2020-02-19'
    lookback = 40
    
    # Optional: ensure the outputs directory exists for matplotlib charts
    os.makedirs("outputs/figures", exist_ok=True)

    # 2. Data Acquisition
    universe = get_sp500_tickers()
    # Note: If testing, you can slice the universe to save time: universe = universe[:100]
    data_df = get_data_df(universe, start_date="2018-01-01", end_date="2020-03-01")
    
    # yfinance might drop some tickers (delisted, etc.). We need the valid ones for the chart.
    valid_tickers = data_df.columns.tolist()

    # 3. Metric Space Translation (Math Engine)
    print(f"\nCalculating distance matrix for {crash_eve_date}...")
    distance_matrix = get_distance_matrix(data_df, target_date=crash_eve_date, lookback=lookback)

    # 4. Topological Feature Extraction (Ripser)
    print("\nComputing Persistent Homology...")
    tda_results = ripser(distance_matrix, maxdim=1, distance_matrix=True)
    diagrams = tda_results['dgms']

    # 5. Visual Engine A: Static Persistence Diagram
    print("Plotting Persistence Diagram...")
    plt.figure(figsize=(8, 6))
    persim.plot_diagrams(diagrams, show=False)
    plt.title(f"S&P 500 Persistence Diagram: {crash_eve_date}")
    
    # Save the plot alongside the HTML file, then display it
    plt.savefig(f"outputs/figures/persistence_diagram_{crash_eve_date}.png")
    plt.show(block=False) # block=False lets the script keep running while the chart is open
    plt.pause(3) # Keep it open for a few seconds before generating the Mapper graph

    # 6. Visual Engine B: Interactive Topological Network
    try:
        end_idx = data_df.index.get_indexer([pd.to_datetime(crash_eve_date)], method='ffill')[0]
    except KeyError:
        end_idx = len(data_df) - 1
    window_data = data_df.iloc[end_idx - lookback : end_idx]

    # Pass BOTH window_data and distance_matrix
    html_filename = f"outputs/figures/sp500_topology_{crash_eve_date}.html"    
    generate_mapper_graph(window_data, distance_matrix, valid_tickers, output_filename=html_filename)
    print("\n--- Pipeline Complete! ---")

if __name__ == "__main__":
    run_tda_pipeline()