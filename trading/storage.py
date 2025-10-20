import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
import json
import datetime
import os
import pandas as pd

DB_PATH = Path(__file__).resolve().parent / 'data' / 'trading_data.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS symbols (
        symbol TEXT PRIMARY KEY,
        last_fetched TEXT,
        last_accessed TEXT,
        rows INTEGER DEFAULT 0
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS history (
        symbol TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        PRIMARY KEY(symbol, date)
    )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_history_symbol ON history(symbol)')
    conn.commit()
    conn.close()


def write_symbol_history(symbol: str, df: pd.DataFrame) -> None:
    """Persist the DataFrame of OHLCV for a symbol into the DB."""
    init_db()
    if df is None or df.empty:
        return
    # ensure date column is ISO strings
    rows = []
    for _, r in df.iterrows():
        date = r.get('date')
        if isinstance(date, (datetime.date, datetime.datetime)):
            date = pd.to_datetime(date).strftime('%Y-%m-%d')
        try:
            rows.append((
                symbol, 
                date, 
                float(r.get('open') or 0), 
                float(r.get('high') or 0), 
                float(r.get('low') or 0), 
                float(r.get('close') or 0), 
                float(r.get('volume') or 0)
            ))
        except (ValueError, TypeError):
            # Skip invalid data rows
            continue
    conn = _conn()
    cur = conn.cursor()
    cur.executemany('''INSERT OR REPLACE INTO history(symbol,date,open,high,low,close,volume) VALUES (?,?,?,?,?,?,?)''', rows)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'
    cur.execute('INSERT OR REPLACE INTO symbols(symbol,last_fetched,last_accessed,rows) VALUES (?,?,?,?)', (symbol, now, now, len(rows)))
    conn.commit()
    conn.close()


def read_symbol_history(symbol: str) -> pd.DataFrame:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute('SELECT date, open, high, low, close, volume FROM history WHERE symbol=? ORDER BY date ASC', (symbol,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([dict(r) for r in rows])
    # parse date
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception:
        pass
    return df


def get_symbol_meta(symbol: str) -> Optional[Dict[str, Any]]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute('SELECT symbol,last_fetched,last_accessed,rows FROM symbols WHERE symbol=?', (symbol,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return dict(r)


def touch_symbol_access(symbol: str) -> None:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'
    cur.execute('UPDATE symbols SET last_accessed=? WHERE symbol=?', (now, symbol))
    conn.commit()
    conn.close()


def get_db_stats() -> Dict[str, Any]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as cnt FROM symbols')
    total_symbols = cur.fetchone()['cnt']
    cur.execute('SELECT SUM(rows) as total_rows FROM symbols')
    total_rows = cur.fetchone()['total_rows'] or 0
    conn.close()
    size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
    return {'db_path': str(DB_PATH), 'size_bytes': size, 'total_symbols': total_symbols, 'total_rows': total_rows}


def prune_db(max_symbols: Optional[int] = None, max_bytes: Optional[int] = None, policy: str = 'last_fetched') -> Dict[str, Any]:
    """Prune symbols from the DB based on counts or file size.

    policy: 'last_fetched' or 'last_accessed'
    """
    init_db()
    stats = get_db_stats()
    removed = []
    conn = _conn()
    cur = conn.cursor()
    # prune by symbol count
    if max_symbols is not None and stats['total_symbols'] > max_symbols:
        # select symbols ordered by policy ascending
        order_col = 'last_fetched' if policy == 'last_fetched' else 'last_accessed'
        cur.execute(f"SELECT symbol FROM symbols ORDER BY {order_col} ASC")
        rows = [r['symbol'] for r in cur.fetchall()]
        to_remove = rows[:max(0, stats['total_symbols'] - max_symbols)]
        for s in to_remove:
            cur.execute('DELETE FROM history WHERE symbol=?', (s,))
            cur.execute('DELETE FROM symbols WHERE symbol=?', (s,))
            removed.append(s)
        conn.commit()
    # prune by bytes: approximate by checking file size and removing oldest symbols until under threshold
    if max_bytes is not None:
        stats2 = get_db_stats()
        size = stats2['size_bytes']
        if size > max_bytes:
            order_col = 'last_fetched' if policy == 'last_fetched' else 'last_accessed'
            cur.execute(f"SELECT symbol FROM symbols ORDER BY {order_col} ASC")
            rows = [r['symbol'] for r in cur.fetchall()]
            for s in rows:
                if size <= max_bytes:
                    break
                cur.execute('DELETE FROM history WHERE symbol=?', (s,))
                cur.execute('DELETE FROM symbols WHERE symbol=?', (s,))
                removed.append(s)
                conn.commit()
                size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
    conn.close()
    return {'removed': removed, 'removed_count': len(removed)}


def _cli_info():
    s = get_db_stats()
    print(f"DB: {s['db_path']}")
    print(f"Size: {s['size_bytes']} bytes")
    print(f"Symbols: {s['total_symbols']}")
    print(f"Rows: {s['total_rows']}")


def _cli_prune(args):
    res = prune_db(max_symbols=args.max_symbols, max_bytes=args.max_bytes, policy=args.policy)
    print(f"Removed {res['removed_count']} symbols")


def _cli_migrate(args):
    try:
        from . import cache as cache_mod
    except Exception:
        cache_mod = None
    if cache_mod is None:
        print('No cache module found; cannot locate raw CSVs')
        return
    raw_dir = cache_mod.RAW_DIR
    if not raw_dir.exists():
        print('No raw cache directory:', raw_dir)
        return
    res = migrate_csv_from_rawdir(raw_dir)
    print(f"Migrated {res['migrated_count']} CSV files into DB. Migrated copies are in {res['migrated_dir']}")


def migrate_csv_from_rawdir(raw_dir_path):
    """Import CSV files from raw_dir_path into DB and move them to migrated/ subfolder.

    Returns dict with migrated_count and migrated_dir path.
    """
    raw_dir = Path(raw_dir_path)
    migrated_dir = raw_dir / 'migrated'
    migrated_dir.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    count = 0
    for p in raw_dir.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() != '.csv':
            continue
        symbol = p.stem
        try:
            df = pd.read_csv(p, parse_dates=['date'])
            # basic validation
            if set(['date','open','high','low','close','volume']).issubset(df.columns):
                write_symbol_history(symbol, df)
                # move file to migrated folder
                try:
                    p.rename(migrated_dir / p.name)
                except Exception:
                    # fallback copy+delete
                    import shutil
                    shutil.copy2(p, migrated_dir / p.name)
                    try:
                        p.unlink()
                    except Exception:
                        pass
                count += 1
            else:
                print('Skipping (invalid columns):', p)
        except Exception as e:
            print('Failed to import', p, e)
    return {'migrated_count': count, 'migrated_dir': str(migrated_dir)}


def _cli_main():
    import argparse
    parser = argparse.ArgumentParser(prog='python -m trading.storage')
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('info', help='Show DB usage')
    p_prune = sub.add_parser('prune', help='Prune DB symbols')
    p_prune.add_argument('--max-symbols', type=int, default=None, help='Maximum symbols to keep')
    p_prune.add_argument('--max-bytes', type=int, default=None, help='Maximum DB bytes to keep')
    p_prune.add_argument('--policy', choices=['last_fetched','last_accessed'], default='last_fetched')
    p_mig = sub.add_parser('migrate-csv', help='Migrate existing CSVs from raw cache into DB')
    args = parser.parse_args()
    if args.cmd == 'info':
        _cli_info()
    elif args.cmd == 'prune':
        _cli_prune(args)
    elif args.cmd == 'migrate-csv':
        _cli_migrate(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    _cli_main()
