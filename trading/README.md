Usage notes for the trading scanner

The scanner supports several CLI options useful for local development and production runs.

Options of interest

- --watchlist SYMBOLS...
  Provide tickers on the command line. Example: `--watchlist RELIANCE.NS TCS.NS`

- --symbols-file PATH
  Provide a file containing one ticker per line. This overrides the default built-in NIFTY50 list.
  Example: `--symbols-file my_watchlist.txt`

- --limit N
  Limit the scan to the first N tickers from the supplied watchlist or default list. Useful for fast local tests.
  Example: `--limit 5`

- --refresh-cache
  Force re-download of symbol historical data and overwrite cached data in SQLite database.
  Use this when you want fresh data regardless of cache age.

- --cache-freshness SECONDS
  Override the default cache freshness window (default 86400 seconds / 24 hours). If cached data is younger than this value it will be used instead of re-downloading.
  Example: `--cache-freshness 3600` (1 hour)

Examples

Quick dev run (first 5 NIFTY50 symbols):

```bash
python -m trading.scan --outdir outputs/dev --limit 5
```

Force-refresh cache for the full NIFTY50:

```bash
python -m trading.scan --outdir outputs/full --refresh-cache
```

Use a custom symbols file and 1-hour cache freshness:

```bash
python -m trading.scan --symbols-file my_symbols.txt --cache-freshness 3600
```

Notes

- Cached symbol data is stored in SQLite database at `trading/data/trading_data.db`.
- The default symbol list is `trading/data/nifty50.txt` when no `--watchlist` or `--symbols-file` is provided.
- Legacy CSV cache files may still exist under `trading/data/raw/` from older versions.
