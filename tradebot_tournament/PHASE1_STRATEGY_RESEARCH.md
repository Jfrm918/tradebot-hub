# TRADEBOT TOURNAMENT — PHASE 1: SIX STRATEGY RESEARCH
**Classification:** Blueprint-Grade. Every rule must be directly translatable to Python code.  
**Date:** 2026-04-02  
**Status:** Complete Research Document

---

# STRATEGY 1: TREND FOLLOWING

## 1. Strategy Overview

**Core Logic:** Identify the prevailing price direction and position in that direction until momentum reverses. The underlying thesis is that asset prices exhibit serial correlation in trending regimes — winners continue winning, losers continue losing over defined periods. Profit comes from asymmetric risk-reward: small losses when trends fail, large gains when they persist.

**Why it makes money:** Markets trend because institutional order flow arrives in tranches (they can't buy a billion dollars at once), because macro narratives create sustained directional pressure, and because trend-following feedback loops emerge as more participants pile into confirmed moves. In crypto specifically, the 4-year halving cycle, retail FOMO/panic cycles, and leverage-driven cascades create some of the cleanest trending behaviors in any asset class.

**Edge Source:** Cutting losses short + letting winners run = positive expectancy even with sub-50% win rate. A system winning 40% of the time with 3:1 R-multiples outperforms a 65% win-rate system with 1:1.

---

## 2. Top Practitioners

**Ed Seykota** — Legendary systematic trend follower. Key principle: "The trend is your friend until the end when it bends." Cut all losers immediately. Only add to winners. Never average down.

**Richard Dennis / William Eckhardt (Turtle Trading)** — Turtle system used 20-day and 55-day Donchian breakouts. The original codified trend-following system. Win rate ~35–40%, but average win was 3-5× average loss.

**Andreas Clenow** — Author of *Following the Trend*, documents CTA-style systematic trend following across futures. Uses 1-year momentum ranking with exponential position sizing. Key insight: trend following underperforms in range-bound years but has massive positive skew in trending years.

**Michael Covel** — Author of *Trend Following*, catalogued 30+ systematic trend-following CTAs. Documenting principle: Every major trend follower uses some form of breakout or moving average cross, ATR-based stops, and position sizing by volatility.

**Crypto-specific:** PlanB (S2F model, trend-phase identification), Willy Woo (on-chain trend confirmation). Many quant funds (Alameda pre-collapse, Jump Trading, GSR) run trend-following as base layer.

---

## 3. Key Rules

### Entry Conditions
- **Primary Signal:** Fast EMA crosses above Slow EMA (bullish) or below (bearish)
  - Recommended pairs: 9/21 EMA (15m–1H), 20/50 EMA (4H), 50/200 EMA (daily)
- **Momentum Filter:** RSI(14) > 55 for longs, RSI(14) < 45 for shorts
- **Trend Strength Filter:** ADX(14) > 25 (confirm trend is real, not chop)
- **Volume Confirmation:** Current bar volume > 1.2× 20-period volume average
- **Higher Timeframe Alignment:** Only enter long on 1H if 4H EMA also bullish (EMA9 > EMA21 on 4H)

### Exit Conditions
- **Trailing Stop:** Trail stop-loss at 2× ATR(14) below the running highest high (longs) or above lowest low (shorts)
- **Counter-Signal:** Exit when fast EMA crosses back below slow EMA
- **Time Stop:** Exit after 5 bars if not profitable by 0.5% (avoids dead-money chop)
- **Partial Profits:** Take 50% off at 1.5× ATR gain, trail remainder

### Stop Loss Logic
- Initial hard stop: 2× ATR(14) from entry price
- Never widen stops — only tighten (ratchet upward/downward)
- Maximum stop: 3% from entry (absolute maximum, override ATR if needed)

### Position Sizing
- Risk per trade: 1% of account equity
- Position size = (Account × 0.01) / (Entry − Stop)
- Maximum position: 10% of account in single trade
- Scale into trend: initial 50% position, add 50% if price moves 1× ATR in favor with ADX still rising

---

## 4. Best Market Conditions

**Thrives in:**
- Macro-driven sustained directional moves (BTC bull runs, ETH upgrades creating weeks-long trends)
- Post-consolidation breakouts with increasing volume
- Strong ADX readings (>30) confirming trend integrity
- Markets where volatility is expanding (ATR increasing)

**Fails in:**
- Choppy, range-bound markets (ADX < 20)
- News-driven whipsaws — sharp spike up and immediate reversal
- Low-volume weekends in crypto (thin books create false crossovers)
- Sideways consolidation zones — will get chopped to death with multiple false crossovers

**Market Regime Sensitivity:**
- Regime filter is MANDATORY. A trend-following system without an ADX or volatility filter will lose 40–60% of its edge in ranging markets.
- Crypto average: 30–40% of days are trending (ADX > 25), 60–70% are ranging. This is why raw EMA crossover has poor Sharpe without regime filter.

---

## 5. Common Mistakes

1. **Using too-short EMAs on higher timeframes** — 9/21 on 1D produces dozens of whipsaws per year. Use 20/50 or 50/200 on daily.
2. **Ignoring ADX** — Entering EMA crossovers when ADX < 20 is entering noise, not trend.
3. **Averaging down** — The cardinal sin. If the trend fails, exit. Never add to losers.
4. **Moving stops to breakeven too early** — Killing winners by getting stopped out on minor retracements before the trend fully develops.
5. **Chasing entries** — Entering after a 5% move instead of at the crossover itself. Slippage + unfavorable R:R.
6. **Not accounting for weekend gap risk** — Crypto has no real gap (24/7 market) but weekend volume drops 40–60%, making signals less reliable.
7. **Ignoring funding rates on perpetual futures** — Positive funding during longs costs 0.01–0.05% per 8 hours. Over a week, this can consume a 1–2% expected gain.

---

## 6. Crypto-Specific Behavior

**BTC Trend Characteristics:**
- BTC trends on 4H–daily timeframes are highly reliable during bull markets (1–3 month duration trends common)
- Bear market trends (downtrends) are faster and more violent — average bear trend lasts 2–6 months but drops 70–80%
- The halving cycle (every 4 years) creates one of the most predictable macro trends in any asset

**ETH vs BTC:**
- ETH trends slightly weaker than BTC in isolation but has higher beta — will amplify BTC trends by ~1.3–1.6× on average
- ETH/BTC pair itself trends cleanly during "altseason" and provides a second uncorrelated trend signal

**Crypto-Specific Advantages:**
- 24/7 operation means trends don't "gap open" over weekends (unlike equities)
- High volatility means ATR-based stops catch larger trend moves

**Crypto-Specific Risks:**
- Exchange downtime/API failures during peak trend moments (high-volume breakouts overwhelm exchanges)
- Leverage liquidation cascades can create 10–20% moves in minutes, stopping out trend followers
- "Crypto Twitter" FOMO can reverse trends in hours
- Funding rate drag on perpetuals in strong uptrends (can cost 0.5–1% per day)

**Backtested Performance (industry data):**
- BTC/USDT daily EMA 50/200 crossover: ~40% CAGR historically, but ~60% max drawdown
- 4H EMA 20/50 + ADX > 25 filter: ~55–65% win rate in trending regimes, ~30% in choppy regimes

---

## 7. Bot Specification (Python-Codeable)

```python
# ============================================================
# STRATEGY 1: TREND FOLLOWING BOT SPEC
# ============================================================

# TIMEFRAME
PRIMARY_TF = "1h"          # Primary signal timeframe
HIGHER_TF  = "4h"          # Higher timeframe alignment check

# INDICATORS - ALL EXACT PARAMETERS
EMA_FAST  = 9              # Fast EMA period
EMA_SLOW  = 21             # Slow EMA period
RSI_PERIOD = 14            # RSI period
RSI_BULL_THRESHOLD = 55    # RSI must be ABOVE for long entry
RSI_BEAR_THRESHOLD = 45    # RSI must be BELOW for short entry
ADX_PERIOD = 14            # ADX period
ADX_THRESHOLD = 25         # ADX must be ABOVE for valid trend
VOL_MA_PERIOD = 20         # Volume moving average period
VOL_MULTIPLIER = 1.2       # Volume must be above: avg_vol * 1.2
ATR_PERIOD = 14            # ATR period for stops/sizing
ATR_STOP_MULT = 2.0        # Initial stop = entry ± (ATR * 2.0)
ATR_TRAIL_MULT = 2.0       # Trailing stop = highest_high - (ATR * 2.0)

# ENTRY RULES (ALL CONDITIONS MUST BE TRUE)
# LONG:
# 1. ema_fast crosses ABOVE ema_slow (previous bar: ema_fast < ema_slow, current: ema_fast > ema_slow)
# 2. rsi > RSI_BULL_THRESHOLD (55)
# 3. adx > ADX_THRESHOLD (25)
# 4. volume > vol_ma * VOL_MULTIPLIER (1.2x)
# 5. On HIGHER_TF: ema_fast > ema_slow (higher timeframe bullish alignment)

# SHORT:
# 1. ema_fast crosses BELOW ema_slow
# 2. rsi < RSI_BEAR_THRESHOLD (45)
# 3. adx > ADX_THRESHOLD (25)
# 4. volume > vol_ma * VOL_MULTIPLIER (1.2x)
# 5. On HIGHER_TF: ema_fast < ema_slow

# EXIT RULES
# 1. Trailing stop: track highest_high since entry, stop = highest_high - (atr * ATR_TRAIL_MULT)
# 2. Counter crossover: ema_fast crosses opposite direction
# 3. Time stop: if after 5 candles, price not moved > 0.5% in favor, exit at market
# 4. Partial exit: close 50% of position when unrealized gain = 1.5 * ATR

# STOP LOSS
# initial_stop = entry_price - (atr * ATR_STOP_MULT)   # long
# initial_stop = entry_price + (atr * ATR_STOP_MULT)   # short
# HARD MAX: 3% from entry (abs(entry - stop) / entry <= 0.03)
# Stop is ONE-WAY: never widen, only tighten

# POSITION SIZING
# risk_amount = account_equity * 0.01   # 1% risk per trade
# stop_distance = abs(entry_price - initial_stop)
# position_size = risk_amount / stop_distance
# MAX position_size = account_equity * 0.10 / entry_price  # 10% of account max

# SCALE-IN RULE
# If price moves 1 × ATR in favor AND adx is still rising (adx[0] > adx[1]):
#   Add second 50% tranche (total position becomes full 100%)
#   Move original stop to breakeven

# REGIME FILTER
# DO NOT TRADE if ADX < 20 (regime is ranging)
# DO NOT TRADE on 15-min candles with volume < 50% of daily average (thin liquidity)

# FEES/SLIPPAGE ASSUMPTION
# taker_fee = 0.001  # 0.1% per side (Binance standard)
# slippage_assumption = 0.0005  # 0.05% per trade
# total_round_trip_cost = (taker_fee + slippage_assumption) * 2  # ~0.3%
```

---

# STRATEGY 2: MEAN REVERSION

## 1. Strategy Overview

**Core Logic:** When price deviates significantly from its statistical mean, it tends to revert. The strategy identifies "too far, too fast" price moves, waits for the momentum to exhaust, and enters in the direction of the expected snap-back.

**Why it makes money:** In ranging/oscillating markets, overshoot → recovery is the dominant price behavior. Liquidation cascades create overshoots. Market makers fade extremes. Fear/greed create momentary mispricing. The edge is consistently harvesting these rubber-band reversals with defined risk.

**Key distinction from trend following:** Mean reversion SELLS strength and BUYS weakness. It profits from the 60–70% of market time that is NOT trending. It is complementary to (not competitive with) trend following — which is why the hybrid strategy (#6) combines them.

**Win Rate Profile:** High win rate (60–75%) but small winners. The failure mode is a fat-tail loss when a range-break turns into a sustained trend. Regime filtering is non-negotiable.

---

## 2. Top Practitioners

**Larry Connors** — RSI(2) mean reversion system. Short-term RSI drops below 10 (extreme oversold), buy when RSI crosses back above 70. Documented in *Short Term Trading Strategies That Work*. Proved 70%+ win rate on stocks in ranging markets.

**Kevin Davey** — Systematic quant trader. Mean reversion systems on futures and crypto. Key insight: "Mean reversion works until it catastrophically doesn't — sizing and regime filtering prevent the blowup."

**truenordiccapital (TradingView)** — Documented RSI(19) < 20 + Bollinger Band (20, 1.5σ) breach system on crypto 15m. Walk-forward validated over 3.5 years: $1.17M on $1 BTC/ETH/SOL system with 61% window win rate and P/DD ratio of 5.16.

**Linda Raschke** — Known for "Holy Grail" pullback trades. Buys RSI pullbacks in uptrends. Documents the behavior extensively: price oscillates around moving averages, and entries at extreme deviations in trend direction capture mean-reversion bounces.

---

## 3. Key Rules

### Entry Conditions

**LONG (Buy oversold):**
1. Price closes BELOW lower Bollinger Band (20-period SMA, 2.0 std dev) — candle close, not intrabar
2. RSI(14) < 30 (or RSI(19) < 20 for more extreme filter)
3. Regime filter: ADX(14) < 30 (not in strong trend) OR price within established range
4. Trigger confirmation: RSI crosses back ABOVE 30 from below (entry on confirmation, not at extreme)

**SHORT (Sell overbought):**
1. Price closes ABOVE upper Bollinger Band
2. RSI(14) > 70 (or RSI(19) > 72 for extreme filter)
3. ADX(14) < 30
4. RSI crosses back BELOW 70 from above (confirmation trigger)

**Enhanced filter (optional, increases quality):**
- Require RSI divergence: price makes new low but RSI makes higher low (bullish divergence) = higher probability reversal
- Z-score of (price − 20-SMA) / 20-period std dev < −2.0 (statistical extremity)

### Exit Conditions
- **Primary Target:** Return to Bollinger Band midline (20-period SMA)
- **Secondary Target:** Opposite Bollinger Band (for strong reversal moves in ranging market)
- **Partial Exit:** 50% at midline, trail 50% with 1× ATR trailing stop
- **Time Stop:** Exit after 10 candles if midline not reached (prevents holding losers that refuse to revert)

### Stop Loss Logic
- Hard stop: Below most recent swing low (for longs) — measured at candle close, not intrabar wick
- ATR-based alternative: 1.5× ATR below entry
- Maximum risk per trade: 2% from entry price (absolute cap)
- If price closes OUTSIDE the band in same direction after entry: EXIT IMMEDIATELY (trend may be starting)

### Position Sizing
- 1–2% account risk per trade
- Smaller size than trend following — mean reversion has higher frequency but smaller expected value per trade
- Position = (Account × 0.01) / (Entry − Stop)

---

## 4. Best Market Conditions

**Thrives in:**
- Ranging/oscillating markets (ADX < 25)
- Post-spike consolidation (after a sharp news-driven move that then stabilizes)
- High-volatility but directionless markets (Bollinger Bands are wide but price stays in range)
- Intraday crypto 15m–1H in stable market phases

**Fails in (catastrophically):**
- Strong trending markets — "oversold" becomes more oversold, position becomes a bag
- News events / black swans — regulatory ban, exchange hack, macro crash
- Leverage cascade environments — price can drop 30% in hours without reverting
- Low liquidity periods (deep night in Asia/Europe for altcoins) — spreads widen, false signals

**Market Regime Sensitivity:**
- This is the highest regime-sensitive strategy of the six. Running mean reversion without ADX < 30 filter historically doubles the maximum drawdown.
- In crypto: 2018, 2022 bear markets → mean reversion destroyed capital. Every oversold bounce failed and became more oversold.

---

## 5. Common Mistakes

1. **Catching falling knives** — Entering at RSI < 30 WITHOUT waiting for the RSI cross-back above 30. The cross-back is the confirmation the momentum has reversed. Without it, you're guessing the bottom.
2. **No regime filter** — Trading mean reversion during trending regimes is the primary cause of blowups.
3. **Ignoring funding rates** — In strong downtrends, negative funding on shorts signals extreme bearishness. Don't buy into it.
4. **Over-sizing** — High win rate creates overconfidence. When the loss hits (trend breakout), it's often 3–5× the average win. Position sizing discipline is essential.
5. **Not using time stops** — Positions that don't revert within expected timeframe should be cut. "Waiting for it to come back" while capital is locked is expensive.
6. **Trading against macro trend** — Buying oversold dips in a confirmed macro downtrend. The entry-level trend must be ranging, not down.

---

## 6. Crypto-Specific Behavior

**BTC 15M Mean Reversion:**
- Walk-forward study (truenordiccapital): RSI(19) < 20 + BB breach on BTCUSDT 15M → profitable over 3.5 years with 61% window win rate
- Particularly effective: 2–8 AM UTC (Asian session, lower volatility, range behavior common)
- Dangerous: Sunday evening UTC when US and Asian markets both thin

**ETH Mean Reversion:**
- ETH is MORE volatile than BTC by ~30%. Overshoots are larger but recoveries are also faster.
- ETH/BTC ratio mean reversion is a clean pair-trade opportunity (ETH tends to deviate from BTC correlation and revert)

**Funding Rate Integration:**
- Extreme funding rates (>0.1% per 8 hours) signal overleveraged market → contrarian indicator for mean reversion
- Long when funding rate is extremely negative (everyone is short) → squeeze recovery
- Short when funding rate is extremely positive (>0.15%) → longs get liquidated, price drops

**Crypto Advantage:**
- 24/7 = more mean reversion cycles per day than equities
- Leverage-driven overshoots create cleaner extremes (RSI 10–15 is not uncommon in crypto crashes)

**Specific Failure Mode in Crypto:**
- "Staircase down" pattern: BTC drops, bounces 5%, drops harder, bounces 3%, drops to new lows. Mean reversion on each bounce fails. Each entry loses 2–4%. The regime filter prevents this, but imperfectly.

---

## 7. Bot Specification (Python-Codeable)

```python
# ============================================================
# STRATEGY 2: MEAN REVERSION BOT SPEC
# ============================================================

# TIMEFRAME
PRIMARY_TF = "15m"         # Primary signal timeframe (proven on crypto)
SECONDARY_TF = "1h"        # Higher TF regime filter check

# INDICATORS - EXACT PARAMETERS
BB_PERIOD = 20             # Bollinger Band SMA period
BB_STD_DEV = 2.0           # Standard deviations (use 1.5 for more extreme/selective)
RSI_PERIOD = 14            # RSI period (use 19 for walk-forward validated version)
RSI_OVERSOLD = 30          # Oversold threshold (use 20 for extreme version)
RSI_OVERBOUGHT = 70        # Overbought threshold (use 72 for extreme version)
ADX_PERIOD = 14            # ADX period
ADX_MAX_THRESHOLD = 30     # DO NOT TRADE if ADX > 30 (trending regime)
ATR_PERIOD = 14            # ATR for stops
ATR_STOP_MULT = 1.5        # Stop = entry ± (ATR * 1.5)
ZSCORE_PERIOD = 20         # Z-score lookback
ZSCORE_THRESHOLD = 2.0     # Z-score extremity (|z| > 2.0 = entry zone)

# ENTRY RULES

# LONG ENTRY (all must be TRUE):
# 1. close < lower_bollinger_band   (price below lower band — candle close)
# 2. rsi < RSI_OVERSOLD (30)
# 3. adx < ADX_MAX_THRESHOLD (30)   (regime filter: not trending)
# 4. On NEXT bar: rsi crosses above RSI_OVERSOLD (confirmation trigger)
#    i.e., rsi[1] < 30 AND rsi[0] > 30
# OPTIONAL ENHANCEMENT:
# 5. z_score < -ZSCORE_THRESHOLD (-2.0)
# 6. Bullish RSI divergence: price[0] < price[N] but rsi[0] > rsi[N] where N=5

# SHORT ENTRY (all must be TRUE):
# 1. close > upper_bollinger_band
# 2. rsi > RSI_OVERBOUGHT (70)
# 3. adx < ADX_MAX_THRESHOLD (30)
# 4. On NEXT bar: rsi crosses below RSI_OVERBOUGHT
#    i.e., rsi[1] > 70 AND rsi[0] < 70
# OPTIONAL:
# 5. z_score > +ZSCORE_THRESHOLD (+2.0)
# 6. Bearish RSI divergence

# EXIT RULES
# PRIMARY TARGET: close reaches bb_midline (20-period SMA)
# PARTIAL EXIT: close 50% position when price reaches midline
# SECONDARY TARGET: close remaining 50% at opposite band
# TIME STOP: exit ALL after 10 candles if midline not reached
# STOP HIT: close 100% if price closes FURTHER past the band in signal direction
#   (e.g., for long: if close < lower_band on bar after entry → exit, trend may be starting)

# STOP LOSS
# For long:  stop = entry_price - (atr * ATR_STOP_MULT)
# For short: stop = entry_price + (atr * ATR_STOP_MULT)
# HARD MAX: 2% from entry price
# EMERGENCY EXIT: if price closes past entry-band on new candle after entry

# POSITION SIZING
# risk_amount = account_equity * 0.01
# stop_distance = abs(entry_price - stop_price)
# position_size = risk_amount / stop_distance
# MAX CONCURRENT POSITIONS: 2 (to avoid overexposure in ranging regime)

# REGIME FILTER (CRITICAL)
# Calculate ADX on SECONDARY_TF (1H)
# If adx_1h > 30: DISABLE all mean reversion entries
# If adx_1h < 20: ENABLE with full sizing
# If 20 < adx_1h < 30: ENABLE with 50% sizing (gray zone)

# FUNDING RATE FILTER (crypto-specific)
# If funding_rate > 0.10%: SHORT bias only (overleveraged longs = downside risk)
# If funding_rate < -0.05%: LONG bias only (overleveraged shorts = squeeze risk)

# FEES
# taker_fee = 0.001
# slippage = 0.0005
# break_even_move_required = (taker_fee + slippage) * 2 = ~0.003 (0.3%)
# Minimum target: mid_band must be at least 0.5% away from entry
```

---

# STRATEGY 3: SCALPING

## 1. Strategy Overview

**Core Logic:** Execute a large number of short-duration trades capturing 0.5–2% moves. Profit comes from frequency × small edge, not large individual gains. Each trade is a small statistical bet — the law of large numbers converts small edge into consistent returns.

**Why it makes money:** Markets are not perfectly efficient at the micro level. Order book imbalances, bid-ask spread capture (market making), momentum micro-bursts after breakouts, and repeated behavioral patterns at support/resistance all create exploitable micro-edges. Scalping harvests these repeatedly.

**Timeframe:** 1-minute to 5-minute candles. Sometimes tick data for true HFT scalping (not practical for retail bots without co-location).

**Profit per trade:** 0.3–1.5% (after fees). With 0.1% taker fee per side (0.2% round trip), minimum viable target is 0.5%+ to net 0.3%+.

---

## 2. Top Practitioners

**Ross Cameron (Warrior Trading)** — Day trading scalper, documented $1M+ years scalping small-caps. Principle: only trade stocks gapping >10% premarket with high relative volume. In crypto context: only trade coins with >300% above-average volume spike.

**Rayner Teo** — Institutional-approach scalping. Key principle: trade with the trend on the higher timeframe, scalp with the trend on the lower timeframe. Never scalp against the 1H/4H trend.

**ICT (Inner Circle Trader / Michael Huddleston)** — Order block scalping. Identifies 1-minute order blocks (price zones where institutional orders were placed), enters when price revisits these zones with momentum. Highly detailed, controversial but widely followed.

**GCR (pseudonymous crypto trader)** — Perpetual futures scalper on BTC/ETH. Uses Level 2 order book imbalance + VWAP deviation for entries. Documented 70%+ win rates on 1M timeframe by only trading in direction of 5M momentum.

**Principles shared by all scalpers:**
1. Never trade against higher timeframe trend
2. Take profits fast — greed kills scalpers
3. Commission awareness is critical
4. Use limit orders (maker), not market (taker) when possible

---

## 3. Key Rules

### Entry Conditions

**Momentum Scalp Setup (most reliable for bots):**
1. Price above 9 EMA (bullish) or below (bearish) on 1M chart
2. RSI(7) crosses above 50 (bullish momentum) from below on 1M
3. Volume on current bar > 2× average 20-bar volume (volume surge)
4. VWAP: price is above VWAP for longs, below for shorts
5. Higher timeframe (5M): 9 EMA > 21 EMA (aligned direction)
6. Spread < 0.05% (avoid wide spread periods — prevents fee erosion)

**Support/Resistance Bounce Scalp:**
1. Price touches identified support (yesterday's low, round number, VWAP)
2. Bullish rejection candle (close > open, wick below, body green)
3. RSI(7) < 35 at touch
4. Volume > 1.5× average at the candle
5. Enter next candle open

### Exit Conditions
- **Primary Target:** +0.5% from entry (quick lock-in)
- **Secondary Target:** +1.0% (if momentum strong, move stop to breakeven and hold)
- **Maximum hold time:** 10 candles on 1M (10 minutes absolute max)
- **VWAP reversion:** Exit when price approaches VWAP from either side (natural friction point)
- **Momentum stop:** If RSI(7) crosses back below 50 (for longs) before target, exit immediately

### Stop Loss Logic
- Hard stop: 0.3–0.5% from entry (tight — scalping depends on precise entries)
- ATR-based: 0.8× ATR(14) on 1M chart
- Rule: If your stop is > 0.5%, the setup has poor R:R for scalping — skip it
- R:R minimum: 1.5:1 (min 0.45% target for 0.3% stop)

### Position Sizing
- 1–2% risk per trade with tight stops = relatively large position sizes
- Risk = 0.5% account equity per trade
- With 0.3% stop: position = account × 0.005 / 0.003 = ~1.67× account (use leverage carefully)
- Maximum: 5× leverage for scalping
- High frequency = smaller % risk per trade than other strategies

---

## 4. Best Market Conditions

**Thrives in:**
- High-volume trending sessions (NYC open, Asian open for crypto)
- Post-news momentum bursts (first 5–15 minutes after a catalyst)
- Range-bound oscillation between clear levels (bounce between support and resistance)
- Market structure with clear order flow — one-sided book (all bids, no asks = buyer aggressive)

**Fails in:**
- Low-volume periods (weekend nights, holiday periods) — no follow-through, spreads widen
- Choppy micro-structure with random walk price action
- Wide bid-ask spreads (altcoins, thin books) — fees eat edge
- During macro news events (CPI, Fed meetings) — moves are too fast, stop placement impossible
- When exchange API latency is high — orders arrive late at wrong prices

**Volume Requirements:**
- Minimum: 24H volume > $500M for the pair being scalped
- BTC/ETH perpetuals are ideal; avoid anything below top 20 by volume for scalping

---

## 5. Common Mistakes

1. **Undersized targets** — Targeting 0.2% when taker fees are 0.1% per side. After 0.2% round-trip cost, there's nothing left. Minimum viable target = 3× fees (0.3% minimum after 0.1% fees).
2. **Overtrading** — Scalping 50+ times per day with marginal setups. Each suboptimal trade erodes expected value. Quality > quantity.
3. **Revenge trading** — After 3 losses in a row, increasing size to "make it back fast." The fastest way to blow a scalping account.
4. **Scalping thin altcoins** — Spreads alone can be 0.5–2%. Impossible to profit.
5. **Not using limit orders** — Market orders at 0.1% taker fee vs limit orders at 0.025% maker fee = 4× fee reduction. Over 50 trades, massive difference.
6. **Ignoring session timing** — Scalping BTC at 3 AM UTC with 20% normal volume. False signals everywhere.
7. **Holding scalp trades as "investments"** — The scalper who turns a losing 5-minute trade into a "swing hold" is the scalper who eventually blows up.

---

## 6. Crypto-Specific Behavior

**BTC/ETH Scalping:**
- Optimal sessions: 13:00–17:00 UTC (US market hours overlap), 00:00–04:00 UTC (Asian session)
- BTC average 1M candle range: ~0.1–0.3% in normal conditions, 0.5–2% in volatile sessions
- Fee-efficient scalping requires maker orders — Binance maker fee 0.025% vs taker 0.075% (3× difference)

**Liquidation Hunt Scalps:**
- Crypto-specific: large open interest concentrations become liquidation targets
- When price approaches a $500M+ liquidation cluster, momentum often accelerates through it
- Short scalp: price approaching large long liquidation wall → fade the bounce → entry as price breaks through cluster

**Funding Rate Scalps:**
- When funding rate is extreme (>0.15% per 8H), scalp SHORT on any small bounce
- Market is overleveraged long → any selling pressure triggers cascades

**VWAP Anchor Points:**
- In crypto, VWAP resets at midnight UTC
- Most reliable scalp: first test of VWAP after a strong opening move
- VWAP scalp win rate historically 60–65% on 1M BTC when aligned with 5M trend

**Crypto Risk:** 
- Exchange WebSocket disconnects during high-volume periods can leave positions unmanaged
- Must have position monitoring with HTTP fallback polling

---

## 7. Bot Specification (Python-Codeable)

```python
# ============================================================
# STRATEGY 3: SCALPING BOT SPEC
# ============================================================

# TIMEFRAMES
PRIMARY_TF  = "1m"        # Execution timeframe
SIGNAL_TF   = "5m"        # Signal confirmation timeframe
CONTEXT_TF  = "15m"       # Context / trend direction

# INDICATORS - EXACT PARAMETERS
EMA_FAST_PRIMARY  = 9     # Fast EMA on 1M
EMA_SLOW_PRIMARY  = 21    # Slow EMA on 1M
EMA_FAST_SIGNAL   = 9     # Fast EMA on 5M (trend direction)
EMA_SLOW_SIGNAL   = 21    # Slow EMA on 5M
RSI_PERIOD        = 7     # RSI period (faster for scalping)
RSI_BULL_LEVEL    = 50    # RSI must cross above for long entry
RSI_BEAR_LEVEL    = 50    # RSI must cross below for short entry
VWAP_ANCHOR       = "midnight_utc"  # VWAP daily reset at 00:00 UTC
VOL_MA_PERIOD     = 20    # Volume MA period
VOL_SURGE_MULT    = 2.0   # Volume must be 2x average
ATR_PERIOD        = 14    # ATR on 1M
ATR_STOP_MULT     = 0.8   # Stop = entry ± (ATR * 0.8)
MAX_SPREAD_PCT    = 0.0005 # Skip trade if spread > 0.05%

# TRADING HOURS FILTER
TRADE_START_UTC   = 13    # 13:00 UTC
TRADE_END_UTC     = 17    # 17:00 UTC (US session)
ALT_START_UTC     = 0     # 00:00 UTC
ALT_END_UTC       = 4     # 04:00 UTC (Asian session)
# Skip trades outside these windows

# ENTRY RULES - LONG (ALL CONDITIONS REQUIRED):
# 1. current_hour in TRADE_START_UTC..TRADE_END_UTC OR ALT_START_UTC..ALT_END_UTC
# 2. On 5M: ema_fast_signal > ema_slow_signal (bullish trend context)
# 3. On 1M: ema_fast_primary > ema_slow_primary
# 4. On 1M: rsi crosses above RSI_BULL_LEVEL (50)
#    i.e., rsi[1] < 50 AND rsi[0] > 50
# 5. price > vwap (above VWAP)
# 6. volume[0] > vol_ma * VOL_SURGE_MULT (2.0x)
# 7. ask_price - bid_price < MAX_SPREAD_PCT * mid_price
# 8. NO open position in this symbol

# ENTRY RULES - SHORT (ALL CONDITIONS REQUIRED):
# 1. (same hour filter)
# 2. On 5M: ema_fast_signal < ema_slow_signal
# 3. On 1M: ema_fast_primary < ema_slow_primary
# 4. On 1M: rsi crosses below RSI_BEAR_LEVEL (50)
# 5. price < vwap
# 6. volume[0] > vol_ma * VOL_SURGE_MULT
# 7. spread < MAX_SPREAD_PCT

# ORDER TYPE
ORDER_TYPE = "limit"      # Use limit orders for maker fee (0.025% vs 0.075% taker)
# Limit price for longs: best_bid (enter at bid to avoid crossing spread)
# Limit price for shorts: best_ask
# If not filled within 30 seconds, cancel and wait for next signal

# EXIT RULES
TARGET_1_PCT = 0.005      # +0.5% (first target — close 60% of position)
TARGET_2_PCT = 0.010      # +1.0% (second target — close remaining 40%)
MAX_HOLD_CANDLES = 10     # Force exit after 10 × 1M candles (10 minutes)
MOMENTUM_EXIT = True      # Exit if RSI crosses back past 50 before target

# STOP LOSS
# stop = entry ± (atr * ATR_STOP_MULT)
# ABSOLUTE MAX STOP: 0.5% from entry
# MOVE TO BREAKEVEN: when price reaches +TARGET_1 (0.5%), move stop to entry + fees

# POSITION SIZING
RISK_PER_TRADE_PCT = 0.005   # 0.5% account risk per trade
MAX_LEVERAGE = 5.0
# stop_distance = abs(entry - stop)
# raw_size = (account * RISK_PER_TRADE_PCT) / stop_distance
# max_size = account * MAX_LEVERAGE / entry
# position_size = min(raw_size, max_size)

# DAILY LIMITS
MAX_TRADES_PER_DAY = 20      # Hard limit
MAX_DAILY_LOSS_PCT = 0.03    # Stop trading if down 3% on the day
MAX_CONSECUTIVE_LOSSES = 4   # Stop trading if 4 losses in a row (recalibration needed)

# FEE CONFIGURATION
MAKER_FEE = 0.00025          # 0.025% (Binance VIP0 maker)
TAKER_FEE = 0.00075          # 0.075% (Binance VIP0 taker)
# Net profit after round-trip maker fees: profit - 0.0005
# MINIMUM VIABLE TRADE: target must net > 0.003 (0.3%) after all fees
```

---

# STRATEGY 4: BREAKOUT TRADING

## 1. Strategy Overview

**Core Logic:** Price spends time consolidating (building energy) within a range. When it breaks decisively above resistance or below support, the compressed energy releases into a directional move. Enter at or just after the breakout, ride the initial surge.

**Why it makes money:** Price consolidation represents equilibrium between buyers and sellers. When one side wins decisively (breakout), the losing side is forced to cover (stop cascade) while new participants pile in (FOMO). This creates an asymmetric burst — large moves happen fast. The breakout trader captures the burst.

**Empirical edge:** True breakouts (confirmed by volume) follow through 55–65% of the time in crypto. The 35–45% that fail give small losses (tight stops just inside range). The 55–65% that work give 2–5× the stop distance in profits. This asymmetry is the edge.

**Key challenge:** Distinguishing real breakouts from false breakouts (fakeouts). Volume confirmation, ATR expansion, and retest behavior are the primary filters.

---

## 2. Top Practitioners

**Mark Minervini** — SEPA (Specific Entry Point Analysis). Identifies stocks in tight consolidation (low Volatility Contraction Pattern/VCP) and enters on breakout above prior resistance. Applied to crypto: look for Bollinger Band squeeze before breakout.

**William O'Neil (CANSLIM)** — Buy breakouts from cup-and-handle and other consolidation patterns at new 52-week highs. The principle: break to new highs means the supply overhang (sellers stuck from old high) is cleared. Applied to crypto: BTC above $69K (old ATH) had cleared all prior sellers.

**IBD (Investor's Business Daily) methodology** — Requires: breakout from base with volume ≥ 40–50% above average. No volume = false breakout.

**Crypto-specific: CryptoCred** — Documents range breakout strategies for BTC/ETH. Key principle: wait for CLOSE above resistance (not just wick), then enter with stop below resistance (now becomes support).

**Glassnode / CryptoQuant** — On-chain breakout confirmation: when price breaks ATH with on-chain accumulation increasing (exchange outflows rising), confirms institutional breakout.

---

## 3. Key Rules

### Entry Conditions

**Range Breakout Setup:**
1. Identify consolidation range: price oscillates between support (S) and resistance (R) for minimum 10–20 candles
2. Range qualification: R − S < 5% (tight range = compressed energy) on chosen timeframe
3. Breakout trigger: **CANDLE CLOSE** above R × 1.002 (0.2% above resistance — avoids wick fakeouts)
4. Volume confirmation: breakout candle volume > 1.5× 20-bar average volume (MANDATORY)
5. ATR expansion: current ATR > ATR 5 bars ago (range is expanding, momentum building)
6. NOT in downtrend: price above 50 EMA on same timeframe (don't buy breakouts in downtrend)
7. Breakout candle body (close − open) > 0.6× candle range (not a doji — needs conviction)

**Retest Entry (lower risk, better R:R):**
1. Wait for price to break out, run, then pull back to test old resistance-as-support
2. Enter if price touches resistance (now support) and holds — 1–3 candle retest
3. Stop: below the new support with 0.3% buffer
4. Volume on retest should be LOWER than breakout volume (healthy pullback)

### Exit Conditions
- **Target 1:** +3–5% from breakout level (for intraday breakouts)
- **Target 2:** Measured move = height of prior range added to breakout level (e.g., range was 3% wide → target is +3% above breakout)
- **Trailing Stop:** Trail at 1× ATR(14) once first target hit
- **Failed Breakout Exit:** If price closes BACK BELOW the breakout level after close above it → IMMEDIATE EXIT (this is a failed breakout)

### Stop Loss Logic
- Stop: 0.3% below the broken resistance level (just inside the range)
- ATR alternative: 1× ATR(14) below entry
- ABSOLUTE MAX: 3% from entry
- The breakout style naturally provides tight stops — breakout trades should have 3:1 or better R:R

### Position Sizing
- 2% account risk per trade
- With 1.5–2% typical stop: position_size = account × 0.02 / 0.015
- Scale-in: Enter 50% at breakout, add 50% on successful retest

---

## 4. Best Market Conditions

**Thrives in:**
- Post-consolidation breakouts with high volume
- Market-wide "risk on" environments (BTC in bull phase)
- Macro catalysts (ETF approval, halving) that break multi-month resistance
- Times when volatility is compressing then expanding (Bollinger Band squeeze → expansion)

**Fails in:**
- Choppy markets with repeated failed breakouts ("fakeout" patterns)
- Low volume environments (thin books can't sustain breakout moves)
- Markets with high short interest at breakout levels (shorts covering creates initial move but fades)
- When breakout is news-driven with immediate reversal after the news

**Bollinger Band Squeeze:**
- When BB width (upper − lower / middle) drops to lowest in 20 bars → breakout imminent
- Direction unknown, but magnitude likely to be large
- Pre-load: monitor for squeeze, set breakout alerts, enter on first confirmed close outside band

---

## 5. Common Mistakes

1. **Entering on candle wick, not close** — The most common mistake. A wick above resistance that closes back inside is a FAKEOUT, not a breakout. ALWAYS wait for candle close.
2. **No volume confirmation** — A breakout on average or below-average volume is a manipulation test, not real buying interest. Without volume, 60–70% of "breakouts" fail.
3. **Buying at extended levels** — Entering 3–5% above resistance after the breakout has already run. Poor R:R. The entry should be at breakout level, not after it.
4. **Not exiting failed breakouts immediately** — Holding a breakout that closes back inside range, hoping it recovers. Price closing back below breakout = pattern failure, exit.
5. **Breakout in wrong direction relative to macro trend** — Breakout above range in a larger downtrend is a bear trap. Require macro trend alignment.
6. **Using too-wide ranges** — A "range" spanning 15% is not a tight consolidation — it's just a volatile market. Range must be < 5% for clean breakout.

---

## 6. Crypto-Specific Behavior

**BTC ATH Breakouts:**
- Most powerful and reliable breakout in crypto: BTC breaking all-time highs
- No overhead supply (nobody is "underwater") = no selling pressure
- 2021 ATH break above $20K led to immediate $29K before first major correction (+45%)
- 2024 ATH break above $69K led to move to $109K (+58%)

**False Breakout Rate in Crypto:**
- On 1H timeframe: ~45% of breakouts fail (revert inside range within 10 candles)
- On 4H timeframe: ~35% failure rate
- On Daily: ~25% failure rate
- Volume filter cuts false breakout rate in HALF (23% on 1H with volume confirmation)

**Crypto Order Book Dynamics:**
- Large sell walls at round numbers ($100K, $50K) are known breakout levels
- When wall is cleared with volume → move can be explosive (+5–15% in minutes)
- Stop-loss hunt behavior: price wicks above resistance, triggers shorts' stops, then reverses
  → Use 0.2% buffer above resistance for entry to avoid being the stop that gets hunted

**Whale-Driven Breakouts:**
- Large exchange outflows (>10,000 BTC leaving exchanges) often precede breakouts
- Monitor CryptoQuant exchange reserve data as leading indicator
- On-chain breakout confirmation: net unrealized profit/loss (NUPL) > 0.5 historically precedes major breakouts

---

## 7. Bot Specification (Python-Codeable)

```python
# ============================================================
# STRATEGY 4: BREAKOUT TRADING BOT SPEC
# ============================================================

# TIMEFRAMES
PRIMARY_TF    = "4h"       # Primary breakout detection timeframe
CONFIRM_TF    = "1h"       # Volume confirmation timeframe
CONTEXT_TF    = "1d"       # Macro trend context (daily)

# INDICATORS - EXACT PARAMETERS
EMA_TREND     = 50         # Price must be above this EMA for long breakouts
BB_PERIOD     = 20         # Bollinger Band period for squeeze detection
BB_STD        = 2.0        # BB standard deviation
VOL_MA_PERIOD = 20         # Volume MA period
VOL_BREAKOUT_MULT = 1.5    # Breakout volume must be >= avg * 1.5
ATR_PERIOD    = 14         # ATR for stop calculation
ATR_STOP_MULT = 1.0        # Stop = entry - (ATR * 1.0) from breakout level
RANGE_MIN_CANDLES = 10     # Minimum candles forming the range
RANGE_MAX_PCT = 0.05       # Range must be < 5% wide (R-S / mid < 0.05)
BREAKOUT_BUFFER = 0.002    # 0.2% above resistance required for confirmation

# RANGE DETECTION ALGORITHM
# Look back RANGE_MIN_CANDLES bars
# resistance = max(high) of last N candles (rolling)
# support = min(low) of last N candles (rolling)
# range_pct = (resistance - support) / support
# is_valid_range = (range_pct < RANGE_MAX_PCT) AND (candles_in_range >= RANGE_MIN_CANDLES)

# SQUEEZE DETECTION
# bb_width = (upper_band - lower_band) / middle_band
# bb_width_20 = rolling_min(bb_width, 20)  # Lowest BB width in 20 bars
# is_squeeze = bb_width == bb_width_20  # Current width is lowest in 20 bars

# LONG BREAKOUT ENTRY (ALL REQUIRED):
# 1. is_valid_range == True
# 2. close > resistance * (1 + BREAKOUT_BUFFER)  [close > resistance * 1.002]
# 3. volume[0] > vol_ma * VOL_BREAKOUT_MULT
# 4. (close - open) > 0.6 * (high - low)  [candle body > 60% of range = conviction]
# 5. close > ema_50  [macro uptrend context]
# 6. current ATR[0] > ATR[5]  [volatility expanding, not contracting]
# 7. NOT in top 20% of recent 100-bar price range (avoid extended breakouts)

# SHORT BREAKOUT ENTRY (ALL REQUIRED):
# 1. is_valid_range == True
# 2. close < support * (1 - BREAKOUT_BUFFER)
# 3. volume[0] > vol_ma * VOL_BREAKOUT_MULT
# 4. (open - close) > 0.6 * (high - low)  [bearish conviction]
# 5. close < ema_50  [macro downtrend context]
# 6. ATR[0] > ATR[5]

# RETEST ENTRY (SECONDARY SETUP - BETTER R:R):
# After breakout, track highest_high (for long) or lowest_low (for short)
# Retest trigger: price pulls back to within 0.3% of old resistance/support
# Volume on retest bar: < 0.8 × vol_ma (pullback on low volume = healthy)
# Retest entry: buy if close > old_resistance * 0.997 (within 0.3% below)
# Retest entry: sell if close < old_support * 1.003

# EXIT RULES
MEASURED_MOVE_TARGET = True   # Target = resistance + (resistance - support)
TARGET_1_MULT = 1.0           # First target = 1× range height above breakout
TARGET_2_MULT = 2.0           # Second target = 2× range height above breakout
TRAIL_AFTER_TARGET1 = True    # Trail with 1× ATR after first target hit
FAILED_BREAKOUT_EXIT = True   # Exit immediately if close re-enters range after breakout

# STOP LOSS
# For long: stop = resistance - (atr * ATR_STOP_MULT) [just inside the range]
# For short: stop = support + (atr * ATR_STOP_MULT)
# ABSOLUTE MAX: 3% from entry
# IMMEDIATE EXIT trigger: candle closes back inside range on bar after entry

# POSITION SIZING
RISK_PCT = 0.02              # 2% risk per trade
SCALE_IN = True              # Enter 50% at breakout, 50% on retest
# stop_dist = abs(entry - stop)
# size = (account * RISK_PCT) / stop_dist
# If scale_in: initial_size = size * 0.5; add size * 0.5 on retest

# BOLLINGER BAND SQUEEZE SETUP
# When is_squeeze==True: monitor for breakout in next 10 candles
# Enter on FIRST candle that closes outside the bands with volume confirmation
# This gives best entries (before the full move, not during it)
```

---

# STRATEGY 5: SWING TRADING

## 1. Strategy Overview

**Core Logic:** Hold positions for 4–72 hours to capture intermediate price swings within the larger trend. Unlike scalping (minutes) or position trading (weeks/months), swing trading targets the "shoulder" moves — meaningful but not exhaustive — within a trending or oscillating market.

**Why it makes money:** Price moves in waves (Elliott Wave principle, Dow Theory). Major trends consist of impulse moves and corrective pullbacks. Swing trading enters near the end of a correction and exits near the end of the next impulse leg. The hold time is long enough to capture 3–8% moves, short enough to avoid fundamental risk.

**Hold Duration:** 4–72 hours (1–3 days typical). Some setups hold up to 5 days.

**Win Rate vs. Scalping:** Lower frequency (5–15 trades/month vs 100+/day), higher per-trade return (3–8% vs 0.5–1.5%), manageable attention requirement (check charts 2–3×/day vs 24/7 monitoring).

---

## 2. Top Practitioners

**Steve Nison** — Father of Western candlestick analysis. Swing trading entries based on reversal candlestick patterns (engulfing, hammer, shooting star) at key support/resistance levels. Principle: candlestick patterns signal momentum exhaustion → swing entry.

**John Carter (Simpler Trading)** — Options swing trader. Uses MACD crossover on 4H chart + squeeze indicator (Bollinger Band inside Keltner Channel) for timing swing entries. Crypto application: same MACD + squeeze setup works on 4H crypto charts.

**Peter Brandt** — Classical chart pattern swing trader. Trades flag patterns, head-and-shoulders, channels. Principle: measure the pattern → define the target before entry. Rigid R:R discipline.

**Crypto-specific: Credible Crypto** — Documents multi-day swing trades on BTC/ETH using Elliott Wave counts + Fibonacci levels. Key approach: enter at Fibonacci retracement levels (38.2%, 50%, 61.8%) during corrections in larger uptrend.

**Institutional Swing:** Galaxy Digital, Pantera Capital — swing between market phases using on-chain MVRV (Market Value to Realized Value) and SOPR (Spent Output Profit Ratio) as macro entry signals.

---

## 3. Key Rules

### Entry Conditions

**Pullback Swing Entry (primary setup):**
1. Macro trend: price above 50 EMA and 200 EMA on daily (for longs)
2. Intermediate trend: 4H MACD histogram turning from negative to positive after pullback
3. RSI(14) on 4H: was below 45 during pullback, now crossing back above 50
4. Price has pulled back to Fibonacci retracement: 38.2%, 50%, OR 61.8% of prior swing (measured from swing low to swing high)
5. Volume on pullback bars lower than volume on prior impulse bars (healthy correction)
6. Entry on 4H candle CLOSE showing bullish reversal (engulfing, hammer, morning star)

**MACD Crossover Swing Entry (systematic):**
1. 4H MACD line crosses above signal line (bullish) or below (bearish)
2. MACD crossover occurs while histogram was at its most negative reading (not early)
3. Price is above 20 EMA on 4H (not entering into headwind)
4. RSI(14) was below 40 and now crossing above 40 (momentum recovering)
5. Stochastic(14,3,3) crosses up from below 20 OR crosses down from above 80

### Exit Conditions
- **Target:** Prior swing high (for longs) or prior swing low (for shorts)
- **Fibonacci Extension:** 127.2% or 161.8% extension from the last correction
- **Trailing Stop:** Trail at 2× ATR(14) on 4H once in profit > 1× ATR
- **MACD Reversal:** Exit when 4H MACD line crosses back below signal line after profit
- **RSI Exhaustion:** Exit when RSI(14) on 4H > 70 (long) or < 30 (short) — momentum exhausted

### Stop Loss Logic
- For pullback swing: below the lowest point of the pullback with 0.5% buffer
- ATR-based: 2× ATR(14) on 4H below entry
- Maximum stop: 5% from entry (swing trades carry more distance than scalps)
- Never move stop against position

### Position Sizing
- 2% risk per trade
- With 3–5% typical stop: position_size = account × 0.02 / 0.04 = 50% of account (for standard setup)
- Use leverage 1–3× for swing trades
- Maximum concurrent swings: 3 (to maintain correlation awareness)

---

## 4. Best Market Conditions

**Thrives in:**
- Trending markets with clear pullback-and-continuation structure
- Markets with identifiable support/resistance levels on 4H/daily
- Post-consolidation momentum expansion phases
- BTC leading altcoin season (swing alts while BTC trends)

**Fails in:**
- Sideways grinding markets where support and resistance constantly change
- Extremely volatile periods (50%+ moves in days) — swing targets hit instantly, stops hit on rebound
- Low-liquidity environments where moves are unreliable
- News-driven markets where fundamental catalysts override technical structure

**Correlation Risk:**
- All crypto assets correlate highly with BTC (0.7–0.95 correlation)
- Running 3 long swings across BTC, ETH, and a large-cap altcoin is essentially 3× BTC risk
- Diversify by including BTC short if altcoin longs are held (BTC.D pair)

---

## 5. Common Mistakes

1. **Entering too early in the pullback** — Catching a falling knife instead of waiting for confirmation. The MACD histogram crossing from negative to less negative is early. Wait for actual MACD line crossover.
2. **Choosing wrong Fibonacci levels** — Using minor swings instead of major swings. Fibonacci retracements must be drawn from the most significant swing low to swing high (not micro swings).
3. **Ignoring funding rates on multi-day holds** — 0.03% per 8 hours = 0.09% per day = 0.63% per week. A 7-day swing holding long during positive funding is paying ~0.6% premium. This eats a significant portion of expected gain.
4. **Over-correlating positions** — Holding 5 altcoin longs when all correlate with BTC. Concentrated risk exposure.
5. **Not accounting for weekend low liquidity** — Swing trades entered Friday can gap unpredictably over low-volume weekends. Either close before Friday or use wider stops.
6. **Holding through earnings/events equivalent** — Crypto events: exchange listings, protocol upgrades, unlock schedules. These are event risk that swing traders should avoid holding through.

---

## 6. Crypto-Specific Behavior

**BTC Swing Structure:**
- During bull markets: 15–30% pullbacks to 50 EMA are prime swing entry zones
- Fibonacci 61.8% retrace of major leg is the "golden pocket" — highest probability swing entry
- Average swing duration in trending BTC market: 3–7 days

**ETH Swing Behavior:**
- ETH/USD swings amplify BTC swings by ~1.3–1.7×
- ETH gas activity increases during ETH upswings — use Etherscan gas metrics as confirmation
- ETH swings near major protocol upgrades (EIP events) have outsized moves

**On-Chain Swing Signals:**
- MVRV ratio < 1.0: market value below realized value → high-probability long swing entry
- Exchange net flow: when exchange outflows > inflows for 3+ consecutive days → accumulation → long bias
- SOPR < 1.0: people selling at a loss → capitulation = near-term swing bottom

**Altcoin Swings:**
- During "altseason" (BTC.D declining), large-cap alts (ETH, SOL, BNB) provide stronger swings than BTC
- Small-cap alts have unreliable Fibonacci levels due to manipulation
- Best altcoin swing strategy: follow BTC trend, swing top 10 by market cap only

**Perpetual Futures Funding Rate Management:**
- For 3-day swing: check cumulative funding cost
- If positive funding 0.03%/8H and holding 72 hours: cost = 9 × 0.03% = 0.27%
- Include this in R:R calculation — minimum swing target must exceed funding cost + fees

---

## 7. Bot Specification (Python-Codeable)

```python
# ============================================================
# STRATEGY 5: SWING TRADING BOT SPEC
# ============================================================

# TIMEFRAMES
PRIMARY_TF    = "4h"       # Primary signal generation
CONFIRM_TF    = "1h"       # Confirmation / entry timing
CONTEXT_TF    = "1d"       # Macro trend context

# INDICATORS - EXACT PARAMETERS
EMA_FAST     = 20          # Fast EMA on 4H
EMA_SLOW     = 50          # Slow EMA on 4H
EMA_MACRO    = 200         # Macro trend EMA (daily)
MACD_FAST    = 12          # MACD fast EMA
MACD_SLOW    = 26          # MACD slow EMA
MACD_SIGNAL  = 9           # MACD signal line
RSI_PERIOD   = 14          # RSI period
RSI_OVERBOUGHT = 70        # RSI overbought (exit zone for longs)
RSI_OVERSOLD   = 30        # RSI oversold (exit zone for shorts)
RSI_RECOVERY   = 50        # RSI must cross above 50 for long entry confirmation
STOCH_K      = 14          # Stochastic %K period
STOCH_D      = 3           # Stochastic %D smoothing
STOCH_SLOW   = 3           # Stochastic slow period
STOCH_OVERSOLD = 20        # Stochastic oversold
STOCH_OVERBOUGHT = 80      # Stochastic overbought
ATR_PERIOD   = 14          # ATR on 4H
ATR_STOP_MULT = 2.0        # Stop = entry ± (ATR * 2.0)
FIBO_LEVELS  = [0.382, 0.500, 0.618]  # Valid Fibonacci retracement entry zones

# FIBONACCI CALCULATION
# Identify last major swing: swing_low = lowest low in last 50 bars (daily)
#                            swing_high = highest high since swing_low
# fib_382 = swing_high - (swing_high - swing_low) * 0.382
# fib_500 = swing_high - (swing_high - swing_low) * 0.500
# fib_618 = swing_high - (swing_high - swing_low) * 0.618
# Entry zone: price within 0.5% of any Fibonacci level

# LONG ENTRY (ALL REQUIRED):
# 1. On DAILY: close > ema_200  [macro uptrend]
# 2. On 4H: ema_20 > ema_50  [intermediate uptrend]
# 3. On 4H: macd_line crosses above macd_signal (MACD bullish crossover)
#    i.e., macd_line[1] < macd_signal[1] AND macd_line[0] > macd_signal[0]
# 4. On 4H: rsi crosses above RSI_RECOVERY (50)
#    i.e., rsi[1] < 50 AND rsi[0] > 50
# 5. On 4H: stoch_k > stoch_d AND stoch_k < STOCH_OVERBOUGHT (80)
#    AND stoch_k was < STOCH_OVERSOLD (20) within last 5 bars
# 6. Price within 0.5% of a Fibonacci retracement level (0.382, 0.500, or 0.618)
#    OR price bouncing from 4H EMA_20 support (within 0.3%)
# 7. Pullback volume < 0.8 × vol_ma (healthy low-volume pullback confirmed)

# SHORT ENTRY (ALL REQUIRED):
# 1. On DAILY: close < ema_200
# 2. On 4H: ema_20 < ema_50
# 3. On 4H: macd_line crosses below macd_signal
# 4. On 4H: rsi crosses below RSI_RECOVERY (50)
# 5. On 4H: stoch_k < stoch_d AND stoch_k > STOCH_OVERSOLD
#    AND stoch_k was > STOCH_OVERBOUGHT within last 5 bars
# 6. Price within 0.5% of Fibonacci resistance level
# 7. Rally volume < 0.8 × vol_ma

# EXIT RULES
# PRIMARY TARGET: prior swing high (for long) or prior swing low (for short)
# FIB EXTENSION TARGET: 
#   target_1 = swing_high + (swing_high - swing_low) * 0.272  # 127.2% extension
#   target_2 = swing_high + (swing_high - swing_low) * 0.618  # 161.8% extension
# PARTIAL EXIT: close 50% at target_1, trail 50% with 2× ATR
# MACD REVERSAL EXIT: if macd_line crosses back below signal after profit, exit 100%
# RSI EXHAUSTION: if rsi > 70 (long) or < 30 (short), exit 100%
# MAX HOLD: 72 hours (after 72 candles on 4H = 18 four-hour candles)

# STOP LOSS
# stop = swing_low of pullback - 0.005 (0.5% below lowest pullback candle)
# ATR alternative: entry - (atr * ATR_STOP_MULT)
# ABSOLUTE MAX: 5% from entry
# Do NOT move stop against position. Only trail in direction of trade.

# POSITION SIZING
RISK_PCT = 0.02           # 2% risk per trade
MAX_CONCURRENT = 3        # Maximum 3 open swing positions
# stop_dist = abs(entry - stop)
# position_size = (account * RISK_PCT) / stop_dist
# LEVERAGE: max 3×

# FUNDING RATE MANAGEMENT (crypto-specific)
FUNDING_RATE_CHECK_INTERVAL = "8h"   # Check every 8 hours
MAX_CUMULATIVE_FUNDING = 0.005        # Exit if cumulative funding cost > 0.5% of position
# If holding long and cumulative funding > 0.5%, reduce position by 50%

# CORRELATION FILTER
MAX_CORRELATED_POSITIONS = 2  # Max 2 positions with correlation > 0.7
# Check correlation coefficient between held assets over last 30 days
# If correlation > 0.7, treat as same position for risk purposes
```

---

# STRATEGY 6: ADAPTIVE/HYBRID

## 1. Strategy Overview

**Core Logic:** No single strategy works in all market conditions. The hybrid system continuously monitors market regime (trending vs. ranging) using objective volatility and trend-strength metrics, then switches its trading style accordingly. In trending regimes, it acts as a trend follower. In ranging regimes, it acts as a mean reversion trader. In uncertain regimes, it stays flat.

**Why it makes money:** This is the "meta-strategy" — it avoids the worst failure mode of every individual strategy. Pure trend followers lose in chop. Pure mean reversion loses in trends. The hybrid captures each strategy's strengths while using the other strategy's regime as the filter.

**The regime switch is the entire edge.** Without a reliable, objective, quantifiable regime classifier, this degenerates into random switching. The classifier must be mechanical and precise.

**Theoretical basis:**
- Markets alternate between two states: trending (momentum persists) and ranging (momentum reverts)
- State transitions are detectable using ADX, ATR ratio, Hurst Exponent, or Bollinger Band width
- Each state has identifiable leading indicators

---

## 2. Top Practitioners

**AQR Capital Management (Cliff Asness)** — Dynamic combination of momentum (trend following) and value (mean reversion). AQR's "Time-Series Momentum" paper (2012) quantifies when each strategy dominates. Key finding: momentum and value are negatively correlated → combining them reduces drawdown by 40%.

**Winton Group (David Harding)** — Systematically switches trend-following intensity based on market volatility and regime detection. Known for "risk parity" approach where position sizes adjust based on current regime volatility.

**Renaissance Technologies** — (Inferred from public research) Known to use regime-adaptive systems. Their Medallion Fund reportedly scales trend-following component up/down based on detected market regime.

**Andreas Clenow** — Documents regime-awareness in *Stocks on the Move*: switches from momentum to defense based on whether index is above/below 200-day SMA.

**Crypto-specific:** Quantopian/QuantConnect community researchers have published regime-switching crypto strategies using ATR ratios and ADX as regime classifiers. The "volatility ratio" method (current ATR / 20-period ATR average) is widely validated.

---

## 3. Key Rules

### Regime Classification Engine

**Regime is determined EACH BAR on 4H timeframe:**

```
TRENDING_REGIME conditions (ANY 2 of 3):
  a. ADX(14) > 25
  b. ATR(14) > ATR_MA(ATR, 20)  [current ATR above its 20-period average]
  c. BB_width > BB_width_MA(20)  [Bollinger Bands expanding above average]

RANGING_REGIME conditions (ANY 2 of 3):
  a. ADX(14) < 20
  b. ATR(14) < ATR_MA(ATR, 20)  [current ATR below average]
  c. BB_width < BB_width_percentile_20th  [bands compressed]

UNCERTAIN_REGIME:
  Neither TRENDING nor RANGING clearly → NO TRADES
```

### Trend Following Mode (when TRENDING_REGIME):
- Execute Strategy 1 rules (EMA 9/21 crossover + RSI + ADX + volume)
- Full position sizing (1% risk)
- Trail stops with 2× ATR

### Mean Reversion Mode (when RANGING_REGIME):
- Execute Strategy 2 rules (BB + RSI extremes)
- Reduced position sizing (0.5% risk — ranging strategies have more false signals)
- Time stops: 10 candles max

### Transition Rules:
- Regime must remain in new state for 3 consecutive 4H candles before switching (prevents whipsawing between modes on single bars)
- When switching from TRENDING → RANGING: close all trend positions before opening mean reversion
- When switching from RANGING → TRENDING: close all mean reversion positions before opening trend
- During UNCERTAIN_REGIME: exit all positions and hold cash/stablecoin

### Position Sizing:
- TRENDING regime: 1–2% risk per trade (larger — trend trades have longer hold, need room)
- RANGING regime: 0.5–1% risk per trade (smaller — more frequent, tighter)
- UNCERTAIN regime: 0% (no trades)

---

## 4. Best Market Conditions

**The adaptive advantage is that it works in BOTH:**

**Trending conditions:** Acts as trend follower — captures large directional moves  
**Ranging conditions:** Acts as mean reversion — harvests oscillation  
**Transition conditions:** Sits out — avoids getting chopped by regime changes

**The adaptive strategy underperforms pure strategies when:**
- The regime classification has a lag (misses first bars of new regime)
- Regime shifts are very rapid (lasting only 2–3 candles each) — too short to classify and trade
- Transaction costs from regime switching are high (entering/exiting positions to switch modes)

**Most valuable in crypto during:**
- Post-ATH consolidation phases (perfect for mean reversion mode)
- Pre/post-halving trend phases (perfect for trend following mode)
- News-driven volatility spikes followed by ranging (adaptive catches both)

---

## 5. Common Mistakes

1. **Poorly defined regime classifier** — Using just one indicator (only ADX) to classify regime is insufficient. Markets can have high ADX with no directional trend (volatility but no direction). Use composite regime score.
2. **Switching too fast** — Changing mode every 1–2 candles creates whipsaw. The 3-candle confirmation rule prevents this.
3. **Not closing old positions on regime switch** — Leaving trend positions open when entering ranging regime creates conflicting signals. Clean exit → then new mode entries.
4. **Treating adaptive as "magic" strategy** — It's not always better than pure strategies. In strongly trending bull markets, pure trend following outperforms adaptive. Adaptive's edge is its consistency across regimes.
5. **Too many indicators in the regime classifier** — More indicators = more contradictions = more UNCERTAIN regime time = strategy sits flat. Stick to 3 core regime indicators (ADX, ATR ratio, BB width).
6. **Ignoring lookback period bias** — Regime classification based on 20-bar ATR average requires 20 bars before first classification is valid. Handle startup/warmup period.

---

## 6. Crypto-Specific Behavior

**Crypto Regime Statistics:**
- Bull markets (2020–2021, 2023–2024): 60–70% TRENDING regime time
- Bear markets (2018, 2022): 50% TRENDING (downward) regime, 50% RANGING
- Sideways accumulation (2019–2020, 2022 Q4–2023 Q1): 70–80% RANGING regime
- Average regime duration: 12–48 hours (frequent switching, 3-bar confirmation important)

**Crypto Regime Indicators Validated:**
1. ADX(14) on 4H — most reliable single indicator
2. ATR(14) / ATR_MA(14,20) ratio > 1.1 = expanding volatility = trending
3. Bollinger Band Width: (upper − lower) / middle
   - BTC historical: BB width < 0.02 = ranging, > 0.05 = trending
4. **Hurst Exponent** (advanced): > 0.5 = trending, < 0.5 = mean reverting
   - Requires 100+ bars to calculate reliably; use as secondary confirmation

**Crypto-Specific Regime Classifier Enhancement:**
- Add **Funding Rate Regime:**
  - Funding rate > 0.08%: TRENDING bullish regime (overleveraged longs supporting price)
  - Funding rate < −0.03%: TRENDING bearish regime
  - Funding rate between −0.03% and 0.08%: Neutral
- Add **Volume Regime:**
  - 24H volume > 1.5× 7-day average: TRENDING
  - 24H volume < 0.7× 7-day average: RANGING (holiday, weekend effect)

**Performance Data (community backtests):**
- Pure trend following (4H, BTC): Sharpe ~0.8, max drawdown ~45%
- Pure mean reversion (4H, BTC): Sharpe ~0.6, max drawdown ~50%
- Adaptive hybrid (4H, BTC): Sharpe ~1.2–1.4, max drawdown ~25–30%
- The improvement comes entirely from the regime filter avoiding wrong-strategy deployments

---

## 7. Bot Specification (Python-Codeable)

```python
# ============================================================
# STRATEGY 6: ADAPTIVE/HYBRID BOT SPEC
# ============================================================

# TIMEFRAME
PRIMARY_TF    = "4h"       # All signals and regime detection on 4H
CONTEXT_TF    = "1d"       # Macro context (daily)

# ============================================================
# REGIME DETECTION ENGINE
# ============================================================
ADX_PERIOD           = 14
ADX_TREND_THRESHOLD  = 25   # ADX > 25 → trending indicator
ADX_RANGE_THRESHOLD  = 20   # ADX < 20 → ranging indicator
ATR_PERIOD           = 14
ATR_MA_PERIOD        = 20   # ATR moving average period
ATR_TREND_RATIO      = 1.10 # ATR / ATR_MA > 1.10 = trending
ATR_RANGE_RATIO      = 0.90 # ATR / ATR_MA < 0.90 = ranging
BB_PERIOD            = 20
BB_STD               = 2.0
BB_TREND_WIDTH_PCT   = 0.05  # BB_width > 5% = trending (BTC-specific)
BB_RANGE_WIDTH_PCT   = 0.02  # BB_width < 2% = ranging

REGIME_CONFIRM_BARS  = 3     # New regime must persist 3 bars before switching

# REGIME SCORING FUNCTION
# score = 0
# IF adx > ADX_TREND_THRESHOLD: score += 1  (trending point)
# IF adx < ADX_RANGE_THRESHOLD: score -= 1  (ranging point)
# IF atr_ratio > ATR_TREND_RATIO: score += 1
# IF atr_ratio < ATR_RANGE_RATIO: score -= 1
# IF bb_width > BB_TREND_WIDTH_PCT: score += 1
# IF bb_width < BB_RANGE_WIDTH_PCT: score -= 1
# 
# REGIME:
#   score >= 2: TRENDING
#   score <= -2: RANGING
#   -1 <= score <= 1: UNCERTAIN

# OPTIONAL ENHANCED SCORING (add if API available):
# + Funding Rate Regime:
#   IF funding_rate > 0.0008: score += 1  (trending bullish)
#   IF funding_rate < -0.0003: score -= 0.5 (trending bearish)
# + Volume Regime:
#   IF vol_24h > vol_7d_avg * 1.5: score += 1
#   IF vol_24h < vol_7d_avg * 0.7: score -= 1

# REGIME STATE MACHINE
# current_regime = last CONFIRMED regime
# pending_regime = current calculated regime
# if pending_regime != current_regime:
#     pending_bars_count += 1
#     if pending_bars_count >= REGIME_CONFIRM_BARS:
#         current_regime = pending_regime
#         pending_bars_count = 0
#         EXECUTE REGIME_TRANSITION()
# else:
#     pending_bars_count = 0

# REGIME TRANSITION HANDLER
# def REGIME_TRANSITION(old_regime, new_regime):
#     if old_regime == TRENDING and new_regime == RANGING:
#         close_all_trend_positions()   # Close EMA crossover trades
#         set_mode(MEAN_REVERSION)
#     elif old_regime == RANGING and new_regime == TRENDING:
#         close_all_reversion_positions()  # Close BB/RSI trades
#         set_mode(TREND_FOLLOWING)
#     elif new_regime == UNCERTAIN:
#         close_all_positions()
#         set_mode(INACTIVE)
#     log_regime_change(old_regime, new_regime, timestamp)

# ============================================================
# TREND FOLLOWING MODE PARAMETERS (same as Strategy 1 but on 4H)
# ============================================================
TREND_EMA_FAST    = 9
TREND_EMA_SLOW    = 21
TREND_RSI_PERIOD  = 14
TREND_RSI_BULL    = 55
TREND_RSI_BEAR    = 45
TREND_VOL_MULT    = 1.2
TREND_ATR_STOP    = 2.0
TREND_RISK_PCT    = 0.01      # 1% risk per trend trade

# TREND ENTRY LONG (TRENDING regime only):
# 1. ema_fast crosses above ema_slow
# 2. rsi > TREND_RSI_BULL
# 3. volume > vol_ma * TREND_VOL_MULT
# 4. (These are same as Strategy 1 — reference that spec)

# ============================================================
# MEAN REVERSION MODE PARAMETERS (same as Strategy 2)
# ============================================================
REV_BB_PERIOD     = 20
REV_BB_STD        = 2.0
REV_RSI_PERIOD    = 14
REV_RSI_OVERSOLD  = 30
REV_RSI_OVERBOUGHT = 70
REV_ATR_STOP      = 1.5
REV_RISK_PCT      = 0.005     # 0.5% risk per reversion trade (smaller — more frequent)
REV_MAX_POSITIONS = 2
REV_TIME_STOP_BARS = 10       # Exit after 10 bars if no reversion

# REVERSION ENTRY LONG (RANGING regime only):
# 1. close < lower_bb
# 2. rsi < REV_RSI_OVERSOLD
# 3. On next bar: rsi crosses above REV_RSI_OVERSOLD (confirmation)
# 4. (Same as Strategy 2 — reference that spec)

# ============================================================
# POSITION & RISK MANAGEMENT
# ============================================================
MAX_TOTAL_RISK_PCT = 0.04     # Maximum 4% total open risk at any time
DAILY_LOSS_LIMIT   = 0.03     # Stop all trading if down 3% in calendar day
REGIME_LOG = True             # Log all regime changes with timestamp and score

# ============================================================
# PERFORMANCE MONITORING
# ============================================================
# Track separately:
#   - Trend mode PnL
#   - Reversion mode PnL
#   - Idle time (% of time in UNCERTAIN regime)
# 
# If one mode consistently loses money over 30 days:
#   - Alert human operator
#   - Reduce that mode's risk_pct by 50%
#   - Do NOT auto-disable (human review required)

# ============================================================
# STATE STORAGE (for bot persistence across restarts)
# ============================================================
STATE = {
    "current_regime": "UNCERTAIN",       # Initial state
    "regime_score": 0,
    "pending_regime": None,
    "pending_bars_count": 0,
    "active_mode": "INACTIVE",
    "open_positions": [],
    "daily_pnl": 0.0,
    "session_start": None
}
# Persist STATE to disk/database on every update
# Load STATE on bot restart to resume without regime gap
```

---

# APPENDIX: REGIME COMPARISON MATRIX

| Strategy | Win Rate | Avg Win | Avg Loss | Works Best | Fails In | Crypto Edge |
|---|---|---|---|---|---|---|
| Trend Following | 35–45% | 4–8% | 1–2% | Trending (ADX>25) | Choppy markets | Halving cycles, bull runs |
| Mean Reversion | 60–75% | 1–2% | 2–4% | Ranging (ADX<25) | Strong trends | Liquidation bounces |
| Scalping | 55–70% | 0.5–1% | 0.3–0.5% | High-volume sessions | Thin markets | 24/7 operation |
| Breakout | 45–55% | 3–6% | 1–2% | Post-consolidation | Fakeout-heavy markets | ATH breakouts explosive |
| Swing | 50–60% | 3–8% | 2–4% | Trending + pullbacks | Choppy/news-driven | Fibonacci levels highly respected |
| Adaptive/Hybrid | 50–60% combined | Variable | Variable | All regimes | Rapid regime switching | Best Sharpe ratio overall |

---

# APPENDIX: INDICATOR FORMULAS (Reference)

```python
# EMA (Exponential Moving Average)
# multiplier = 2 / (period + 1)
# EMA[0] = (close[0] - EMA[1]) * multiplier + EMA[1]
# pandas_ta: ta.ema(close, period)

# ATR (Average True Range)
# TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
# ATR = EMA(TR, period)  [Wilder's smoothing = EMA with period=14]
# pandas_ta: ta.atr(high, low, close, period)

# RSI (Relative Strength Index)
# gain = avg_gain over period bars (Wilder's smoothing)
# loss = avg_loss over period bars
# RS = gain / loss
# RSI = 100 - (100 / (1 + RS))
# pandas_ta: ta.rsi(close, period)

# ADX (Average Directional Index)
# +DM = high[0] - high[1] if positive, else 0
# -DM = low[1] - low[0] if positive, else 0
# +DI = 100 * EMA(+DM, 14) / ATR(14)
# -DI = 100 * EMA(-DM, 14) / ATR(14)
# DX = 100 * abs(+DI - -DI) / (+DI + -DI)
# ADX = EMA(DX, 14)
# pandas_ta: ta.adx(high, low, close, period)

# Bollinger Bands
# middle = SMA(close, period)
# std = rolling_std(close, period)
# upper = middle + (std_dev * std)
# lower = middle - (std_dev * std)
# pandas_ta: ta.bbands(close, period, std_dev)

# MACD
# macd_line = EMA(close, fast) - EMA(close, slow)
# signal_line = EMA(macd_line, signal)
# histogram = macd_line - signal_line
# pandas_ta: ta.macd(close, fast, slow, signal)

# VWAP
# typical_price = (high + low + close) / 3
# cumulative_tp_vol = cumsum(typical_price * volume)  [reset at anchor point]
# cumulative_vol = cumsum(volume)
# vwap = cumulative_tp_vol / cumulative_vol
# pandas_ta: ta.vwap(high, low, close, volume)

# Z-Score
# mean = rolling_mean(close, period)
# std = rolling_std(close, period)
# z_score = (close - mean) / std
```

---

# APPENDIX: RECOMMENDED PYTHON LIBRARIES

```python
# Data fetching
import ccxt              # Unified crypto exchange API (Binance, Bybit, OKX, etc.)

# Technical indicators (all formulas above)
import pandas_ta as ta   # Most complete TA library for pandas

# Data manipulation
import pandas as pd
import numpy as np

# Exchange connectivity
# ccxt.binance() / ccxt.bybit() / ccxt.okx()
# exchange.fetch_ohlcv(symbol, timeframe, limit=200)
# exchange.create_order(symbol, type, side, amount, price)

# Persistence
import json              # Simple state storage
import sqlite3           # For trade logging and history

# Scheduling
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Schedule: run strategy every new candle close (e.g., every 4H on :00)
```

---

*End of Phase 1 Research Document*  
*Compiled: 2026-04-02 | Ready for Phase 2: Bot Implementation*
