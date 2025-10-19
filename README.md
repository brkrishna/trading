trading — scanner for SMA/RSI setups

This repository contains a small scanner that fetches historical OHLCV for tickers (via yfinance by default), computes SMA/RSI indicators, and detects pullback/breakout setups.

Quick flags

- --watchlist SYMBOLS...  Provide symbols on the command line.
- --symbols-file PATH      Provide a file with one ticker per line (overrides built-in NIFTY50).
- --limit N                Limit scan to first N symbols (useful for quick tests).
- --refresh-cache          Force re-download of symbol history.
- --cache-freshness SECS   Cache freshness in seconds (default 86400 = 24h).

Cached data

Per-symbol cached CSVs are stored under `trading/data/raw/` to accelerate repeated runs.

See `trading/README.md` for more usage examples.

Troubleshooting
---------------

- No data for some symbols: Yahoo/YFinance may not have data for certain tickers or they may be delisted. The scanner will log "No data for <SYMBOL>" for these cases. Consider verifying the ticker name on Yahoo Finance.
- Slow runs / rate limits: Use `--limit` during development to reduce network calls. The cache under `trading/data/raw/` speeds repeated runs.
- Forcing fresh data: Use `--refresh-cache` to force re-downloads even if cache is fresh.
- Inspecting cache usage:
	- Info: python -m trading.cache info
	- Prune: python -m trading.cache prune --max-files 100 --max-bytes 50000000

If you see permission errors when writing cache files, check that your user has write access to `trading/data/raw/`.

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

You can run a small local HTTP server that lists cached files and allows deleting selected files:

```bash
python tools/cache_server.py --port 8000
# then open http://127.0.0.1:8000/ in your browser
```

This is intended for local, trusted use only (no auth). It operates directly on files under `trading/data/raw/`.
