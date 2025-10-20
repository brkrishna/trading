import yfinance as yf
import pandas as pd
from typing import List, Optional
import re
import time
from . import cache as cache_mod
from . import storage as storage_mod

# use central cache module for pruning policy defaults
CACHE_FRESHNESS_SECONDS = 24 * 3600  # 1 day

def _safe_symbol_filename(symbol: str) -> str:
    # keep alphanumerics, dash and underscore
    return re.sub(r'[^A-Za-z0-9_.-]', '_', symbol) + '.csv'

def fetch_symbol_history(symbol: str, period: str = '1y', interval: str = '1d', refresh_cache: bool = False, cache_freshness_seconds: Optional[int] = None) -> pd.DataFrame:
    """Fetch historical OHLCV for symbol using yfinance and return DataFrame with date, open, high, low, close, volume."""
    # Try load from cache unless refresh_cache is True
    # Check storage DB first unless refresh_cache
    if not refresh_cache:
        try:
            df = storage_mod.read_symbol_history(symbol)
            if not df.empty:
                # optionally check freshness via symbol metadata
                meta = storage_mod.get_symbol_meta(symbol) or {}
                freshness = cache_freshness_seconds if cache_freshness_seconds is not None else CACHE_FRESHNESS_SECONDS
                if 'last_fetched' in meta:
                    try:
                        fetched_ts = pd.to_datetime(meta['last_fetched'])
                        if (pd.Timestamp.utcnow() - fetched_ts) <= pd.Timedelta(seconds=freshness):
                            storage_mod.touch_symbol_access(symbol)
                            return df
                    except Exception:
                        # ignore parse errors and treat as stale
                        return df
                else:
                    return df
        except Exception:
            # fall through to re-fetch
            pass

    t = yf.Ticker(symbol)
    df = t.history(period=period, interval=interval)
    if df.empty:
        return pd.DataFrame()
    df = df.reset_index()
    df = df.rename(columns={'Date':'date','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'})
    # Ensure columns exist
    df = df[['date','open','high','low','close','volume']]
    # save to storage DB (best-effort)
    try:
        storage_mod.write_symbol_history(symbol, df)
        # run eviction/prune via cache module -> use storage prune
        try:
            # use environment defaults from cache_mod for policy
            storage_mod.prune_db(max_symbols=None, max_bytes=None, policy=cache_mod.DEFAULT_PRUNE_POLICY)
        except Exception:
            pass
    except Exception:
        pass
    return df

def fetch_watchlist(symbols: List[str], period: str = '1y', interval: str = '1d', refresh_cache: bool = False, cache_freshness_seconds: Optional[int] = None) -> dict:
    results = {}
    for s in symbols:
        try:
            df = fetch_symbol_history(s, period=period, interval=interval, refresh_cache=refresh_cache, cache_freshness_seconds=cache_freshness_seconds)
            results[s] = df
        except Exception:
            results[s] = pd.DataFrame()
    return results
