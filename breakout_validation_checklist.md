# Pre-Trade Validation: Technical & Fundamental Filters for Breakout Stocks

## Overview

Before you enter ANY trade, ask yourself: "Is this a REAL breakout or a false breakout trap?" This checklist helps you avoid the 70% of trades that fail because traders ignore validation.

---

## SECTION 1: TECHNICAL VALIDATION (Confirm Real Breakout)

### 1.1 Volume Confirmation - THE MOST CRITICAL FILTER

**Why it matters**: 80% of false breakouts happen on LOW volume. Real breakouts have institutional buying pressure.

**Check this first:**

| Metric | What to Look For | NSE Context |
|--------|------------------|------------|
| **Breakout Volume** | 1.5-2x average volume | If avg volume is 5M shares, breakout should have 7.5M+ |
| **Volume trend** | Volume increasing over last 5 days | Not just one spike day |
| **Compare to average** | Last 20-day average volume | Use Kite's volume panel below chart |

**On Zerodha Kite:**
- Look at the volume bars (histogram below price chart)
- The bar on breakout day should be NOTICEABLY taller than recent bars
- If volume is similar to normal days = FAKE BREAKOUT, skip it

**Example:**
```
Average volume: 2,00,000 shares/day
Day 20 volume: 1,95,000 (normal)
Day 21 breakout volume: 5,00,000 (2.5x average) ✓ REAL BREAKOUT
→ Safe to enter

vs.

Average volume: 2,00,000 shares/day
Day 20 volume: 1,85,000 (normal)
Day 21 breakout volume: 2,10,000 (1.05x average) ✗ FAKE BREAKOUT
→ SKIP, avoid this trade
```

---

### 1.2 Resistance Level & Breakout Quality

**Check the resistance being broken:**

- **How long did price consolidate?** 
  - 5-10 days at resistance = weak (might snap back)
  - 20-30+ days at resistance = strong (built pressure) ✓
  
- **How decisively did it break?**
  - Broke 2-3% above resistance = weak
  - Broke 4-5%+ above resistance with volume = strong ✓

**On Kite Chart:**
1. Draw a horizontal line at resistance level
2. Check how many times price tested this level (4+ tests = stronger breakout)
3. Check distance price traveled after breakout (still rising, not dead bounce)

**Decision Rule:**
```
Strong Breakout = 
  • Resistance tested 3-5 times (not just once)
  • 20+ days of consolidation at resistance
  • Broke 4%+ on 2x volume
  • Price still rising 2-3 hours after breakout

Weak Breakout = Skip
  • Broke 1% on normal volume
  • First test of resistance (not repeated)
  • Price already exhausted (up 5% in one candle, now stalling)
```

---

### 1.3 Moving Average Alignment (Trend Health)

**This confirms the bigger trend is supporting the breakout:**

**Check on daily chart:**

1. **Price position relative to SMAs:**
   - Price > 20-day SMA > 50-day SMA > 200-day SMA = GOLDEN ALIGNMENT ✓
   - If SMAs are tangled or reversed = Weak trend, avoid
   
2. **SMA spacing** (are they spreading apart?):
   - 20 SMA pulling away from 50 SMA = Strong uptrend ✓
   - 20 SMA converging toward 50 SMA = Trend weakening, be cautious
   
3. **Angle of 20-day SMA**:
   - Steep upward angle = Strong momentum ✓
   - Flat or slightly declining = Weak momentum, avoid

**On Kite:**
- Look at your chart with 20, 50, 200 SMAs visible
- Do they form a "stack" with largest gaps = Golden trend

---

### 1.4 RSI Momentum Check (Is there still gas in the tank?)

**The breakout happens, but RSI tells you if momentum is REAL or EXHAUSTED:**

| RSI Level | Meaning | Trade Confidence |
|-----------|---------|------------------|
| **Below 40** | Momentum too weak, breakout likely false | ✗ SKIP |
| **40-60** | Healthy momentum, room to run | ✓ ENTER |
| **60-75** | Strong momentum, but getting extended | ✓ ENTER (tighter stops) |
| **Above 75** | Likely exhausted, reversal risk high | ✗ SKIP |

**Watch for RSI pattern:**
- RSI **rising through 50 at breakout** = Strong (price breaking resistance AND momentum accelerating)
- RSI **already above 70 when breakout happens** = Likely exhausted, skip

**On Kite:**
- Look at RSI panel below chart
- At breakout moment, is RSI rising or falling? Rising = good sign

---

### 1.5 Support Below Entry (Safety Net)

**Where's your bailout point? Before you buy, know where you'll get stopped:**

**Check for:**
1. **Recent swing low** (last 5-10 days): This is your natural hard stop
2. **Distance to that swing low**: 
   - 2-3% away = Tight, might get stopped on noise
   - 4-5% away = Comfortable, fewer false touches
   - >6% away = Stop too wide, risk too large

**Calculate Stop Loss:**
```
Entry price: ₹1,000
Recent swing low: ₹965
Distance: ₹35 (3.5% below entry)
Risk: 3.5% ✓ Acceptable

vs.

Entry price: ₹1,000
Recent swing low: ₹950
Distance: ₹50 (5% below entry)
Risk: 5% ⚠ On the edge, position size should be smaller

vs.

Entry price: ₹1,000
Recent swing low: ₹920
Distance: ₹80 (8% below entry)
Risk: 8% ✗ TOO WIDE, skip this trade
```

**On Kite:**
- Draw horizontal line at recent swing low
- Measure distance to your entry
- If >6%, reduce position size or skip

---

### 1.6 Breakout Timing Within Trend (Cycle Check)

**Did the stock already run hard from low?**

- Stock broke out from ₹500 to ₹600 last month = TIRED (already had a 20% move)
- Stock consolidated ₹500-510 for 30 days, now breaks to ₹520 = FRESH (early in new trend) ✓

**On Kite:**
- Zoom out to 3-month chart
- See if this breakout is "early" in a trend or "late" in an existing rally
- Early = better risk/reward, more room to run
- Late = less upside, more downside risk

**Decision Rule:**
```
Fresh Breakout (BEST):
  • Stock base for 30+ days
  • Then breaks out just 2-4% from base
  • Lots of room above breakout level

Exhausted Breakout (SKIP):
  • Stock already up 15-20% this month
  • Now breaking out at 52-week highs
  • Limited room to run before hitting resistance
```

---

### 1.7 Weekly Chart Confirmation (See the Bigger Picture)

**Switch to weekly chart:**

1. **Is weekly chart also in uptrend?**
   - Week price above 20 SMA = Good, breakout aligns with bigger trend ✓
   - Weekly price below 20 SMA = Bad, daily breakout against weekly trend ✗

2. **Is there weekly resistance near the breakout?**
   - If weekly resistance at ₹1,050 and daily breaking out at ₹1,010, you have ₹40 room = Limited ✗
   - If next weekly resistance at ₹1,200, you have ₹190 room = Good ✓

**Why this matters:** Weekly breakouts have 10x better success rate than daily-only setups.

---

### 1.8 Relative Strength vs Market (Is stock outperforming?)

**Compare stock performance vs NIFTY 50:**

**On Zerodha:**
1. Add NIFTY 50 to your watchlist alongside the stock
2. Check: Is stock up 2% today while NIFTY down 0.5%? = Stock has strength ✓
3. Or: Stock up 0.5% while NIFTY up 3%? = Stock lagging, weak relative strength ✗

**Decision Rule:**
```
GOOD: Stock breakout +3% while NIFTY +0.5% (stock showing real strength)
BAD: Stock breakout +0.5% while NIFTY +2.5% (NIFTY carrying it, not real strength)
UGLY: Stock breakout +2% while NIFTY -1% (but breakout fails next day after market recovers)
```

---

## SECTION 2: FUNDAMENTAL VALIDATION (Is Company Safe?)

### 2.1 Sector & Trend (Tailwinds vs Headwinds)

**Is this stock in a HOT sector or a dying one?**

**Check NSE stock information:**

1. **Go to stock detail page on Kite** → Click "Info" tab
2. **Sector**: Look for what sector the stock is in

**Good sectors (2024-2025 tailwinds):**
- Information Technology (AI boom, outsourcing demand)
- Banking & Financials (rising rates, credit growth)
- Renewable Energy (government push, ESG demand)
- FMCG (consumption growth)
- Pharmaceuticals (exports, aging population)

**Risky sectors (headwinds):**
- Coal/Traditional Energy (phase-out risk)
- Automobile (EV transition pain)
- Textile (import competition)
- Real Estate (over-leveraged)

**Decision Rule:**
- Trading with sector tailwinds = Better odds ✓
- Trading against sector headwinds = Unnecessary risk ✗

---

### 2.2 Company Size & Liquidity (Can You Exit?)

**NSE stocks in your breakout setup—are they liquid enough?**

**Check:**

| Market Cap | Trading Liquidity | For ₹50k-₹500k Trades |
|-----------|-------------------|----------------------|
| **Mega-cap (>₹5,00,000 Cr)** | Very high | ✓ Perfect (RELIANCE, TCS, INFY) |
| **Large-cap (₹1,00,000-₹5,00,000 Cr)** | High | ✓ Good |
| **Mid-cap (₹20,000-₹1,00,000 Cr)** | Medium | ✓ Okay for 50k-100k positions |
| **Small-cap (<₹20,000 Cr)** | Low | ✗ Risky for exits, wider spreads |

**On Zerodha Kite:**
- Open stock → Check current bid-ask spread
- If spread is ₹0.20 or less = Good liquidity ✓
- If spread is ₹1+ = Poor liquidity ✗

**Why it matters:** Small-caps with poor liquidity can trap you. You want to exit and can't at a reasonable price.

---

### 2.3 Debt & Balance Sheet (Is Company Financially Healthy?)

**Quick financial health check (5 minutes):**

**Get this data from:**
- Zerodha Kite → Stock info → Fundamentals tab
- Or: Moneycontrol.com, NSE website

**Check these metrics:**

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| **Debt/Equity Ratio** | <1.0 | 1.0-2.0 | >2.0 ✗ |
| **Current Ratio** | >1.5 | 1.0-1.5 | <1.0 ✗ |
| **Promoter Holding** | >40% | 30-40% | <30% ⚠ |

**What this means:**

- **Debt/Equity > 2.0**: Company is overleveraged. If earnings disappoint, stock crashes. SKIP.
- **Current Ratio < 1.0**: Company can't pay short-term obligations. Liquidity crisis risk. SKIP.
- **Promoter holding <25%**: Weak insider confidence. SKIP.

**Decision Rule:**
```
Safe to trade:
  • Debt/Equity < 1.5
  • Current Ratio > 1.2
  • Promoter > 30%

Risky, avoid:
  • Any of above thresholds crossed
```

---

### 2.4 Recent Earnings & Guidance (Is Breakout Justified?)

**Did the stock breakout for a good reason, or is it hype?**

**Check:**

1. **Recently announced earnings?**
   - Stock breakout after good earnings = Real breakout ✓
   - Stock breakout after mediocre earnings = Might be hype/short-covering ✗

2. **Forward guidance positive?**
   - Company expects revenue/profit growth = Real momentum ✓
   - Company giving cautious guidance = Breakout might be short-lived ✗

3. **When is next earnings?**
   - Breakout 10 days before earnings = High risk (might tank on results)
   - Breakout just after earnings = Safer (already priced in results) ✓

**On Zerodha:**
- Go to stock info → Check "Events" tab for earnings dates
- Read company announcements (quarterly results, board meetings)

**Decision Rule:**
```
SAFE ENTRY:
  • Breakout after strong earnings announcement
  • Company gave positive forward guidance
  • Next earnings 60+ days away (no imminent news risk)

RISKY ENTRY:
  • Breakout just before earnings
  • Last earnings were mediocre
  • Multiple analyst downgrades recently
```

---

### 2.5 News & Announcements (Any Red Flags?)

**Before you enter, scan for BAD NEWS:**

**Check (takes 2 minutes):**

1. **Go to NSE website** → Search stock → News section
2. **Moneycontrol/BS/ET** → Search stock name
3. **Look for:**
   - Regulatory action/penalties
   - Accounting issues
   - Insider selling (promoters dumping shares)
   - Lawsuits
   - Supply chain issues

**Red flags that should stop you:**

```
✗ STOP: "Promoters sold 5% stake"
✗ STOP: "Income Tax raid on offices"
✗ STOP: "Accounting restatement announced"
✗ STOP: "Bankruptcy filing"
✗ STOP: "CEO suddenly resigned"
✗ STOP: "Major customer lost contract"
```

**Proceed with caution:**
```
⚠ CAUTION: "Union strike at factories"
⚠ CAUTION: "New regulatory framework expected"
⚠ CAUTION: "Currency headwinds"
⚠ CAUTION: "Supply shortage (temporary)"
```

**On Zerodha Kite:**
- Stock info → News tab shows recent announcements
- Read headline—if it's negative, your breakout might be fighting bad sentiment

---

### 2.6 Insider Trading & Promoter Activity

**Are the smart money (promoters/insiders) buying or selling?**

**Check on NSE website:**
- NSE → Stock → Bulk deals & Block deals section
- Look for promoter buying = Bullish signal ✓
- Look for promoter selling = Warning signal ⚠

**Decision Rule:**
```
VERY BULLISH: Promoter buying into strength (buying near breakout)
BULLISH: Promoter steady, no selling
CAUTION: Promoter selling into strength (selling right at breakout)
RED FLAG: Promoter dumping large quantities
```

---

### 2.7 Analyst Consensus & Price Targets

**What do professionals think about this stock?**

**Quick check (on Moneycontrol):**
1. Search stock name
2. Look at "Analyst Recommendations" section
3. Count: How many "BUY" vs "SELL" vs "HOLD"

**Decision Rule:**

```
GOOD: 10 BUY, 2 HOLD, 0 SELL (80% bullish)
OKAY: 6 BUY, 4 HOLD, 1 SELL (60% bullish)
CAUTION: 4 BUY, 5 HOLD, 2 SELL (40% bullish)
SKIP: 2 BUY, 4 HOLD, 5 SELL (20% bullish)
```

**Also check:**
- **Average price target** vs current price
- If price target is ₹1,000 and stock is at ₹950, breakout makes sense ✓
- If price target is ₹1,200 and stock is at ₹1,500, stock is overvalued ✗

---

## SECTION 3: COMBINED DECISION MATRIX

### Quick Go/No-Go Decision Framework

**Use this checklist before EVERY trade:**

```
TECHNICAL SCORE (5 points possible):
☐ Volume 1.5x+ average (1 pt)
☐ Resistance tested 3+ times before breakout (1 pt)
☐ Price > 20 SMA > 50 SMA (1 pt)
☐ RSI 40-70, not exhausted (1 pt)
☐ Stop loss 2-5% below entry (1 pt)

FUNDAMENTAL SCORE (5 points possible):
☐ Stock in strong sector (1 pt)
☐ Market cap >₹50,000 Cr (1 pt)
☐ Debt/Equity <1.5, healthy balance sheet (1 pt)
☐ Recent good earnings OR positive guidance (1 pt)
☐ No major red flag news (1 pt)

DECISION:
Score 7+/10 = ENTER ✓ High confidence
Score 5-6/10 = ENTER with HALF position (medium confidence)
Score <5/10 = SKIP, wait for better setup

ABSOLUTE KILL SIGNALS (Skip regardless of score):
✗ Volume less than average
✗ Debt/Equity >2.0
✗ Bad news announced
✗ RSI >75
✗ Stop loss >6% away
```

---

## SECTION 4: SPECIFIC CHECKS ON ZERODHA KITE

### Finding This Info Quickly on Kite

**Step 1: Open Stock**
- Search stock → Click to open detail page

**Step 2: Gather Technical Data**
- Click "Chart" → See volume, SMAs, RSI
- Draw resistance line where breakout occurred
- Note the volume comparison

**Step 3: Check Fundamentals**
- Click "Info" tab → Scroll down
- Find: Sector, Market Cap, P/E, Dividend Yield
- Look at "Technicals" subsection for debt info if available

**Step 4: News Check**
- On Info tab, find "News" or "Events"
- Scan last 5 news items for red flags

**Step 5: Compare to Market**
- Add NIFTY 50 to watchlist alongside stock
- Check % gain: Stock vs NIFTY today

---

## SECTION 5: PRACTICAL EXAMPLES

### Example 1: RELIANCE Breakout ✓ ENTER

**Setup:**
- Price breaks ₹2,850 (resistance tested 4 times)
- Volume: 45M shares (2.2x average of 20M) ✓
- 20 SMA: ₹2,800, 50 SMA: ₹2,700 (well stacked) ✓
- RSI: 58 (healthy, not exhausted) ✓
- Swing low: ₹2,790 (4% below entry) ✓

**Fundamentals:**
- Sector: Energy/Financials (strong) ✓
- Market cap: ₹18,00,000 Cr (mega-cap, very liquid) ✓
- Debt/Equity: 0.8 (healthy) ✓
- Recent earnings: Profit up 12% YoY ✓
- News: None negative ✓

**Score: 9/10 → ENTER with full position ✓**

---

### Example 2: TCS Breakout ⚠ ENTER CAREFULLY

**Setup:**
- Price breaks ₹3,650 (resistance tested 2 times only) ⚠
- Volume: 8M shares (1.1x average of 7.5M) ⚠ Weak volume
- RSI: 72 (getting exhausted) ⚠
- 20 SMA at ₹3,600, 50 SMA at ₹3,550 ✓
- Swing low: ₹3,600 (5% below) ✓

**Fundamentals:**
- Sector: IT (strong) ✓
- Market cap: ₹13,00,000 Cr (mega-cap) ✓
- Debt/Equity: 0.2 (excellent) ✓
- Recent earnings: Guidance tepid ⚠
- Next earnings: 15 days away ⚠

**Score: 5.5/10 → ENTER with HALF position only ⚠**
- Use smaller position size
- Tighter stop loss (3% instead of 4%)
- Exit quicker if momentum stalls

---

### Example 3: Unknown Mid-Cap Stock ✗ SKIP

**Setup:**
- Price breaks ₹245 (first test of resistance)
- Volume: 50k shares (0.8x average!) ✗ Below average volume
- RSI: 68 ⚠
- SMAs present but loosely spaced
- Swing low: ₹220 (10% below entry!) ✗ Too far

**Fundamentals:**
- Sector: Real Estate (headwinds) ✗
- Market cap: ₹8,000 Cr (small-cap) ⚠
- Debt/Equity: 2.3 (overleveraged) ✗
- Recent earnings: Revenue declining ✗
- News: "Regulatory notice issued" ✗

**Score: 2/10 → SKIP, not worth the risk ✗**

---

## SECTION 6: Pre-Trade Checklist Template

**Print this or save to phone. Check before EVERY trade:**

```
STOCK: _______________  DATE: ________

TECHNICAL (circle one number per row):
Volume          1-Poor  2-Okay  3-Good  4-Excellent
Resistance      1-Weak  2-Okay  3-Strong  4-Very Strong
SMAs aligned    1-No  2-Partial  3-Yes  4-Perfect
RSI zone        1-Bad  2-Caution  3-Good  4-Ideal
Stop distance   1-Too wide  2-Wide  3-Good  4-Tight

FUNDAMENTAL (circle one):
Sector trend    1-Bad  2-Neutral  3-Good  4-Excellent
Liquidity       1-Poor  2-Medium  3-Good  4-Excellent
Balance sheet   1-Weak  2-Okay  3-Strong  4-Excellent
Recent earnings 1-Bad  2-Okay  3-Good  4-Excellent
News sentiment  1-Negative  2-Neutral  3-Positive

RED FLAGS (check if present):
☐ Volume < 1x average
☐ RSI > 75
☐ Stop loss > 6%
☐ Debt/Equity > 2
☐ Bad news today
☐ Earnings in 10 days

TOTAL TECHNICAL SCORE: ___/16
TOTAL FUNDAMENTAL SCORE: ___/16

DECISION:
Score 24+ = ENTER full position ✓
Score 18-23 = ENTER half position ⚠
Score <18 = SKIP ✗

Red flags present? If YES = SKIP regardless of score
```

---

## Final Summary

Before trading any breakout:

1. **Volume must be 1.5x+ average** (non-negotiable)
2. **Stop loss 2-5% below entry** (setup your risk first)
3. **SMAs aligned upward** (trend supporting breakout)
4. **RSI 40-70** (momentum healthy, not exhausted)
5. **Sector in uptrend** (tailwinds matter)
6. **No major red flag news** (read stock news 2 minutes)
7. **Company financially healthy** (debt ratio <1.5)
8. **Analyst consensus bullish** (professionals agree)

**Remember:** The best trades come from patience and validation, not speed. Wait for setups that pass 80%+ of these checks. Those trades will make 15-25% while you sleep. The 50-50 setups that only pass 50% of checks will wipe out your profits.