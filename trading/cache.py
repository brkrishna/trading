import os
from pathlib import Path
from typing import Optional, Tuple, List
import time

# Cache defaults (can be overridden via env vars)
DEFAULT_MAX_CACHE_FILES = int(os.getenv('TRADING_CACHE_MAX_FILES', '200'))
DEFAULT_MAX_CACHE_BYTES = int(os.getenv('TRADING_CACHE_MAX_BYTES', str(200 * 1024 * 1024)))
# default prune policy (mtime or atime)
DEFAULT_PRUNE_POLICY = os.getenv('TRADING_CACHE_PRUNE_POLICY', 'mtime')

# Raw cache directory
RAW_DIR = Path(__file__).resolve().parent / 'data' / 'raw'
RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_stats(dirpath: Optional[Path] = None) -> dict:
    d = dirpath or RAW_DIR
    files = [p for p in d.iterdir() if p.is_file()]
    total_bytes = sum(p.stat().st_size for p in files)
    total_files = len(files)
    oldest = None
    newest = None
    if files:
        files_sorted = sorted(files, key=lambda p: p.stat().st_mtime)
        oldest = files_sorted[0]
        newest = files_sorted[-1]
    # If no raw files present, try DB stats (new storage backend)
    if total_files == 0:
        try:
            from . import storage as storage_mod
            s = storage_mod.get_db_stats()
            return {
                'dir': str(d),
                'total_files': 0,
                'total_bytes': 0,
                'oldest': None,
                'newest': None,
                'db_path': s.get('db_path'),
                'db_size_bytes': s.get('size_bytes'),
                'db_total_symbols': s.get('total_symbols'),
                'db_total_rows': s.get('total_rows'),
            }
        except Exception:
            pass
    return {
        'dir': str(d),
        'total_files': total_files,
        'total_bytes': total_bytes,
        'oldest': str(oldest) if oldest else None,
        'newest': str(newest) if newest else None,
    }


def has_raw_cache() -> bool:
    return RAW_DIR.exists() and any(p.suffix.lower() == '.csv' for p in RAW_DIR.iterdir())


def prune_cache(dirpath: Optional[Path] = None, max_files: Optional[int] = None, max_bytes: Optional[int] = None, policy: Optional[str] = None) -> dict:
    d = dirpath or RAW_DIR
    max_files = max_files if max_files is not None else DEFAULT_MAX_CACHE_FILES
    max_bytes = max_bytes if max_bytes is not None else DEFAULT_MAX_CACHE_BYTES

    policy = policy or DEFAULT_PRUNE_POLICY

    files = [p for p in d.iterdir() if p.is_file()]
    # choose sorting key based on policy: 'mtime' (modification) or 'atime' (access time)
    if policy == 'atime':
        files_sorted = sorted(files, key=lambda p: p.stat().st_atime)
    else:
        files_sorted = sorted(files, key=lambda p: p.stat().st_mtime)

    total = sum(p.stat().st_size for p in files_sorted)
    removed: List[str] = []
    # remove oldest until under thresholds
    while (len(files_sorted) > max_files) or (total > max_bytes):
        if not files_sorted:
            break
        to_remove = files_sorted.pop(0)
        try:
            sz = to_remove.stat().st_size
            to_remove.unlink()
            removed.append(str(to_remove))
            total -= sz
        except Exception:
            # skip if cannot remove
            pass

    return {
        'removed_count': len(removed),
        'removed_files': removed,
        'total_files_after': len(files_sorted),
        'total_bytes_after': total,
        'policy': policy,
    }


def _format_bytes(n: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def _cli_info():
    stats = get_cache_stats()
    print(f"Cache dir: {stats['dir']}")
    print(f"Files: {stats['total_files']}\nSize: {_format_bytes(stats['total_bytes'])}")
    if stats['oldest']:
        print(f"Oldest: {stats['oldest']}")
    if stats['newest']:
        print(f"Newest: {stats['newest']}")


def _cli_prune(args):
    res = prune_cache(max_files=args.max_files, max_bytes=args.max_bytes, policy=getattr(args, 'policy', None))
    print(f"Removed {res['removed_count']} files")
    print(f"Files after: {res['total_files_after']}, Size after: {_format_bytes(res['total_bytes_after'])}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='python -m trading.cache')
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('info', help='Show cache usage')
    p_prune = sub.add_parser('prune', help='Prune cache to configured limits')
    p_prune.add_argument('--max-files', type=int, default=None, help='Maximum cache files to keep')
    p_prune.add_argument('--max-bytes', type=int, default=None, help='Maximum total cache bytes to keep')
    p_prune.add_argument('--policy', choices=['mtime','atime'], default=None, help='Prune policy to use (defaults to env TRADING_CACHE_PRUNE_POLICY)')

    args = parser.parse_args()
    if args.cmd == 'info':
        _cli_info()
    elif args.cmd == 'prune':
        _cli_prune(args)
    else:
        parser.print_help()
