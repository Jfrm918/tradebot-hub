# Trading Bot Deep Research
## Compiled: 2026-03-31

---

## KEY FINDINGS FROM TOP OPEN SOURCE BOTS

### Freqtrade (Gold Standard)
- 3 mandatory functions: `populate_indicators`, `populate_entry_trend`, `populate_exit_trend`
- Signals fire on **candle CLOSE**, execute on **next candle OPEN** — never trade on current candle
- `startup_candle_count` MUST = your longest indicator period
- Always place stoploss ON the exchange (survives crashes/disconnects)
- Use **limit orders** for entries, **market orders** for stops only
- Run lookahead-analysis AND recursive-analysis before real money

### Strategy Architecture That Works
- Multi-timeframe confirmation is #1 edge most bots miss
- Entry on 5m pullback + 1h trend confirmation = win rate 55-65%
- Volume confirmation is non-negotiable (filter out weak signals)
- Fisher RSI (normalized) beats raw RSI at extremes significantly
- Bollinger Bands + Stochastic crossover + Volume spike = high probability entry

### What Actually Makes Money (ranked)
1. Trend-following on 1h-4h with 5m entries — most consistent
2. Mean reversion on oversold dips (15m-1h) — works in ranging markets
3. Grid bots on liquid pairs — 0.1-0.5%/day in sideways markets
4. RSI/BB mean reversion (5m) — mediocre edge after fees
5. Scalping < 5m — fees destroy the edge unless market making

---

## WHAT CONSISTENTLY FAILS
- Scalping on 1m — fees kill it
- Pure RSI without trend filter — backtest hero, live zero
- Overfitting hyperopt to same data — noise not signal
- Ignoring fees — 0.2% per trade × 3 trades/day = 0.6%/day hole to dig out of
- Not testing out-of-sample

---

## REAL PROFITABILITY NUMBERS
- Good: 15-25% annual in sideways market (market-neutral)
- Very good: 40-80% annual in trending markets
- Most beginners: Lose money first 6-12 months (overfitting/lookahead bias)
- Grid bot: 0.1-0.5%/day on $500 in ranging market = $0.50-$2.50/day

---

## CRITICAL UPGRADES NEEDED FOR OUR SYSTEM

### Priority 1: Add Volume Data
- Blofin public API has volume in ticker data — we have it, not using it
- Volume spike filter eliminates 40-60% of false entries

### Priority 2: Multi-Timeframe Logic
- Currently: one timeframe per bot
- Need: 1h trend filter + 5m entry signal
- Blofin candle endpoint: `/api/v1/market/candles?instId=BTC-USDT&bar=1H`

### Priority 3: Fisher RSI (better than raw RSI)
```python
rsi = 0.1 * (rsi_value - 50)
fisher_rsi = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)
fisher_rsi_norma = 50 * (fisher_rsi + 1)  # 0-100 scale
# Use < 5 for oversold, > 95 for overbought
```

### Priority 4: Portfolio Risk Layer
- Max 3 open positions simultaneously
- Max 20% capital per trade
- Daily drawdown limit: -3% → pause all bots
- Correlation check: don't hold BTC and ETH long simultaneously

### Priority 5: Candle-Based Logic (Not Tick-Based)
- Real strategies use OHLCV candles, not individual price ticks
- Pull 5m candles from Blofin every 5 minutes
- Signals fire on candle close, execute on next open

### Priority 6: Trailing Stop Loss
```python
trailing_stop = True
trailing_stop_positive = 0.01        # Lock in 1% after profitable
trailing_stop_positive_offset = 0.02 # Only after +2% gain
```

---

## BEST STRATEGY CONFIG FOR $500 CAPITAL

```python
PROVEN_CONFIG = {
    'timeframe': '5m',
    'htf': '1h',                    # higher timeframe for trend
    'startup_candles': 200,
    'max_open_trades': 3,
    'stake_per_trade_pct': 0.20,    # 20% per trade
    'stoploss': -0.05,              # Hard -5% stop
    'trailing_stop': True,
    'trailing_stop_positive': 0.01,
    'trailing_stop_offset': 0.02,
    'minimal_roi': {
        '1440': 0.01,   # 24h: 1%
        '80':   0.02,   # 80min: 2%
        '40':   0.03,   # 40min: 3%
        '0':    0.05    # immediate: 5%
    },
    'entry_conditions': [
        'htf_ema50 > htf_ema200',       # 1h uptrend
        'fisher_rsi_norma < 15',        # 5m deeply oversold
        'close < bb_lower',             # below Bollinger
        'fastd > fastk',                # Stochastic turning up
        'volume > volume_ma20 * 1.3',   # volume confirmation
    ]
}
```

---

## HUMMINGBOT MARKET MAKING (for later)
- With $500 on Binance: 0.1-0.3%/day = $0.50-$1.50/day
- Requires tight spreads on liquid pairs
- Key risk: inventory accumulation in trending markets
- Best pairs for small capital: BTC/USDT, ETH/USDT spot

---

## NEXT BUILD PRIORITIES

1. **Upgrade to candle-based data** (Blofin OHLCV API)
2. **Add Fisher RSI** (better signal quality)
3. **Add volume confirmation** (eliminate false signals)
4. **Add 1h trend filter** (HTF confirmation)
5. **Add portfolio risk layer** (max trades, drawdown limits)
6. **Add trailing stops** (protect profits)
7. **Backtest with real historical data** before going live
8. **Paper trade for 30 days** with upgraded system
9. **Live with $100 test capital** if paper results are good
10. **Scale to full capital** after 2 weeks of live validation

---

## THE TRUTH ABOUT TIMEFRAME
- From paper trading to real money: minimum 30-60 days of validation
- From real money test to scale: another 30 days
- Realistic timeline to confident real trading: 60-90 days from now
- Shortcuts here = losses. No exceptions.
