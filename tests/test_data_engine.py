import unittest
import pandas as pd
import os
import shutil

from src.data.data_engine import get_sp500_tickers, get_data_df

class TestDataEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data/test_temp"
        os.makedirs(self.test_dir, exist_ok=True)
    def test_getsp500_tickers(self):
        test_path=f"{self.test_dir}/test_tickers.csv"
        tickers=get_sp500_tickers(filepath=test_path)
        self.assertIsInstance(tickers, list)
        self.assertGreater(len(tickers), 450)
        self.AssertTrue(os.path.exists(test_path))
    def test_get_data_df(self):
        test_path = f"{self.test_dir}/test_prices.csv"
        tickers = ['AAPL', 'MSFT'] # just test 2 stocks to make it fast
        df = get_data_df(tickers, start_date="2020-01-01", end_date="2020-01-10", filepath=test_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertTrue(os.path.exists(test_path))
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()