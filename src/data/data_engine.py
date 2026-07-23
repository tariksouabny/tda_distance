import io
import os
from urllib.request import Request, urlopen

import pandas as pd
import yfinance as yf

from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_sp500_tickers(filepath="data/external/sp500_tickers.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
    if os.path.exists(filepath):
        logger.info("Loading S&P 500 price history from local cache (data/external/)")
        return pd.read_csv(filepath)["Symbol"].tolist()

    logger.info("Scraping S&P500 Off Wikipedia")
    url_sp = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    req = Request(url=url_sp, headers={"User-Agent": "Mozilla/5.0"})
    html = urlopen(req).read().decode("utf-8")
    tables = pd.read_html(io.StringIO(html))
    df = tables[0]
    tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
    df[["Symbol", "Security"]].to_csv(filepath, index=False)
    logger.info("Successfully saved S&P data")
    logger.info(f"Successfully scraped {len(tickers)} tickers.")
    return tickers


def get_data_df(tickers, start_date="2018-01-01", end_date="2024-01-01", filepath="data/raw/sp500_raw_prices.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
    if os.path.exists(filepath):
        logger.info("Loading S&P 500 price history from local cache (data/raw/)...")
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return df.loc[start_date:end_date]

    logger.info(f"Downloading data for {len(tickers)} assets")
    raw = yf.download(tickers, start=start_date, end=end_date)
    if "Close" in raw.columns.get_level_values(0):
        data = raw.xs("Close", level=0, axis=1)
    else:
        data = raw["Close"]

    logger.info("\nCOLUMNS RETURNED:\n%s", data.columns)
    data_df = data.pct_change().iloc[1:].dropna(axis=1)
    data_df.to_csv(filepath)
    logger.info("Data downloaded from get_data_df(). Shape: %s", data_df.shape)
    return data_df