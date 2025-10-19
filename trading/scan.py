import argparse
from . import cache as cache_mod
import logging
import time
import json
from datetime import datetime
from pathlib import Path
from .fetcher import fetch_watchlist
from .detector import detect_signal
from .writer import write_candidates_csv, write_candidates_json
from .report import generate_html_report

# Production defaults: use SMA20/SMA50, 60 days history
DEFAULT_CONFIG = {
    'sma_fast': 20,
    'sma_slow': 50,
    'rsi_period': 14,
    'rsi_min': 40,
    'rsi_max': 100,
    'pullback_window': 5,
    'breakout_lookback': 20,
    'volume_multiplier': 1.2,
    'min_history_days': 60,
    'sma_touch_tolerance_pct': 0.5,
    'liquidity_min_avg_volume': 100000,
}

def scan_watchlist(symbols, out_dir: Path, config=DEFAULT_CONFIG, limit: int = None, refresh_cache: bool = False, cache_freshness: int = None, report_path: Path = None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger('trading.scan')
    logger.setLevel(logging.INFO)
    start = time.time()
    # apply optional limit to avoid fetching full universe during dev/tests
    if limit and isinstance(limit, int) and limit > 0:
        symbols = symbols[:limit]
    fetched = fetch_watchlist(symbols, refresh_cache=refresh_cache, cache_freshness_seconds=cache_freshness)
    candidates = []
    failures = []
    processed = 0
    for s, df in fetched.items():
        processed += 1
        try:
            if df.empty:
                logger.warning('No data for %s', s)
                failures.append({'symbol': s, 'reason': 'no_data'})
                continue
            sig = detect_signal(s, df, config)
            if sig:
                candidates.append(sig)
        except Exception as e:
            logger.exception('Error processing %s: %s', s, e)
            failures.append({'symbol': s, 'reason': str(e)})

    # write outputs with timestamp
    run_id = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    csv_path = out_dir / f'candidates_{run_id}.csv'
    json_path = out_dir / f'candidates_{run_id}.json'
    report_path = report_path or (out_dir / f'report_{run_id}.html')
    write_candidates_csv(csv_path, candidates)
    write_candidates_json(json_path, candidates)

    end = time.time()
    run_meta = {
        'run_id': run_id,
        'timestamp_utc': datetime.utcnow().isoformat(),
        'symbols_processed': processed,
        'candidates_found': len(candidates),
        'failures': failures,
        'duration_seconds': end - start,
        'csv': str(csv_path),
        'json': str(json_path),
        'report': str(report_path),
    }
    # write run metadata
    meta_path = out_dir / 'reports'
    meta_path.mkdir(parents=True, exist_ok=True)
    with open(meta_path / f'run_{run_id}.json', 'w') as f:
        json.dump(run_meta, f, indent=2)

    logger.info('Scan complete: %s candidates found (run_id=%s)', len(candidates), run_id)
    return candidates

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--watchlist', nargs='+', required=False, help='List of tickers to scan (defaults to NIFTY50)')
    parser.add_argument('--symbols-file', default=None, help='Path to a file with one ticker per line (overrides default NIFTY50 file)')
    parser.add_argument('--outdir', default='outputs', help='Output directory')
    parser.add_argument('--limit', type=int, default=None, help='Limit to first N tickers from the watchlist (for quick runs)')
    parser.add_argument('--refresh-cache', action='store_true', help='Force refresh cached symbol data')
    parser.add_argument('--cache-freshness', type=int, default=None, help='Cache freshness in seconds (overrides default 24h)')
    # cache utilities
    parser.add_argument('--cache-info', action='store_true', help='Show cache stats and exit')
    parser.add_argument('--prune-cache', action='store_true', help='Prune cache according to limits (use with --prune-max-files/--prune-max-bytes)')
    parser.add_argument('--prune-max-files', type=int, default=None, help='Max cache files to keep for prune')
    parser.add_argument('--prune-max-bytes', type=int, default=None, help='Max cache bytes to keep for prune')
    parser.add_argument('--prune-policy', choices=['mtime','atime'], default='mtime', help='Prune policy: mtime (old files) or atime (LRU)')
    parser.add_argument('--score-high', type=int, default=75, help='Score threshold for high/green rows')
    parser.add_argument('--score-mid', type=int, default=40, help='Score threshold for mid/yellow rows')
    args = parser.parse_args(argv)
    # if no watchlist provided, load NIFTY50 default file
    watchlist = args.watchlist
    # allow user to pass explicit symbols file
    symbols_file = args.symbols_file
    if symbols_file:
        sfp = Path(symbols_file)
        if not sfp.exists():
            raise SystemExit(f'Symbols file not found: {sfp}')
        with open(sfp, 'r') as f:
            watchlist = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        print(f'Loaded watchlist ({len(watchlist)} symbols) from {sfp}')
    if not watchlist:
        default_file = Path(__file__).resolve().parent / 'data' / 'nifty50.txt'
        try:
            with open(default_file, 'r') as f:
                watchlist = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except FileNotFoundError:
            raise SystemExit(f'Default watchlist not found: {default_file}. Provide --watchlist or add the file.')
        print(f'Loaded default NIFTY50 watchlist ({len(watchlist)} symbols) from {default_file}')
    # If user requested cache info, show and exit
    if args.cache_info:
        stats = cache_mod.get_cache_stats()
        print(f"Cache dir: {stats['dir']}")
        print(f"Files: {stats['total_files']}, Size: {stats['total_bytes']}")
        raise SystemExit(0)

    # If user requested prune, run prune and exit
    if args.prune_cache:
        res = cache_mod.prune_cache(max_files=args.prune_max_files, max_bytes=args.prune_max_bytes, policy=args.prune_policy)
        print(f"Removed {res['removed_count']} files (policy={res.get('policy')})")
        print(f"Files after: {res['total_files_after']}, Size after: {res['total_bytes_after']}")
        raise SystemExit(0)

    outdir = Path(args.outdir)
    run_id = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    report_path = outdir / f'report_{run_id}.html'
    candidates = scan_watchlist(watchlist, outdir, limit=args.limit, refresh_cache=args.refresh_cache, cache_freshness=args.cache_freshness, config=DEFAULT_CONFIG, report_path=report_path)
    # generate report with thresholds
    try:
        generate_html_report(candidates, report_path, threshold_high=args.score_high, threshold_mid=args.score_mid)
    except Exception:
        logging.getLogger('trading.scan').exception('Failed to generate HTML report')
    print(f'Found {len(candidates)} candidates')

if __name__ == '__main__':
    main()
