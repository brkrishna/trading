# SMA + RSI Trading Strategy on Zerodha Kite (NSE)

## Part 1: Zerodha Kite Setup for Technical Analysis

### Accessing Charts on Kite
1. **Login to Kite**: https://kite.zerodha.com with your credentials
2. **Search for Stock**: 
   - Click the search icon or use Ctrl+K
   - Type stock name (e.g., "RELIANCE", "TCS", "INFY")
   - Press Enter
3. **Open Chart**:
   - Click on the stock name to open detail view
   - Click "Chart" button (bottom section) or the candlestick icon
   - This opens the full charting interface

### Setting Up Your Workspace
- In the chart view, you'll see a toolbar at the top with timeframe options
- **Select "1 day" (daily candles)** for your 2-4 week trades
- For faster trades, you can use 4-hour or hourly, but daily is more reliable for SMA signals

---

## Part 2: Adding Indicators to Your Chart

### Adding Simple Moving Average (SMA)

**Steps:**
1. In the chart, look for the **indicator icon** (usually a waveform/line icon in toolbar)
2. Click **"Add indicator"** or the **"+" button**
3. Search for **"SMA"** or **"Moving Average"**
4. A window will appear asking for settings:
   - **Period**: 20 (for fast SMA)
   - **Source**: Close (uses closing price)
   - **Color**: Pick a color (e.g., blue)
5. Click **Add**
6. **Repeat the process** for 50-day SMA:
   - Add second SMA with Period: 50
   - Choose different color (e.g., red)

**What you see:**
- Two lines on your chart: 20-day SMA (blue, faster) and 50-day SMA (red, slower)
- When price is above both, you have an uptrend ✓

### Adding RSI (Relative Strength Index)

**Steps:**
1. Click **"Add indicator"** again
2. Search for **"RSI"**
3. Settings window appears:
   - **Period**: 14 (standard, this is RSI(14))
   - **Color**: Pick one (e.g., orange)
4. Click **Add**

**What you see:**
- A separate panel below the price chart showing a line between 0-100
- 70+ = Overbought (red zone)
- 30- = Oversold (green zone)
- 40-70 = Good entry zone (where we want to trade)

### Optional: Add Bollinger Bands for Volume Confirmation
1. Add indicator: **"Bollinger Bands"**
2. **Period**: 20
3. This helps confirm price rejection at moving averages

---

## Part 3: Finding Trading Setups on NSE Stocks

### Step 1: Identify Potential Stocks
**In Zerodha Kite:**
1. Go to **Watchlist** (left panel)
2. Create a new watchlist: Click **"Create Watchlist"** → Name it "Trading Setup 1"
3. **Popular NSE stocks for momentum trading**:
   - RELIANCE, TCS, INFY, WIPRO (large-cap, liquid)
   - BAJAJFINSV, AXISBANK, ICICIBANK (financial sector)
   - WIPRO, LT, HDFCBANK (trending stocks)
   - Or use NSE indices like NIFTY 50 to scan

### Step 2: Spot the SMA + RSI Setup

**Open daily chart for a stock and check for:**

✓ **Uptrend Confirmed:**
- Price is above both 20-day and 50-day SMA
- 20-day SMA is above 50-day SMA (lines separated, not tangled)

✓ **Momentum in Setup Zone:**
- RSI is between 40-70 (not below 30, not above 80)
- RSI is rising or steady (not declining sharply)

✓ **Entry Trigger (Pick one):**
- **Pull-back Entry**: Price touched 20-day SMA and bounced back up (creates a "V" shape on chart)
- **Breakout Entry**: Price broke above recent resistance level while RSI rose through 50
- **Volume Confirmation**: Look for increasing volume on the bounce (wider bars on volume panel)

### Step 3: Use Kite's Drawing Tools for Entry Planning

**In Kite chart:**
1. Click the **"Draw" or paintbrush icon** in toolbar
2. Use **"Horizontal Line"** tool:
   - Draw line at recent swing low (where you'll place hard stop loss)
   - Draw line at your target exit price (+10% above entry)
3. Use **"Trend Line"** tool:
   - Connect recent lows to see if stock bounces along a support line
   - Better entry when price touches this line

---

## Part 4: Placing Your Entry Order on Kite

### Before Placing Order - Calculate Position Size

**Example for NSE:**
- Account size: ₹1,00,000
- Risk per trade (2%): ₹2,000
- Stock price: ₹500
- Stop loss level: ₹485 (3% below entry)
- Risk per share: ₹500 - ₹485 = ₹15
- Position size: ₹2,000 ÷ ₹15 = 133 shares ✓

**Note for NSE:** Lot sizes don't apply to equity (stocks). You can buy any number of shares. Lot sizes only apply to derivatives/F&O.

### Placing Buy Order on Kite

**Steps:**

1. **Open the Stock**: Search and click on the stock name
2. **Click the "Buy" button** (green, on the right panel):
   - A buy order panel opens

3. **Fill in Order Details**:
   - **Quantity**: Enter calculated shares (e.g., 133)
   - **Price**: 
     - For limit order (recommended): Enter your planned entry price (e.g., ₹500.50)
     - For market order: Leave blank or use current price (less safe, gets filled immediately)
   - **Order Type**: Select **"Regular"** (not after-market, not AMO unless market is closed)

4. **Select Execution Type**: Choose **"Limit"**
   - This ensures you buy at your planned price, not above it

5. **Review**:
   - Check: Quantity, Price, Total (should match your calculation)
   - Example: 133 shares × ₹500 = ₹66,500

6. **Click "Buy"** → Review popup appears
   - Verify all details
   - Click **"Confirm"** (you may need to enter a PIN or 2FA if set)

**Your order is now placed!** It will fill when price hits ₹500.50 (if you used limit).

### Setting Hard Stop Loss (Critical - Do This First!)

**VERY IMPORTANT: Protect yourself BEFORE trade moves against you**

**Steps:**

1. **After buy order is confirmed**, the stock appears in your Holdings
2. **Open the stock** and click **"Sell" button** (red)
3. **Fill Sell Order (This is your STOP LOSS):**
   - **Quantity**: Same as buy (133 shares)
   - **Price**: Your stop loss level (₹485)
   - **Order Type**: **"Stop-Limit"** or **"Stop-Market"**
     - Stop-Limit: You set stop price (₹485) and limit price (₹485)
     - Stop-Market: Stops at ₹485 but sells at best available price (might be lower)
   - **Recommend Stop-Market for cleaner exits**

4. **Advanced Tab** (optional):
   - Check if there's an option to set "Trailing Stop Loss"
   - If available: Set trailing stop % (e.g., 5%)
   - If NOT available in buy order: You'll manually adjust this later

5. **Click "Sell"** and **"Confirm"**

**Result:** Your hard stop loss is now active. If price drops to ₹485, you automatically sell all 133 shares.

---

## Part 5: Setting Profit Targets on Kite

### Setting +10% Target Exit (Half Position)

**For ₹500 entry, target is ₹550 (+10%)**

**Steps:**

1. **Open the stock** and click **"Sell"** button
2. **Fill Sell Order**:
   - **Quantity**: 50% of position (e.g., 67 shares out of 133)
   - **Price**: ₹550 (your +10% target)
   - **Order Type**: **"Limit"**
   - **Execution**: **"Regular"**
3. **Review and Confirm**

**Result:** When price hits ₹550, half your position (67 shares) automatically sells, locking in ₹3,350 profit.

### For Remaining 50% - Trailing Stop Loss

**After your +10% target sells, 66 shares remain with hard stop at ₹485:**

**Steps:**

1. **Modify the stop loss order** from ₹485 to a trailing structure:
   - You now have 66 shares still in position
   - Original stop: ₹485 (but price is now ₹550, so this is outdated)

2. **Cancel existing stop order**:
   - Go to "Orders" section (bottom left)
   - Find your pending stop-loss order
   - Click on it → Select **"Cancel"**

3. **Place new trailing stop order**:
   - Click **"Sell"** on the stock
   - **Quantity**: 66 (remaining shares)
   - **Price**: ₹521.50 (5% below current ₹550)
   - **Order Type**: **"Regular" (Limit)**
   - This acts as your trailing stop floor

4. **Update this manually** as price rises:
   - If price rises to ₹560 → Update stop to ₹532
   - If price rises to ₹570 → Update stop to ₹541.50
   - Each time price reaches new high, adjust stop higher by 5%

**Alternative: Use Kite API or Bracket Orders for Auto-Trailing**
- Zerodha allows "Bracket Orders" which can auto-adjust stops
- But for NSE equity (not F&O), manual trailing is simpler

---

## Part 6: Step-by-Step Trade Execution Example

### Setup: Trading RELIANCE on NSE

**Chart Analysis (using daily timeframe):**
- Current Price: ₹2,800
- 20-day SMA: ₹2,750 ✓ (price above)
- 50-day SMA: ₹2,700 ✓ (below 20-day)
- RSI: 55 ✓ (in 40-70 zone)
- Volume: Recent volume spike on bounce ✓
- Setup: Price bouncing from 20-day SMA

**Trading Plan:**

| Element | Value |
|---------|-------|
| Account Size | ₹5,00,000 |
| Risk per Trade (2%) | ₹10,000 |
| Entry Price | ₹2,800 |
| Stop Loss | ₹2,716 (3% below) |
| Risk Per Share | ₹84 |
| Position Size | 119 shares (₹10,000 ÷ ₹84) |
| First Target (10%) | ₹3,080 (sell 60 shares) |
| Trailing Stop (5%) | Adjust manually |
| Max Hold | 20-25 days |

### Execution on Zerodha Kite:

**Day 1 - Entry:**

1. **Login to Kite** at 9:15 AM (market open)
2. **Search "RELIANCE"** → Click to open
3. **Place Buy Order**:
   - Quantity: 119
   - Price: ₹2,800 (limit)
   - Order Type: Limit
   - Click Buy → Confirm
   - Status: Pending (waiting to fill)

4. **Place Hard Stop Loss** (CRITICAL):
   - Click Sell
   - Quantity: 119
   - Price: ₹2,716 (stop-market)
   - Order Type: Stop-Market
   - Click Sell → Confirm
   - Status: This order waits until price drops to ₹2,716

5. **Place +10% Target**:
   - Click Sell
   - Quantity: 60 (50% position)
   - Price: ₹3,080
   - Order Type: Limit
   - Click Sell → Confirm

**Note:** All three orders are now active:
- Buy at ₹2,800 (waiting)
- Sell 60 @ ₹3,080 (waiting)
- Sell 119 @ ₹2,716 as stop loss (safety net)

**Day 2 - Price moves to ₹2,810:**
- Your buy fills at ₹2,800 ✓ (or close to it)
- Stop loss order is now active (will trigger if price drops to ₹2,716)
- Monitor chart: Check if RSI stays above 50

**Day 5 - Price reaches ₹3,080:**
- Your 60-share sell order executes ✓
- Profit locked in: (₹3,080 - ₹2,800) × 60 = ₹16,800
- **59 shares remain** with stop loss at ₹2,716

**Now Activate Trailing Stop for Remaining 59 shares:**
- Cancel existing stop at ₹2,716
- Price is at ₹3,080, so set new trailing stop at ₹2,926 (5% below)
- Monitor price rise daily and adjust stop upward

**Day 8 - Price rises to ₹3,150:**
- Update trailing stop: ₹3,150 × 0.95 = ₹2,992.50

**Day 12 - Price drops to ₹3,000:**
- Trailing stop at ₹2,992.50 is NOT hit yet

**Day 15 - Price rises to ₹3,200:**
- Update trailing stop: ₹3,200 × 0.95 = ₹3,040

**Day 18 - Price drops sharply to ₹3,020:**
- Price hits trailing stop at ₹3,040? NO, it's still above
- Price is ₹3,020, stop is ₹3,040

**Day 20 - Price continues falling to ₹3,035:**
- Your trailing stop at ₹3,040 is hit ✓
- Remaining 59 shares sell at ₹3,040 (approximately)
- Profit on this portion: (₹3,040 - ₹2,800) × 59 = ₹14,160

**Total Trade Result:**
- First exit: ₹16,800 profit (60 shares)
- Second exit: ₹14,160 profit (59 shares)
- **Total Profit: ₹30,960 on ₹3,38,000 invested (9.2% return in 20 days)**
- Hard stop loss never hit ✓ (capital protected)

---

## Part 7: Monitoring and Adjusting Stops on Kite

### Check Your Active Orders

1. **Open Kite** → Bottom left shows **"Orders"** and **"Holdings"**
2. **Click "Orders"**: Shows all pending buy/sell orders
3. **Click "Holdings"**: Shows stocks you currently own and their status

### Modifying Stop Loss Order

**If you want to adjust your trailing stop:**

1. **Go to Orders section**
2. **Find your sell (stop) order** for that stock
3. **Click on it** → Options appear:
   - "Modify" (change price/quantity)
   - "Cancel" (remove order)
4. **Click "Modify"**:
   - Change Price to new trailing stop level
   - Click "Update" → Confirm
5. **New stop price is now active**

### Real-Time Monitoring Checklist

**Check Daily (at 3:25 PM before market close):**
- [ ] Is price still above 20-day SMA? (If no, consider exiting)
- [ ] Is RSI above 50? (If drops below 50, momentum weakening)
- [ ] Has price hit new high? (If yes, adjust trailing stop upward)
- [ ] Days held? (If over 20 days and profit < 10%, consider exiting to redeploy capital)
- [ ] Did any news release badly impact the stock? (Exit if fundamentals change)

---

## Part 8: Common Zerodha Kite Features & Tips

### Best Times to Trade on NSE

- **9:15 AM - 9:30 AM**: Opening 15 minutes (volatile, avoid)
- **9:30 AM - 12:00 PM**: Morning session (good momentum, clear trends)
- **12:00 PM - 2:30 PM**: Afternoon (quieter, wider spreads)
- **2:30 PM - 3:30 PM**: Closing hour (volatility spikes)
- **3:15 PM - 3:30 PM**: Final 15 minutes (avoid entry, good exits)

### Useful Kite Tools for Your Strategy

1. **Watchlist Management**:
   - Create separate watchlists: "Trending Stocks", "Active Orders", "Monitoring"
   - Add stocks with strong technicals for quick reference

2. **Alerts** (Kite app has this):
   - Set price alerts on stocks you're watching
   - Get notification when stock hits key levels (RSI 50, SMA touchpoints)

3. **GTT Orders** (Good Till Triggered - on Kite app):
   - Set orders that trigger even if market is closed
   - Example: "Sell RELIANCE at ₹2,750" triggers at market open if price was ₹2,800 yesterday
   - Useful for overnight positions

4. **Advanced Charts** (Kite Pro has more indicators):
   - Multiple timeframes simultaneously
   - More drawing tools, better charting

### Spreadsheet Tracking (Important for Learning)

**Create a Google Sheet to track every trade:**

| Date | Stock | Entry | Target | Stop | Qty | Exit Price | P&L | Days | Notes |
|------|-------|-------|--------|------|-----|-----------|-----|------|-------|
| Oct 20 | RELIANCE | 2800 | 3080 | 2716 | 119 | 3040 | +30,960 | 20 | RSI helped timing |
| Oct 22 | TCS | 3500 | 3850 | 3395 | 85 | 3350 | -12,750 | 8 | Entered too late in trend |

**Track:**
- Win rate (% of profitable trades)
- Average profit per trade
- Which setups worked best
- What signals failed

---

## Part 9: Important Notes for NSE Trading

### Brokerage & Costs (Zerodha)

- **Equity brokerage**: Flat ₹20 per order (very cheap)
- **No impact on 10% profit goal**: ₹20 brokerage is minor vs ₹30,000+ profits

### Market Hours
- **NSE opens**: 9:15 AM
- **NSE closes**: 3:30 PM (4:00 PM for order settlement)
- **Can't place intraday orders before 9:15 AM** (use AMO if needed)

### Settlement
- **T+1**: You can use profits to trade next day
- **T+2**: Money hits your bank 2 days later

### Tax Implications
- **Short-term capital gains**: <2 years held = Added to income tax (not ideal)
- **Long-term capital gains**: >1 year held = 20% with indexation benefit
- **Your <30-day trades are short-term**: Track for tax season

### GST on Brokerage
- Zerodha charges GST on top of ₹20 brokerage (~₹3.60 extra)

---

## Part 10: Troubleshooting Common Issues

### Order Not Filling
- **Problem**: Limit buy order at ₹2,800 but stock only reaches ₹2,805
- **Solution**: Lower your entry price slightly, or use market order if price is very close

### Stop Loss Got Hit Unexpectedly
- **Problem**: Stock dipped to stop, then recovered
- **Solution**: 
  - Use 3% stops instead of 2% (wider, fewer false touches)
  - Place stops below swing lows, not at round numbers
  - Check volume: If volume is low, wider spreads cause false touches

### Can't See Trailing Stop in Kite
- **Problem**: Kite doesn't have built-in auto-trailing stops for equity
- **Solution**: Manually adjust stops as price rises (takes 5 seconds per adjustment)
- **Or**: Use Kite API if you're technical, or consider bracket orders on F&O instead

### RSI Indicator Missing
- **Problem**: Searched "RSI" but doesn't appear
- **Solution**: 
  - Kite has it as "Relative Strength Index"
  - Or search "14 RSI"
  - Update Kite to latest version if it still doesn't appear

---

## Quick Reference: Complete NSE Trading Workflow

1. **Morning (9:30 AM)**: Open Kite, scan your watchlist for SMA + RSI setups
2. **Setup Check**: Confirm uptrend, RSI 40-70, entry trigger visible
3. **Calculate Position Size**: Risk 2% of account ÷ stop distance = shares
4. **Place Buy Limit Order**: Your planned entry price
5. **IMMEDIATELY Place Stop-Market Order**: Your hard stop loss (same quantity)
6. **Place Sell Limit Order**: 50% position at +10% target
7. **Daily Monitoring**: Check if price > SMA, RSI > 50, adjust trailing stop if needed
8. **At +10% Target**: Half position sells automatically, activate trailing stop on remaining 50%
9. **Exit Remaining**: Either trailing stop hits, or day 20 arrives, or momentum dies (RSI < 50)
10. **Log Trade**: Record in spreadsheet for analysis and learning

---

**Remember**: Consistency beats perfection. You don't need 100% win rate. Even 40% win rate with proper risk management makes money if your winners are 2x your losses. Trade with discipline, follow the rules, and compound your gains over time.**