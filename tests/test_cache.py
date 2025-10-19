import os
import time
from pathlib import Path
import pandas as pd

import trading.fetcher as fetcher


def _make_sample_df():
    return pd.DataFrame({
        'date': pd.date_range(end=pd.Timestamp.today(), periods=5),
        'open': [1, 2, 3, 4, 5],
        'high': [1, 2, 3, 4, 5],
        'low': [1, 2, 3, 4, 5],
        'close': [1, 2, 3, 4, 5],
        'volume': [100, 200, 300, 400, 500],
    })


def test_cache_fresh_and_stale(monkeypatch, tmp_path):
    symbol = 'TESTCASH.NS'
    raw_dir = fetcher.RAW_DIR
    fname = raw_dir / fetcher._safe_symbol_filename(symbol)
    # ensure clean state
    if fname.exists():
        fname.unlink()

    # monkeypatch yfinance.Ticker.history to return a sample DF and count calls
    calls = {'count': 0}

    def fake_history(self, period='1y', interval='1d'):
        calls['count'] += 1
        return _make_sample_df().set_index('date')

    monkeypatch.setattr('yfinance.Ticker.history', fake_history)

    # first call, force refresh -> writes cache and calls history
    df1 = fetcher.fetch_symbol_history(symbol, refresh_cache=True)
    assert calls['count'] == 1
    assert fname.exists()

    # Now set mtime to now (fresh). Call without refresh and with large freshness -> should NOT call history
    now = time.time()
    os.utime(fname, (now, now))
    calls['count'] = 0
    df2 = fetcher.fetch_symbol_history(symbol, refresh_cache=False, cache_freshness_seconds=3600)
    assert calls['count'] == 0

    # Now make the cache stale by setting mtime far in the past
    old = now - (3600 * 24 * 7)  # 7 days old
    os.utime(fname, (old, old))
    calls['count'] = 0
    # set cache freshness to 3600 seconds -> cache is stale so it should call history again
    df3 = fetcher.fetch_symbol_history(symbol, refresh_cache=False, cache_freshness_seconds=3600)
    assert calls['count'] == 1
