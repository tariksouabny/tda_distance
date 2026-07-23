import os

import numpy as np
import pandas as pd


def get_distance_matrix(data_df, target_date, lookback=40, save_path="data/processed/distance_matrix.csv"):
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
    if data_df is None or data_df.empty:
        raise ValueError("Cannot compute a distance matrix from an empty data frame.")

    if lookback <= 0:
        raise ValueError("lookback must be a positive integer.")

    os.makedirs(os.path.dirname(save_path), exist_ok=True) if os.path.dirname(save_path) else None

    try:
        end_idx = data_df.index.get_loc(target_date)
    except KeyError:
        try:
            end_idx = data_df.index.get_indexer([pd.to_datetime(target_date)], method="ffill")[0]
        except Exception as exc:
            raise ValueError(f"Target date '{target_date}' could not be resolved in the data index: {exc}") from exc

    start_idx = end_idx - lookback
    if start_idx < 0:
        raise ValueError("Not enough historical data to build the requested lookback window.")

    window_data = data_df.iloc[start_idx:end_idx]
    if window_data.empty:
        raise ValueError("The selected lookback window is empty.")

    if window_data.shape[1] < 2:
        raise ValueError("Not enough assets remain in the lookback window to compute a distance matrix.")

    corr_matrix = window_data.corr(method="pearson").to_numpy()
    if np.isnan(corr_matrix).any():
        raise ValueError("The correlation matrix contains NaN values; the window may be ill-conditioned.")

    dist_matrix = np.sqrt(np.clip(2 * (1 - corr_matrix), 0, 4))
    pd.DataFrame(dist_matrix, index=window_data.columns, columns=window_data.columns).to_csv(save_path)
    np.fill_diagonal(dist_matrix, 0)
    return dist_matrix