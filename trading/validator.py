"""
Comprehensive validation engine based on the breakout validation checklist.
Provides detailed scoring for technical and fundamental indicators with explanations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger('trading.validator')

class BreakoutValidator:
    """
    Implements the comprehensive breakout validation checklist with scoring.
    Based on the 48-point validation framework for technical and fundamental analysis.
    """
    
    def __init__(self):
        self.technical_weights = {
            'volume_score': 1.0,      # Volume confirmation (most critical)
            'resistance_score': 1.0,   # Resistance quality  
            'sma_alignment_score': 1.0, # Moving average alignment
            'rsi_score': 1.0,         # RSI momentum check
            'support_score': 1.0      # Stop loss distance
        }
        
        self.fundamental_weights = {
            'sector_score': 1.0,      # Sector tailwinds
            'liquidity_score': 1.0,   # Market cap & liquidity
            'balance_sheet_score': 1.0, # Financial health
            'earnings_score': 1.0,    # Recent earnings quality
            'news_score': 1.0         # News sentiment
        }
        
        # Red flag criteria (auto-skip regardless of other scores)
        self.red_flags = {
            'volume_too_low': "Volume below average - likely false breakout",
            'rsi_exhausted': "RSI above 75 - momentum exhausted", 
            'stop_too_wide': "Stop loss >6% away - risk too high",
            'debt_too_high': "Debt/Equity >2.0 - overleveraged company",
            'bad_news': "Negative news announced - sentiment risk"
        }

    def validate_symbol(self, symbol_data: Dict[str, Any], market_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive validation of a symbol using the checklist framework.
        
        Args:
            symbol_data: Dictionary containing symbol price/volume data and indicators
            market_data: Optional market context (NIFTY performance, etc.)
            
        Returns:
            Dictionary with detailed scores, explanations, and recommendations
        """
        try:
            # Calculate technical scores
            tech_scores = self._calculate_technical_scores(symbol_data)
            
            # Calculate fundamental scores (with available data)
            fund_scores = self._calculate_fundamental_scores(symbol_data)
            
            # Check for red flags
            red_flags = self._check_red_flags(symbol_data, tech_scores, fund_scores)
            
            # Calculate overall scores
            tech_total = sum(tech_scores.values())
            fund_total = sum(fund_scores.values()) 
            overall_score = (tech_total + fund_total) / (len(tech_scores) + len(fund_scores)) * 20  # Scale to 100
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_score, red_flags, tech_total, fund_total)
            
            return {
                'symbol': symbol_data.get('symbol', 'Unknown'),
                'overall_score': round(overall_score, 1),
                'technical_score': round(tech_total, 1),
                'fundamental_score': round(fund_total, 1),
                'technical_details': tech_scores,
                'fundamental_details': fund_scores,
                'red_flags': red_flags,
                'recommendation': recommendation,
                'explanations': self._get_explanations(),
                'checklist_summary': self._generate_checklist_summary(tech_scores, fund_scores)
            }
            
        except Exception as e:
            logger.error(f"Validation error for {symbol_data.get('symbol', 'Unknown')}: {e}")
            return {
                'symbol': symbol_data.get('symbol', 'Unknown'),
                'overall_score': 0,
                'technical_score': 0,
                'fundamental_score': 0,
                'error': str(e),
                'recommendation': {'action': 'SKIP', 'reason': 'Validation error', 'confidence': 'LOW'}
            }

    def _calculate_technical_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate technical indicator scores based on checklist criteria"""
        scores = {}
        
        # 1. Volume Score (0-4 points)
        scores['volume_score'] = self._score_volume(data)
        
        # 2. Resistance Quality Score (0-4 points) 
        scores['resistance_score'] = self._score_resistance(data)
        
        # 3. SMA Alignment Score (0-4 points)
        scores['sma_alignment_score'] = self._score_sma_alignment(data)
        
        # 4. RSI Momentum Score (0-4 points)
        scores['rsi_score'] = self._score_rsi(data)
        
        # 5. Support/Stop Loss Score (0-4 points)
        scores['support_score'] = self._score_support_distance(data)
        
        return scores

    def _score_volume(self, data: Dict[str, Any]) -> float:
        """Score volume confirmation (1.5x+ average = strong breakout)"""
        try:
            current_vol = data.get('vol', 0)
            avg_vol = data.get('vol_avg20', 1)  # Avoid division by zero
            
            if avg_vol == 0:
                return 0
                
            vol_ratio = current_vol / avg_vol
            
            # Scoring based on checklist criteria
            if vol_ratio >= 2.5:    # 2.5x+ average = Excellent
                return 4
            elif vol_ratio >= 2.0:  # 2x average = Very Good  
                return 3
            elif vol_ratio >= 1.5:  # 1.5x average = Good (minimum threshold)
                return 2
            elif vol_ratio >= 1.0:  # Average volume = Weak
                return 1
            else:                   # Below average = Poor
                return 0
                
        except Exception:
            return 0

    def _score_resistance(self, data: Dict[str, Any]) -> float:
        """Score resistance breakout quality"""
        try:
            # Use breakout percentage as proxy for resistance strength
            breakout_pct = data.get('metrics', {}).get('breakout_pct', 0)
            
            # Scoring based on breakout strength
            if breakout_pct >= 5.0:    # 5%+ breakout = Very Strong
                return 4
            elif breakout_pct >= 3.0:  # 3-5% breakout = Strong
                return 3  
            elif breakout_pct >= 1.5:  # 1.5-3% breakout = Moderate
                return 2
            elif breakout_pct >= 0.5:  # 0.5-1.5% breakout = Weak
                return 1
            else:                      # <0.5% breakout = Very Weak
                return 0
                
        except Exception:
            return 2  # Default moderate score if data unavailable

    def _score_sma_alignment(self, data: Dict[str, Any]) -> float:
        """Score moving average alignment (Golden alignment = best)"""
        try:
            close = data.get('close', 0)
            sma20 = data.get('sma20', 0) 
            sma50 = data.get('sma50', 0)
            
            if close == 0 or sma20 == 0 or sma50 == 0:
                return 0
            
            # Perfect Golden Alignment: Price > SMA20 > SMA50 with good spacing
            if close > sma20 > sma50:
                # Check spacing between SMAs (indicates trend strength)
                sma_gap = (sma20 - sma50) / sma50 * 100  # Percentage gap
                price_gap = (close - sma20) / sma20 * 100
                
                if sma_gap >= 3.0 and price_gap >= 2.0:  # Wide gaps = Strong trend
                    return 4
                elif sma_gap >= 1.5 and price_gap >= 1.0: # Moderate gaps = Good trend  
                    return 3
                elif sma_gap >= 0.5:  # Small gaps = Weak trend
                    return 2
                else:  # Minimal gaps = Very weak
                    return 1
            else:  # No golden alignment
                return 0
                
        except Exception:
            return 0

    def _score_rsi(self, data: Dict[str, Any]) -> float:
        """Score RSI momentum (40-70 = ideal range)"""
        try:
            rsi = data.get('rsi14', 50)  # Default to neutral if missing
            
            # Scoring based on checklist RSI ranges
            if 45 <= rsi <= 65:     # Ideal momentum zone
                return 4
            elif 40 <= rsi <= 75:   # Good momentum zone 
                return 3
            elif 35 <= rsi <= 80:   # Acceptable zone
                return 2
            elif 30 <= rsi <= 85:   # Marginal zone
                return 1
            else:                   # Extreme zones (too weak or exhausted)
                return 0
                
        except Exception:
            return 2  # Default moderate score

    def _score_support_distance(self, data: Dict[str, Any]) -> float:
        """Score stop loss distance (2-5% ideal range)"""
        try:
            # Calculate recent swing low from price history
            history = data.get('history', [])
            current_price = data.get('close', 0)
            
            if len(history) < 10 or current_price == 0:
                return 2  # Default if insufficient data
            
            # Find recent swing low (approximate)
            recent_low = min(history[-10:])  # Last 10 days minimum
            stop_distance_pct = (current_price - recent_low) / current_price * 100
            
            # Scoring based on checklist stop loss criteria
            if 3.0 <= stop_distance_pct <= 5.0:   # Ideal range
                return 4
            elif 2.0 <= stop_distance_pct <= 6.0: # Good range
                return 3
            elif 1.5 <= stop_distance_pct <= 7.0: # Acceptable range
                return 2
            elif 1.0 <= stop_distance_pct <= 8.0: # Marginal range
                return 1
            else:                                  # Too tight or too wide
                return 0
                
        except Exception:
            return 2  # Default moderate score

    def _calculate_fundamental_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate fundamental scores (limited by available data)"""
        scores = {}
        
        # Note: Many fundamentals require external data sources
        # For now, implement what we can with available data
        
        # 1. Sector Score (placeholder - would need sector mapping)
        scores['sector_score'] = self._score_sector(data)
        
        # 2. Liquidity Score (based on volume/market cap proxy)
        scores['liquidity_score'] = self._score_liquidity(data)
        
        # 3. Balance Sheet Score (placeholder - need external data)
        scores['balance_sheet_score'] = self._score_balance_sheet(data)
        
        # 4. Earnings Score (placeholder - need earnings data)
        scores['earnings_score'] = self._score_earnings(data)
        
        # 5. News Sentiment Score (placeholder - need news feed)
        scores['news_score'] = self._score_news_sentiment(data)
        
        return scores

    def _score_sector(self, data: Dict[str, Any]) -> float:
        """Score sector strength (placeholder implementation)"""
        # TODO: Implement sector classification and scoring
        # For now, return neutral score
        return 2.5

    def _score_liquidity(self, data: Dict[str, Any]) -> float:
        """Score liquidity based on volume patterns"""
        try:
            avg_volume = data.get('vol_avg20', 0)
            
            # Rough liquidity scoring based on average volume
            if avg_volume >= 5000000:    # Very high volume (mega-cap level)
                return 4
            elif avg_volume >= 1000000:  # High volume (large-cap level)  
                return 3
            elif avg_volume >= 500000:   # Medium volume (mid-cap level)
                return 2
            elif avg_volume >= 100000:   # Low volume (small-cap level)
                return 1
            else:                        # Very low volume
                return 0
                
        except Exception:
            return 2

    def _score_balance_sheet(self, data: Dict[str, Any]) -> float:
        """Score balance sheet health (placeholder)"""
        # TODO: Integrate with fundamental data source
        return 2.5  # Neutral score for now

    def _score_earnings(self, data: Dict[str, Any]) -> float:
        """Score earnings quality (placeholder)"""
        # TODO: Integrate with earnings data
        return 2.5  # Neutral score for now

    def _score_news_sentiment(self, data: Dict[str, Any]) -> float:
        """Score news sentiment (placeholder)"""
        # TODO: Integrate with news sentiment analysis
        return 2.5  # Neutral score for now

    def _check_red_flags(self, data: Dict[str, Any], tech_scores: Dict, fund_scores: Dict) -> List[str]:
        """Check for red flag conditions that mandate skipping the trade"""
        flags = []
        
        # Volume red flag
        if tech_scores.get('volume_score', 0) == 0:
            flags.append('volume_too_low')
            
        # RSI exhaustion red flag
        rsi = data.get('rsi14', 50)
        if rsi > 75:
            flags.append('rsi_exhausted')
            
        # Stop loss red flag
        if tech_scores.get('support_score', 2) == 0:
            flags.append('stop_too_wide')
            
        return flags

    def _generate_recommendation(self, overall_score: float, red_flags: List, tech_total: float, fund_total: float) -> Dict[str, str]:
        """Generate trading recommendation based on scores"""
        
        # Red flags override everything
        if red_flags:
            return {
                'action': 'SKIP',
                'reason': f"Red flags detected: {', '.join(red_flags)}",
                'confidence': 'HIGH'
            }
        
        # Score-based recommendations (following checklist guidelines)
        if overall_score >= 70:  # 7+/10 points scaled to 100
            return {
                'action': 'ENTER',
                'reason': 'High confidence setup - strong technical and fundamental scores',
                'confidence': 'HIGH',
                'position_size': 'FULL'
            }
        elif overall_score >= 50:  # 5-6/10 points scaled to 100
            return {
                'action': 'ENTER',
                'reason': 'Medium confidence - acceptable setup with some weaknesses', 
                'confidence': 'MEDIUM',
                'position_size': 'HALF'
            }
        else:  # <5/10 points
            return {
                'action': 'SKIP',
                'reason': 'Low confidence - too many weak indicators',
                'confidence': 'HIGH'
            }

    def _get_explanations(self) -> Dict[str, str]:
        """Return explanations for each indicator (for hover tooltips)"""
        return {
            'volume_score': "Volume Confirmation: Measures if breakout has institutional support. 1.5x+ average volume indicates real buying pressure vs. false breakout on low volume.",
            
            'resistance_score': "Resistance Quality: Evaluates how decisively price broke through resistance. Strong breakouts show 4-5%+ moves above resistance level with conviction.",
            
            'sma_alignment_score': "Moving Average Alignment: Checks trend health via SMA positioning. Golden alignment (Price > SMA20 > SMA50) with wide gaps indicates strong uptrend support.",
            
            'rsi_score': "RSI Momentum: Confirms momentum strength without exhaustion. RSI 40-70 range shows healthy momentum with room to run vs. overbought conditions above 75.",
            
            'support_score': "Stop Loss Distance: Evaluates risk management via recent swing low distance. Ideal 2-5% stop distance provides safety net without being stopped by noise.",
            
            'sector_score': "Sector Strength: Assesses whether stock operates in sector with tailwinds vs. headwinds. Strong sectors provide better odds of continued momentum.",
            
            'liquidity_score': "Liquidity Assessment: Measures ability to enter/exit positions efficiently. High volume stocks offer better execution and lower spreads for trading.",
            
            'balance_sheet_score': "Financial Health: Evaluates company's debt levels and liquidity position. Healthy balance sheets reduce bankruptcy risk and support sustainable growth.",
            
            'earnings_score': "Earnings Quality: Assesses recent earnings strength and forward guidance. Strong earnings justify breakouts while weak earnings suggest unsustainable moves.",
            
            'news_score': "News Sentiment: Identifies negative news that could derail breakout momentum. Clean news flow supports continued upward movement without sentiment headwinds."
        }

    def _generate_checklist_summary(self, tech_scores: Dict, fund_scores: Dict) -> Dict[str, str]:
        """Generate human-readable checklist summary"""
        
        def score_to_text(score: float) -> str:
            if score >= 3.5: return "✓ Excellent"
            elif score >= 2.5: return "✓ Good" 
            elif score >= 1.5: return "⚠ Weak"
            else: return "✗ Poor"
        
        return {
            'Volume Confirmation': score_to_text(tech_scores.get('volume_score', 0)),
            'Resistance Quality': score_to_text(tech_scores.get('resistance_score', 0)),
            'SMA Alignment': score_to_text(tech_scores.get('sma_alignment_score', 0)),
            'RSI Momentum': score_to_text(tech_scores.get('rsi_score', 0)),
            'Stop Loss Distance': score_to_text(tech_scores.get('support_score', 0)),
            'Sector Strength': score_to_text(fund_scores.get('sector_score', 0)),
            'Liquidity': score_to_text(fund_scores.get('liquidity_score', 0)),
            'Balance Sheet': score_to_text(fund_scores.get('balance_sheet_score', 0)),
            'Earnings Quality': score_to_text(fund_scores.get('earnings_score', 0)),
            'News Sentiment': score_to_text(fund_scores.get('news_score', 0))
        }

# Global validator instance
validator = BreakoutValidator()