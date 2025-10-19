import pandas as pd
from trading.detector import compute_score

def make_row(close=100, sma_fast=95, sma_slow=90, rsi=55, volume=2000, vol_avg20=1500):
    return pd.Series({'close': close, 'sma_fast': sma_fast, 'sma_slow': sma_slow, 'rsi': rsi, 'volume': volume, 'vol_avg20': vol_avg20})

def test_score_pullback_good_volume():
    row = make_row()
    metrics = {'touch_distance_pct': 0.5, 'bounce_pct': 1.5}
    cfg = {'sma_touch_tolerance_pct':2.0, 'volume_multiplier':1.2, 'liquidity_min_avg_volume':100, 'score_weights': {'uptrend':30,'rsi':20,'quality':20,'volume':20,'liquidity_penalty':-10}}
    res = compute_score(row, 'pullback', metrics, cfg)
    assert 0 <= res['score'] <= 100
    assert 'uptrend' in res['reason_tags']
    assert any(tag.startswith('rsi-') for tag in res['reason_tags'])

def test_score_low_liquidity_penalty():
    row = make_row(volume=10, vol_avg20=8)
    metrics = {'touch_distance_pct': 0.2, 'bounce_pct': 0.5}
    cfg_penalty = {'sma_touch_tolerance_pct':2.0, 'volume_multiplier':1.2, 'liquidity_min_avg_volume':1000, 'score_weights': {'uptrend':30,'rsi':20,'quality':20,'volume':20,'liquidity_penalty':-10}}
    cfg_no_penalty = {'sma_touch_tolerance_pct':2.0, 'volume_multiplier':1.2, 'liquidity_min_avg_volume':0, 'score_weights': {'uptrend':30,'rsi':20,'quality':20,'volume':20,'liquidity_penalty':0}}
    res_penalty = compute_score(row, 'pullback', metrics, cfg_penalty)
    res_no_penalty = compute_score(row, 'pullback', metrics, cfg_no_penalty)
    # Penalty config should include low-liquidity tag and produce a lower score than no-penalty config
    assert 'low-liquidity' in res_penalty['reason_tags']
    assert res_penalty['score'] < res_no_penalty['score']
