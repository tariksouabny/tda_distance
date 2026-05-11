from ripser import ripser
import yfinance as yf
import pandas as pd
import numpy as np
import persim
import matplotlib.pyplot as plt
import io
import os
from urllib.request import Request, urlopen
from src.utils.logger import get_logger

logger = get_logger(__name__)
def get_sp500_tickers(filepath="data/external/sp500_tickers.csv"):
    os.makedirs(os.path.dirname(filepath),exist_ok=True)
    if os.path.exists(filepath):
        logger.info("Loading S&P 500 price history from local cache (data/external/)")
        return pd.read_csv(filepath)['Symbol'].toList()
    logger.info("Scraping S&P500 Off Wikipedia")
    url_sp = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    req = Request(
        url=url_sp, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    html = urlopen(req).read().decode("utf-8")
    tables = pd.read_html(io.StringIO(html))
    df=tables[0]
    tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
    df[['Symbol','Security']].to_csv(filepath, index=False)
    logger.info(f"Successfully saved S&P data")
    logger.info(f"Successfully scraped {len(tickers)} tickers.")
    return tickers

def get_data_df(tickers, start_date="`2018-01-01", end_date="2024-01-01", filepath="data/raw/sp500_raw_prices.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if os.path.exists(filepath):
        print("Loading S&P 500 price history from local cache (data/raw/)...")
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return df.loc[start_date:end_date]
    print(f"Downloading data for {len(tickers)} assets")
    raw = yf.download(tickers, start=start_date, end=end_date)
    if 'Close' in raw.columns.get_level_values(0):
        data = raw.xs('Close', level=0, axis=1)
    else:
        data = raw['Close']
    print("\nCOLUMNS RETURNED:\n", data.columns)
    data_df = data.pct_change().iloc[1:].dropna(axis=1)
    print(f"Data downloaded from get_data_df(). Shape: {data_df.shape}")
    return data_df

# exec & testing #
if __name__ == "__main__":
    universe = get_sp500_tickers()
    data_df = get_data_df(universe)
    crash_eve_date = '2020-02-19'
    distance_matrix = get_distance_matrix(data_df, target_date=crash_eve_date)
    print(f"\n\n --- Distance Matrix for {crash_eve_date}: --- ")
    # vietoris-rips complex essentially creates clusters
    # we measure the touching edges of spheres rad. ε as a n-dimensional spider web
    # we search for H0 & H1; H0 are clusters (moving in lockstep)
    # H1 are holes in between frames. I.e., a divergence
    # we assign a persistence (death - birth) factor in time for each
    tda_results = ripser(distance_matrix, maxdim=1, distance_matrix=True)
    diagrams = tda_results['dgms']
    plt.figure(figsize=(4,3))
    persim.plot_diagrams(diagrams, show=False)
    plt.title(f"Persistence diagram for {crash_eve_date}")
    plt.show()