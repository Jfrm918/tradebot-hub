# Grid Bot Research Report

## Root Cause: 0 Trades in 7.5 Hours

**The strategy as written is architecturally broken — not a parameter tuning problem.**

### Why 0 Trades Fired

**EMA20 on 5-second ticks = 100-second lookback window.**

With smoothing factor `k = 2/(20+1) = 0.0952`, the EMA tracks price with a ~100-second lag. In a trending or normally-moving market:

- BTC max deviation from EMA20 (5s ticks) over 7.5 hours: **~0.14%**
- Your trigger threshold: **-0.50%**
- Gap: **3.5× too tight**

For price to be 0.5% below its own 100-second EMA would require BTC to drop **~$342 in under 2 minutes**. That's a flash crash, not normal trading.

**The EMA adapts too fast** — it follows price, so price is almost never far from it.

### The Other Problem: This Isn't a Grid Bot

A grid bot doesn't use EMA for entry. It places buy/sell orders at **fixed price levels** and profits from price oscillating between them. The current strategy is a mean-reversion entry with no grid structure at all.

---

## How a Real Grid Bot Works

Standard grid trading (as implemented by Binance, 3Commas, Hummingbot):

1. **Define a price range** (e.g., $65,000–$71,000)
2. **Divide into N equal levels** (e.g., 10 grids = $600/grid)
3. **Place buy orders below current price**, sell orders above
4. **When a buy fills → place sell one level up**
5. **When a sell fills → place buy one level down**
6. Profit comes from each completed buy→sell cycle

**Key**: triggers on ANY price crossing a grid line, regardless of EMA.

BTC moved $859 overnight → would have crossed 10+ grid lines at 1% spacing.

---

## Hummingbot's Approach

Hummingbot's `pure_market_making` strategy places **bid and ask orders around the mid-price**:
- `bid_spread`: distance below mid for buy orders (e.g., 0.1%)
- `ask_spread`: distance above mid for sell orders (e.g., 0.1%)
- `order_levels`: how many layers (grid depth)
- `order_level_spread`: spacing between layers

It **continuously re-prices** as market moves — market making, not trend following.

---

## Strategy Comparison for $100 Capital

| Strategy | Trades Fired | Suited For | Risk |
|---|---|---|---|
| Broken EMA Grid | **0** | Nothing | N/A |
| Real Grid Bot | ✅ Every crossing | Ranging/oscillating markets | Trend risk (runaway) |
| DCA Bot | ✅ Time-based | Trending markets | None (cost averaging) |
| BB Bounce | ✅ At band extremes | Ranging markets | Trend breakthroughs |
| Market Making | ✅ Continuous | High-liquidity, tight spread | Inventory risk |

**Recommendation: Replace with Real Grid Bot + DCA hybrid**

---

## Recommendation

**Replace the broken EMA logic entirely.** Use a proper price-level grid bot.

The full Python implementation is in `grid_bot_v2.py`.
