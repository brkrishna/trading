import json
from pathlib import Path
import builtins
import pytest

from trading import scan


def test_default_watchlist_loaded_and_limit(monkeypatch, tmp_path, capsys):
    # monkeypatch fetch_watchlist to capture symbols and return empty dict
    captured = {}

    def fake_fetch_watchlist(symbols, period='1y', interval='1d', refresh_cache=False, **kwargs):
        captured['symbols'] = list(symbols)
        # return empty dataframes so scan finishes quickly
        return {s: __import__('pandas').DataFrame() for s in symbols}

    # scan.py imports fetch_watchlist at module level, so patch that name
    monkeypatch.setattr('trading.scan.fetch_watchlist', fake_fetch_watchlist)

    # run main without watchlist: should load default NIFTY50 file
    scan.main(['--outdir', str(tmp_path)])
    captured_symbols = captured.get('symbols')
    assert captured_symbols is not None
    # default file contains 50 symbols
    assert len(captured_symbols) == 50

    # run with limit 5
    captured.clear()
    scan.main(['--outdir', str(tmp_path), '--limit', '5'])
    captured_symbols = captured.get('symbols')
    assert captured_symbols is not None
    assert len(captured_symbols) == 5
