import pandas as pd
import numpy as np

def compute_sma(series: pd.Series, n: int) -> pd.Series:
    """Simple moving average aligned to the right (includes current day)."""
    return series.rolling(window=n, min_periods=n).mean()

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI using Wilder's smoothing method.

    Returns a pd.Series aligned with the input closes.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # first average
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Use Wilder's smoothing for subsequent values
    rs = pd.Series(index=series.index, dtype=float)
    rsi = pd.Series(index=series.index, dtype=float)

    # find first valid index where avg_gain is not NaN
    first_valid = avg_gain.first_valid_index()
    if first_valid is None:
        return rsi

    # seed values
    prev_avg_gain = avg_gain.loc[first_valid]
    prev_avg_loss = avg_loss.loc[first_valid]
    rs.loc[first_valid] = prev_avg_gain / prev_avg_loss if prev_avg_loss != 0 else np.inf
    rsi.loc[first_valid] = 100 - (100 / (1 + (rs.loc[first_valid] if np.isfinite(rs.loc[first_valid]) else 1e9)))

    # iterate subsequent indices
    idxs = list(series.index)
    start = idxs.index(first_valid) + 1
    for i in range(start, len(idxs)):
        idx = idxs[i]
        g = gain.loc[idx]
        l = loss.loc[idx]
        prev_avg_gain = (prev_avg_gain * (period - 1) + g) / period
        prev_avg_loss = (prev_avg_loss * (period - 1) + l) / period
        rs_val = prev_avg_gain / prev_avg_loss if prev_avg_loss != 0 else np.inf
        rs.loc[idx] = rs_val
        rsi.loc[idx] = 100 - (100 / (1 + (rs_val if np.isfinite(rs_val) else 1e9)))

    return rsi
