import io
import os
from urllib.request import Request, urlopen

import pandas as pd
import yfinance as yf

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataDownloadError(RuntimeError):
    """Raised when the market data download path fails."""


def get_sp500_tickers(filepath="data/external/sp500_tickers.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
    if os.path.exists(filepath):
        logger.info("Loading S&P 500 price history from local cache (data/external/)")
        return pd.read_csv(filepath)["Symbol"].tolist()

    logger.info("Scraping S&P500 Off Wikipedia")
    try:
        url_sp = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        req = Request(url=url_sp, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req).read().decode("utf-8")
    except Exception as exc:
        raise DataDownloadError(f"Unable to fetch S&P 500 ticker list from Wikipedia: {exc}") from exc

    try:
        tables = pd.read_html(io.StringIO(html))
        df = tables[0]
    except Exception as exc:
        raise DataDownloadError(f"Unable to parse S&P 500 ticker table from Wikipedia: {exc}") from exc

    tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
    if not tickers:
        raise DataDownloadError("S&P 500 ticker list was empty after parsing.")

    df[["Symbol", "Security"]].to_csv(filepath, index=False)
    logger.info("Successfully saved S&P data")
    logger.info(f"Successfully scraped {len(tickers)} tickers.")
    return tickers


def get_data_df(tickers, start_date="2018-01-01", end_date="2024-01-01", filepath="data/raw/sp500_raw_prices.csv"):
    if not tickers:
        raise ValueError("No tickers were provided for the data download.")

    if start_date >= end_date:
        raise ValueError(f"Invalid date range: start_date ({start_date}) must be before end_date ({end_date}).")

    os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
    if os.path.exists(filepath):
        logger.info("Loading S&P 500 price history from local cache (data/raw/)...")
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        try:
            return df.loc[start_date:end_date]
        except KeyError as exc:
            raise DataDownloadError(f"Cached data does not cover the requested date range: {exc}") from exc

    logger.info(f"Downloading data for {len(tickers)} assets")
    try:
        raw = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=False)
    except Exception as exc:
        raise DataDownloadError(f"Yahoo Finance download failed: {exc}") from exc

    if raw is None or raw.empty:
        raise DataDownloadError("Yahoo Finance returned an empty dataset.")

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            data = raw.xs("Close", level=0, axis=1)
        else:
            raise DataDownloadError("Yahoo Finance response did not contain a Close price series.")
    else:
        data = raw["Close"] if "Close" in raw.columns else raw

    if data is None or data.empty:
        raise DataDownloadError("No usable price data was returned after processing the Yahoo Finance response.")

    logger.info("\nCOLUMNS RETURNED:\n%s", data.columns)
    data_df = data.pct_change().iloc[1:].dropna(axis=1)
    if data_df.empty:
        raise DataDownloadError("The filtered return dataset is empty after removing missing values.")

    data_df.to_csv(filepath)
    logger.info("Data downloaded from get_data_df(). Shape: %s", data_df.shape)
    return data_df