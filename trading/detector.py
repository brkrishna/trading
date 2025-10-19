from typing import Optional, Dict, Any
import pandas as pd
import math

from .indicators import compute_sma, compute_rsi


def compute_score(row: pd.Series, signal_type: str, metrics: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Compute detailed score and reason tags for a detected signal.

    Returns dict with 'score' and 'reason_tags'.
    """
    weights = config.get('score_weights', {'uptrend': 30, 'rsi': 20, 'quality': 20, 'volume': 20, 'liquidity_penalty': -10})
    reasons = []
    total = 0.0

    # Uptrend (30)
    uptrend_pass = row['close'] > row['sma_fast'] and row['close'] > row['sma_slow'] and row['sma_fast'] > row['sma_slow']
    uptrend_score = weights.get('uptrend', 30) if uptrend_pass else 0
    if uptrend_pass:
        reasons.append('uptrend')
    total += uptrend_score

    # RSI scoring (20)
    rsi = row['rsi']
    rsi_score = 0
    if 50 <= rsi <= 60:
        rsi_score = weights.get('rsi', 20)
    elif 45 <= rsi < 50:
        rsi_score = int(weights.get('rsi', 20) * 0.6)
    elif 60 < rsi <= 65:
        rsi_score = int(weights.get('rsi', 20) * 0.8)
    elif 40 <= rsi < 45:
        rsi_score = int(weights.get('rsi', 20) * 0.4)
    elif 65 < rsi <= 70:
        rsi_score = int(weights.get('rsi', 20) * 0.5)
    if rsi_score:
        reasons.append(f'rsi-{int(round(rsi))}')
    total += rsi_score

    # Quality score (pullback or breakout) (20)
    quality_score = 0
    if signal_type == 'pullback':
        touch_dist = metrics.get('touch_distance_pct', None)
        bounce_pct = metrics.get('bounce_pct', 0)
        if touch_dist is not None:
            # closer touch yields higher score
            toc = max(0.0, (config['sma_touch_tolerance_pct'] - touch_dist) / max(1e-6, config['sma_touch_tolerance_pct']))
            quality_score = int(weights.get('quality', 20) * toc)
        # bounce strength bonus
        if bounce_pct >= 1.0:
            quality_score += int(weights.get('quality', 20) * 0.2)
        reasons.append('pullback')
    elif signal_type == 'breakout':
        breakout_pct = metrics.get('breakout_pct', 0)
        quality_score = int(weights.get('quality', 20) * min(1.0, breakout_pct / 2.0))
        reasons.append('breakout')
    total += quality_score

    # Volume score (20)
    vol_score = 0
    vol_ratio = (row['volume'] / max(1e-6, row['vol_avg20']))
    if vol_ratio >= 2.0:
        vol_score = weights.get('volume', 20)
    elif vol_ratio >= config.get('volume_multiplier', 1.2):
        vol_score = int(weights.get('volume', 20) * (0.6 + 0.4 * (vol_ratio - config['volume_multiplier']) / (2.0 - config['volume_multiplier'])))
    if vol_score:
        reasons.append('volume-confirmed')
    total += vol_score

    # Liquidity penalty
    liquidity_penalty = 0
    if row['vol_avg20'] < config.get('liquidity_min_avg_volume', 100000):
        liquidity_penalty = weights.get('liquidity_penalty', -10)
        reasons.append('low-liquidity')
    total += liquidity_penalty

    # Normalize and clip
    score = int(max(0, min(100, math.floor(total))))

    return {'score': score, 'reason_tags': reasons}


def detect_signal(symbol: str, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # ensure sorted
    df = df.sort_values('date').reset_index(drop=True)
    if df.shape[0] < config.get('min_history_days', 30):
        return None

    closes = df['close']
    vols = df['volume']

    df['sma_fast'] = compute_sma(closes, config['sma_fast'])
    df['sma_slow'] = compute_sma(closes, config['sma_slow'])
    df['rsi'] = compute_rsi(closes, config['rsi_period'])
    df['vol_avg20'] = vols.rolling(window=config['sma_fast'], min_periods=1).mean()

    last = df.iloc[-1]
    if pd.isna(last['sma_fast']) or pd.isna(last['sma_slow']) or pd.isna(last['rsi']):
        return None

    # Pullback detection
    pw = config['pullback_window']
    touch_found = None
    for i in range(max(0, len(df) - pw - 1), len(df) - 1):
        row = df.iloc[i]
        if pd.isna(row['sma_fast']) or row['sma_fast'] == 0:
            continue
        dist_pct = abs(row['close'] - row['sma_fast']) / row['sma_fast'] * 100
        if dist_pct <= config['sma_touch_tolerance_pct']:
            # look for bounce after i
            for j in range(i + 1, len(df)):
                if df.iloc[j]['close'] > row['close']:
                    bounce = df.iloc[j]
                    vol_ok = bounce['volume'] >= config['volume_multiplier'] * bounce['vol_avg20']
                    touch_found = {'touch_idx': i, 'touch_close': float(row['close']), 'bounce_idx': j, 'bounce_close': float(bounce['close']), 'vol_ok': bool(vol_ok), 'touch_dist_pct': dist_pct, 'bounce_pct': (float(bounce['close']) - float(row['close'])) / max(1e-6, float(row['close'])) * 100}
                    break
        if touch_found:
            break

    # If pullback found, validate bounce day conditions
    if touch_found:
        bounce_idx = touch_found['bounce_idx']
        bounce_row = df.iloc[bounce_idx]
        # uptrend & rsi on bounce day
        if not (bounce_row['close'] > bounce_row['sma_fast'] and bounce_row['close'] > bounce_row['sma_slow'] and bounce_row['sma_fast'] > bounce_row['sma_slow']):
            pass
        elif not (config['rsi_min'] <= bounce_row['rsi'] <= config.get('rsi_max', 100)):
            pass
        else:
            metrics = {'touch_distance_pct': touch_found['touch_dist_pct'], 'bounce_pct': touch_found['bounce_pct']}
            score_info = compute_score(bounce_row, 'pullback', metrics, config)
            # include small history snippet for reporting (last 30 closes)
            history = df['close'].iloc[max(0, bounce_idx-29):bounce_idx+1].tolist()
            signal = {
                'symbol': symbol,
                'date': str(bounce_row['date'].date()) if hasattr(bounce_row['date'], 'date') else str(bounce_row['date']),
                'close': float(bounce_row['close']),
                'sma20': float(bounce_row['sma_fast']),
                'sma50': float(bounce_row['sma_slow']),
                'rsi14': float(bounce_row['rsi']),
                'vol': float(bounce_row['volume']),
                'vol_avg20': float(bounce_row['vol_avg20']),
                'signal_type': 'pullback',
                'trigger_date': str(bounce_row['date'].date()) if hasattr(bounce_row['date'], 'date') else str(bounce_row['date']),
                'score': score_info['score'],
                'reason_tags': score_info['reason_tags'],
                'metrics': metrics
            }
            signal['history'] = [float(x) for x in history]
            return signal

    # Breakout detection
    lookback = config['breakout_lookback']
    prior = df.iloc[-(lookback + 1):-1] if len(df) > lookback else df.iloc[:-1]
    prior_high = prior['close'].max() if not prior.empty else None
    if prior_high and last['close'] >= prior_high:
        prev_rsi = df.iloc[-2]['rsi'] if len(df) >= 2 else last['rsi']
        rsi_increase = last['rsi'] > prev_rsi
        vol_ok = last['volume'] >= config['volume_multiplier'] * last['vol_avg20']
        if rsi_increase and vol_ok:
            metrics = {'breakout_pct': (float(last['close']) - float(prior_high)) / max(1e-6, float(prior_high)) * 100}
            score_info = compute_score(last, 'breakout', metrics, config)
            history = df['close'].iloc[max(0, len(df)-30):len(df)].tolist()
            signal = {
                'symbol': symbol,
                'date': str(last['date'].date()) if hasattr(last['date'], 'date') else str(last['date']),
                'close': float(last['close']),
                'sma20': float(last['sma_fast']),
                'sma50': float(last['sma_slow']),
                'rsi14': float(last['rsi']),
                'vol': float(last['volume']),
                'vol_avg20': float(last['vol_avg20']),
                'signal_type': 'breakout',
                'trigger_date': str(last['date'].date()) if hasattr(last['date'], 'date') else str(last['date']),
                'score': score_info['score'],
                'reason_tags': score_info['reason_tags'],
                'metrics': metrics
            }
            signal['history'] = [float(x) for x in history]
            return signal

    return None
