import pandas as pd
from pathlib import Path
import pytest

# Expected API: detect_signal(df, config)
from trading.detector import detect_signal

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_csv(name):
    return pd.read_csv(FIXTURES_DIR / name, parse_dates=["date"]).sort_values("date")

def base_config():
    return {
        'sma_fast':5,
        'sma_slow':20,
        'rsi_period':14,
    'rsi_min':40,
    'rsi_max':100,
        'pullback_window':5,
        'breakout_lookback':20,
        'volume_multiplier':1.2,
        'min_history_days':25,
    'sma_touch_tolerance_pct':2.0,
        'liquidity_min_avg_volume':100,
    }

def test_pullback_detected():
    df = load_csv('pullback_fixture.csv')
    sig = detect_signal('TEST', df, base_config())
    assert sig is not None
    assert sig['signal_type'] == 'pullback'

def test_breakout_detected():
    df = load_csv('breakout_fixture.csv')
    sig = detect_signal('BRK', df, base_config())
    assert sig is not None
    assert sig['signal_type'] == 'breakout'

def test_low_liquidity_penalty():
    df = load_csv('low_liquidity_fixture.csv')
    sig = detect_signal('TLQ', df, base_config())
    # May still produce a signal but include low-liquidity in reason_tags or be penalized in score
    if sig:
        assert 'low-liquidity' in sig.get('reason_tags', []) or sig['score'] <= 20
