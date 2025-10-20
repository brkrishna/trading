"""Trading utilities package.

A scanner for SMA/RSI setups that fetches historical OHLCV for tickers,
computes SMA/RSI indicators, and detects pullback/breakout setups.
"""

__version__ = "1.0.0"
__author__ = "Trading Scanner"

# Main API imports for easy access
from .scan import scan_watchlist, main as scan_main
from .detector import detect_signal
from .fetcher import fetch_symbol_history, fetch_watchlist
from .indicators import compute_sma, compute_rsi
from .writer import write_candidates_csv, write_candidates_json
from .report import generate_html_report

__all__ = [
    "scan_watchlist",
    "scan_main", 
    "detect_signal",
    "fetch_symbol_history",
    "fetch_watchlist",
    "compute_sma",
    "compute_rsi",
    "write_candidates_csv",
    "write_candidates_json",
    "generate_html_report",
    "__version__",
    "__author__",
]
