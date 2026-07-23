import os
import tempfile
import unittest

import pandas as pd

from src.data.data_engine import get_data_df
from src.features.tda_math import get_distance_matrix


class TestErrorHandling(unittest.TestCase):
    def test_get_data_df_raises_on_empty_ticker_list(self):
        with self.assertRaises(ValueError):
            get_data_df([], start_date="2020-01-01", end_date="2020-01-10", filepath="data/test_empty.csv")

    def test_get_distance_matrix_raises_on_invalid_window(self):
        data_df = pd.DataFrame(
            {"AAPL": [0.01, 0.02], "MSFT": [0.02, 0.03]},
            index=pd.to_datetime(["2020-01-01", "2020-01-02"]),
        )
        with self.assertRaises(ValueError):
            get_distance_matrix(data_df, target_date="2020-01-03", lookback=5)


if __name__ == "__main__":
    unittest.main()
