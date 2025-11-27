import yfinance as yf
import pandas as pd
from typing import List, Optional, Tuple
import re
import time
import logging
from . import cache as cache_mod
from . import storage as storage_mod

# use central cache module for pruning policy defaults
CACHE_FRESHNESS_SECONDS = 24 * 3600  # 1 day

# Rate limiting for batch fetches (ms between requests)
RATE_LIMIT_MS = 100

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 1

logger = logging.getLogger('trading.fetcher')

def _safe_symbol_filename(symbol: str) -> str:
    # keep alphanumerics, dash and underscore
    return re.sub(r'[^A-Za-z0-9_.-]', '_', symbol) + '.csv'

def _is_nse_symbol(symbol: str) -> bool:
    """Check if symbol is NSE format (ends with .NS)"""
    return symbol.endswith('.NS')

def _normalize_symbol(symbol: str) -> str:
    """Normalize symbol to NSE format if needed"""
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        symbol = symbol + '.NS'
    return symbol.upper()

def fetch_symbol_history(symbol: str, period: str = '1y', interval: str = '1d', refresh_cache: bool = False, cache_freshness_seconds: Optional[int] = None, retries: int = MAX_RETRIES) -> pd.DataFrame:
    """
    Fetch historical OHLCV for NSE symbol using yfinance and return DataFrame with date, open, high, low, close, volume.
    
    Supports NSE (.NS) stock symbols.
    Implements retry logic with exponential backoff for reliability.
    
    Args:
        symbol: NSE stock symbol (e.g., 'TCS.NS', 'INFY.NS', 'RELIANCE.NS')
        period: Historical period ('1y', '6mo', '1d', etc.)
        interval: Interval ('1d', '1h', '15m', etc.)
        refresh_cache: Force fetch from NSE data source (bypass cache)
        cache_freshness_seconds: Override default cache freshness
        retries: Number of retry attempts on failure
    
    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    # Normalize symbol
    symbol = _normalize_symbol(symbol)
    
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
                            logger.debug(f"Cache hit for {symbol}")
                            return df
                    except Exception:
                        # ignore parse errors and treat as stale
                        return df
                else:
                    return df
        except Exception as e:
            # fall through to re-fetch
            logger.debug(f"Cache miss for {symbol}: {e}")
            pass

    # Fetch NSE data with retry logic
    last_error = None
    for attempt in range(retries):
        try:
            t = yf.Ticker(symbol)
            df = t.history(period=period, interval=interval)
            if df.empty:
                logger.warning(f"No data for {symbol} (attempt {attempt + 1}/{retries})")
                last_error = "No data found"
                # For delisted/invalid symbols, return empty rather than retry
                if attempt == 0:
                    break
            else:
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
                except Exception as e:
                    logger.warning(f"Failed to save {symbol} to storage: {e}")
                logger.debug(f"Successfully fetched {symbol} ({len(df)} rows)")
                return df
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Error fetching {symbol} (attempt {attempt + 1}/{retries}): {str(e)[:100]}")
            if attempt < retries - 1:
                backoff_time = RETRY_BACKOFF_SECONDS * (2 ** attempt)
                logger.debug(f"Retrying in {backoff_time}s...")
                time.sleep(backoff_time)
            else:
                logger.error(f"Failed to fetch {symbol} after {retries} attempts: {last_error}")
    
    return pd.DataFrame()

def fetch_watchlist(symbols: List[str], period: str = '1y', interval: str = '1d', refresh_cache: bool = False, cache_freshness_seconds: Optional[int] = None, rate_limit_ms: int = RATE_LIMIT_MS) -> dict:
    """
    Fetch historical data for multiple symbols with rate limiting.
    
    Args:
        symbols: List of symbols to fetch
        period: Historical period
        interval: Data interval
        refresh_cache: Force refresh from Yahoo
        cache_freshness_seconds: Cache freshness threshold
        rate_limit_ms: Milliseconds to wait between requests (helps avoid rate limits)
    
    Returns:
        Dict mapping NSE symbol -> DataFrame
    """
    results = {}
    total = len(symbols)
    
    for idx, s in enumerate(symbols, 1):
        try:
            logger.info(f"Fetching {s} ({idx}/{total})")
            df = fetch_symbol_history(
                s, 
                period=period, 
                interval=interval, 
                refresh_cache=refresh_cache, 
                cache_freshness_seconds=cache_freshness_seconds
            )
            results[s] = df
        except Exception as e:
            logger.error(f"Error fetching {s}: {e}")
            results[s] = pd.DataFrame()
        
        # Rate limiting between requests
        if idx < total:
            time.sleep(rate_limit_ms / 1000.0)
    return results

def load_symbols_from_file(filepath: str) -> List[str]:
    """
    Load symbols from a file (one symbol per line, ignores comments and blank lines).
    
    Args:
        filepath: Path to symbols file
    
    Returns:
        List of symbols
    """
    try:
        with open(filepath, 'r') as f:
            symbols = [
                line.strip() 
                for line in f 
                if line.strip() and not line.strip().startswith('#')
            ]
        logger.info(f"Loaded {len(symbols)} symbols from {filepath}")
        return symbols
    except Exception as e:
        logger.error(f"Failed to load symbols from {filepath}: {e}")
        return []

def get_default_nse_symbols() -> List[str]:
    """Get default NSE symbols list (major 100+ stocks)"""
    from pathlib import Path
    default_file = Path(__file__).resolve().parent / 'data' / 'nse_symbols_major.txt'
    if default_file.exists():
        return load_symbols_from_file(str(default_file))
    else:
        logger.warning(f"Default NSE symbols file not found: {default_file}")
        return []