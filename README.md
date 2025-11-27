trading — scanner for SMA/RSI setups

This repository contains a small scanner that fetches historical OHLCV data for Indian stocks (NSE), computes SMA/RSI indicators, and detects pullback/breakout setups.

## Overview

The scanner:
- Supports **NSE (National Stock Exchange) India** stocks with `.NS` suffix
- Currently includes **~100 major NSE stocks** (easily extensible to 4000+)
- Fetches NSE data via yfinance with automatic retry and rate limiting
- Implements **intelligent caching** (SQLite DB at `trading/data/trading_data.db`)
- Features **retry logic** with exponential backoff for reliability
- Includes **rate limiting** to avoid overwhelming APIs
- Generates **interactive HTML reports** with technical analysis

## Data Source

### NSE via yfinance
- ✅ Reliable and widely-tested data source
- ✅ NSE stock data available via `.NS` suffix (e.g., `TCS.NS`, `INFY.NS`)
- ✅ Good historical data availability
- ✅ No API key required
- ✅ Automatic retry and rate limiting built-in

## Quick Start

- `--watchlist SYMBOLS...`  Provide symbols on the command line (e.g., `TCS.NS INFY.NS`)
- `--symbols-file PATH`     Provide a file with one ticker per line (overrides default)
- `--limit N`               Limit scan to first N symbols (useful for quick tests)
- `--refresh-cache`         Force re-download of NSE symbol history
- `--cache-freshness SECS`  Override cache freshness threshold (default 86400 = 24h)
- `--outdir PATH`           Output directory for results (default: `outputs/`)

### NSE Symbol Lists

The scanner supports multiple symbol lists:

1. **Default NSE Major (101 stocks)**: `trading/data/nse_symbols_major.txt`
   - Includes top companies across sectors
   - Suitable for most users
   - Loaded automatically if no custom list provided

2. **NIFTY50 Fallback**: `trading/data/nifty50.txt`
   - Legacy option, still available
   - Used if NSE major list not found

3. **Custom Lists**: Create your own `my_stocks.txt` with one symbol per line
   - Use NSE format with `.NS` suffix (e.g., `TCS.NS`, `INFY.NS`)
   - Include comments with `#` prefix
   - Example:
     ```
     # My favorite tech stocks
     TCS.NS
     INFY.NS
     WIPRO.NS
     HCLTECH.NS
     ```

Cached data
-----------

Per-symbol historical data is cached in a SQLite database at `trading/data/trading_data.db` to accelerate repeated runs.

### Cache Management

```bash
# Show database stats
python -m trading.storage info

# Prune database (keep last 100 symbols or under 50MB)
python -m trading.storage prune --max-symbols 100 --max-bytes 50000000

# Migrate legacy CSV cache to DB (one-time)
python -m trading.storage migrate-csv
```

### Data Refresh

To fetch fresh data from Yahoo Finance and update the cache:

```bash
# Refresh specific limit (first 20 symbols)
python -m trading.scan --limit 20 --refresh-cache

# Refresh all symbols in custom list
python -m trading.scan --symbols-file my_stocks.txt --refresh-cache
```

## Examples

### 1. Quick test scan (5 symbols)
```bash
python -m trading.scan --limit 5
```

### 2. Scan custom stock list
```bash
python -m trading.scan --symbols-file my_stocks.txt
```

### 3. Force fresh data and scan 50 NSE major stocks
```bash
python -m trading.scan --limit 50 --refresh-cache
```

### 4. Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```

Then access at `http://localhost:8501` and use the **"🔄 Refresh NSE Data"** checkbox to fetch fresh data.

Troubleshooting
---------------

### No data for some symbols
- NSE data may not be available for certain tickers
- Symbols may be delisted, suspended, or newly listed
- Verify ticker name on [NSE India website](https://www.nseindia.com)
- The scanner logs "No data for <SYMBOL>" for these cases

### Slow runs / Rate limits
- Use `--limit N` during development to reduce network calls
- The SQLite cache speeds up repeated runs significantly
- Rate limiting is built-in (default 100ms between requests)

### Symbol format errors
- Always use NSE format with `.NS` suffix: `TCS.NS`, `INFY.NS`
- Fetcher auto-normalizes symbols, but explicit `.NS` suffix is recommended
- Example valid formats:
  - ✅ `TCS.NS` (preferred)
  - ✅ `TCS` (auto-converted to `TCS.NS`)
  - ❌ `TCS.BO` (Bombay Stock Exchange, not NSE)
  - ❌ `TCS` (without .NS suffix - always use TCS.NS format)

### Permission errors
- Check write access to `trading/data/` directory
- Database should be readable/writable by your user account

### Expanding to more stocks

To add more NSE stocks beyond the current ~100:

1. **Manual approach**: Add symbols to `trading/data/nse_symbols_major.txt` (one per line)

2. **Programmatic approach**:
   ```python
   from trading.fetcher import load_symbols_from_file, fetch_watchlist
   
   # Load your custom list
   symbols = load_symbols_from_file('my_4000_stocks.txt')
   
   # Fetch with rate limiting (built-in)
   results = fetch_watchlist(symbols, refresh_cache=True)
   ```

3. **Sourcing 4000+ stocks**:
   - NSE publishes the complete symbol list on their website
   - You can also scrape it from financial data providers
   - Once you have the list, add it to a file and use `--symbols-file`

Screenshots (optional)
----------------------

You can open the generated HTML report in your browser and capture a screenshot manually. Example (Windows):

1. Run a scan to generate the report: 

```bash
python -m trading.scan --outdir outputs/dev --limit 10
```

2. Open the report file in your browser (Explorer -> open file), e.g. `outputs/dev/report_<run_id>.html`.

3. Use your OS screenshot tool (Snipping Tool on Windows, or PrintScreen) to capture the page.

Automated headless screenshots (Playwright)
-----------------------------------------

If you want an automated screenshot, use Playwright (optional):

```bash
pip install playwright
playwright install
python tools/screenshot_report.py outputs/dev/report_<run_id>.html outputs/dev/report.png
```

Note: Playwright will download browser binaries during `playwright install`.

Cache inspector (interactive)
-----------------------------

You can run a small local HTTP server that lists cached CSV files (if any legacy files remain) and allows deleting selected files:

```bash
python tools/cache_server.py --port 8000
# then open http://127.0.0.1:8000/ in your browser
```

This is intended for local, trusted use only (no auth). It operates on legacy CSV files under `trading/data/raw/`.

**Note**: The application now primarily uses SQLite storage. Use `python -m trading.storage info` to inspect the database.
