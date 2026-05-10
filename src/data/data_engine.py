from ripser import ripser
import yfinance as yf
import pandas as pd
import numpy as np
import persim
import matplotlib.pyplot as plt
import io
# tarik souabny
'''
Notes:
 * source is yfinance, adj. closing prices.
    - then calc. the returns
 * transforms the rolling correlation matix onto strict
 distance matrix for target date
 * file as SCRIPT to __init__
'''

## data acquisition ##
def get_sp500_tickers():
    from urllib.request import Request, urlopen
    print("Scraping S&P500 Off Wikipedia")
    url_sp = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    req = Request(
        url=url_sp, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    html = urlopen(req).read().decode("utf-8")
    tables = pd.read_html(io.StringIO(html))
    df=tables[0]
    tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
    print(f"Successfully scraped {len(tickers)} tickers.")
    return tickers

def get_data_df(tickers, start_date="2018-01-01", end_date="2024-01-01"):
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


# pass to strict dist. matrix for target date #
def get_distance_matrix(data_df, target_date, lookback=40):
    '''
    - the idea is to get the distance between two points in a metric space
    - but standard correlation not metric space pearson correlation coefficcient is NOT viable because:
        - for two stocks x, y stocks ∈ n-space, if we normalize, Pearson corr coeff 
        corr coeff ρ relates to the angle θ between X and Y as
                (1)     ρ = cos(θ)
        where ρ = 1 means x,y point in same directions, ρ=0 means x,y point in opposite directions, ρ=-1 means x,y point in opposite directions
        - the distance d, between x, is related as
                        d**2 = ||u||**2 + ||v||**2 - 2||u||||v||cos(θ)
                             = 1**2 + 1**2 - 2(1)(1)cos(θ)
                             = 2(1-cos(θ))
                (2) ⇒  d  =  sqrt(2(1-ρ))
    '''
    try:
        end_idx = data_df.index.get_loc(target_date)
    except KeyError:
        end_idx = data_df.index.get_indexer([pd.to_datetime(target_date)], method='ffill')[0]

    start_idx = end_idx - lookback
    if start_idx < 0:
        raise ValueError("ERROR: Not enough historical data to present a lookback window")

    window_data = data_df.iloc[start_idx:end_idx]
    corr_matrix = window_data.corr(method='pearson').to_numpy()
    dist_matrix = np.sqrt(np.clip(2*(1-corr_matrix),0,4))
    np.fill_diagonal(dist_matrix,0)
    return dist_matrix


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