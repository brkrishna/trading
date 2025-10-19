import pandas as pd
import pytest
from pathlib import Path

# Expected API: functions compute_sma(series, n) and compute_rsi(series, n)
from trading.indicators import compute_sma, compute_rsi

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_csv(name):
    return pd.read_csv(FIXTURES_DIR / name, parse_dates=["date"]).sort_values("date")

def test_sma_basic():
    df = load_csv('sma_fixture.csv')
    closes = df['close']
    sma3 = compute_sma(closes, 3)
    # sma3 last value should be mean of last 3 closes: 3,4,5 => 4.0
    assert pytest.approx(sma3.iloc[-1]) == 4.0

def test_rsi_all_gains():
    df = load_csv('rsi_fixture.csv')
    closes = df['close']
    rsi = compute_rsi(closes, 14)
    # With steadily rising prices, RSI should be high (close to 100)
    assert rsi.iloc[-1] > 90
