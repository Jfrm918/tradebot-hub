#!/usr/bin/env python3
"""
Momentum Trading Bot - Blofin Paper Trading Simulation
Strategy: Buy on uptrend confirmation, sell on momentum loss
Capital: $100 USD
Exchange: Blofin (public API for prices, simulated execution)
"""

import json
import urllib.request
import urllib.error
import time
import datetime
import os
import sys

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
CAPITAL = 100.0          # starting USD
PAIRS   = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT"]
LEVERAGE = 1             # no leverage for safety
POSITION_PCT = 0.25      # 25% of capital per trade max
EMA_SHORT = 5            # bars
EMA_LONG  = 20           # bars
RSI_PERIOD = 14
RSI_BUY_THRESH = 55      # buy when RSI crosses above
RSI_SELL_THRESH = 45     # sell when RSI drops below
CANDLE_INTERVAL = "1m"
LOOKBACK = 50            # number of candles to fetch
LOG_DIR  = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

BASE_URL = "https://openapi.blofin.com/api/v1"

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
balance  = CAPITAL
positions = {}   # pair -> {entry_price, qty, entry_time, entry_rsi}
trades   = []    # completed trades

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    with open(os.path.join(LOG_DIR, f"bot_{date_str}.log"), "a") as f:
        f.write(line + "\n")

def fetch_json(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        log(f"HTTP error fetching {url}: {e}")
        return None

def get_candles(inst_id, bar=CANDLE_INTERVAL, limit=LOOKBACK):
    url = f"{BASE_URL}/market/candles?instId={inst_id}&bar={bar}&limit={limit}"
    data = fetch_json(url)
    if not data or data.get("code") != "0":
        return []
    # data["data"] = list of [ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
    candles = data["data"]
    # Return list of floats [close] oldest→newest
    closes = [float(c[4]) for c in reversed(candles)]
    return closes

def ema(prices, period):
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    e = prices[0]
    for p in prices[1:]:
        e = p * k + e * (1 - k)
    return e

def rsi(prices, period=RSI_PERIOD):
    if len(prices) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, period + 1):
        d = prices[-period + i - 1 + 1] - prices[-period + i - 1] if i < len(prices) else 0
        # simpler:
        pass
    # Proper RSI on last period+1 values
    subset = prices[-(period + 1):]
    deltas = [subset[i] - subset[i-1] for i in range(1, len(subset))]
    gain   = sum(d for d in deltas if d > 0) / period
    loss   = sum(-d for d in deltas if d < 0) / period
    if loss == 0:
        return 100.0
    rs = gain / loss
    return 100 - 100 / (1 + rs)

def should_buy(closes):
    if len(closes) < LOOKBACK:
        return False, None
    ema_s = ema(closes[-EMA_SHORT*2:], EMA_SHORT)
    ema_l = ema(closes[-EMA_LONG*2:],  EMA_LONG)
    r     = rsi(closes)
    if ema_s is None or ema_l is None or r is None:
        return False, r
    # Momentum: short EMA above long EMA and RSI > threshold
    return (ema_s > ema_l and r > RSI_BUY_THRESH), r

def should_sell(closes, entry_price):
    if len(closes) < LOOKBACK:
        return False, None
    ema_s = ema(closes[-EMA_SHORT*2:], EMA_SHORT)
    ema_l = ema(closes[-EMA_LONG*2:],  EMA_LONG)
    r     = rsi(closes)
    if ema_s is None or ema_l is None or r is None:
        return False, r
    current_price = closes[-1]
    # Sell if: EMA bearish crossover OR RSI drops below threshold OR trailing stop -2%
    bearish = ema_s < ema_l
    rsi_weak = r < RSI_SELL_THRESH
    stop_loss = current_price < entry_price * 0.98
    take_profit = current_price > entry_price * 1.03
    return (bearish or rsi_weak or stop_loss or take_profit), r

def record_trade(pair, entry_price, exit_price, qty, entry_time, exit_time, exit_reason):
    pnl = (exit_price - entry_price) * qty
    pnl_pct = (exit_price - entry_price) / entry_price * 100
    trade = {
        "pair": pair,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "qty": qty,
        "entry_time": entry_time,
        "exit_time": exit_time,
        "pnl_usd": round(pnl, 4),
        "pnl_pct": round(pnl_pct, 4),
        "exit_reason": exit_reason,
        "hold_minutes": round((exit_time - entry_time).total_seconds() / 60, 1)
    }
    trades.append(trade)
    return trade

def daily_report():
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    day_trades = [t for t in trades if t["exit_time"].strftime("%Y-%m-%d") == today]
    total = len(day_trades)
    wins  = [t for t in day_trades if t["pnl_usd"] > 0]
    losses = [t for t in day_trades if t["pnl_usd"] <= 0]
    win_rate = (len(wins) / total * 100) if total > 0 else 0
    total_pnl = sum(t["pnl_usd"] for t in day_trades)
    best  = max(day_trades, key=lambda t: t["pnl_usd"]) if day_trades else None
    worst = min(day_trades, key=lambda t: t["pnl_usd"]) if day_trades else None

    report = {
        "date": today,
        "balance_usd": round(balance, 4),
        "total_trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": round(win_rate, 1),
        "total_pnl_usd": round(total_pnl, 4),
        "best_trade": best,
        "worst_trade": worst,
        "all_trades": day_trades
    }

    report_path = os.path.join(LOG_DIR, f"report_{today}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log(f"📊 DAILY REPORT | Date: {today} | Balance: ${balance:.2f} | Trades: {total} | WinRate: {win_rate:.1f}% | PnL: ${total_pnl:.4f}")
    if best:
        log(f"  🏆 Best:  {best['pair']} +${best['pnl_usd']} ({best['pnl_pct']}%) [{best['exit_reason']}]")
    if worst:
        log(f"  📉 Worst: {worst['pair']} ${worst['pnl_usd']} ({worst['pnl_pct']}%) [{worst['exit_reason']}]")
    return report

# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
def run(max_cycles=None, cycle_sleep=60):
    global balance
    log(f"🚀 Momentum Bot starting | Capital: ${balance} | Pairs: {PAIRS}")
    log(f"   Strategy: EMA({EMA_SHORT}/{EMA_LONG}) + RSI({RSI_PERIOD}) | TP: +3% | SL: -2%")

    last_report_date = None
    cycle = 0

    while True:
        cycle += 1
        now = datetime.datetime.now(datetime.timezone.utc)
        today = now.strftime("%Y-%m-%d")

        # Daily report at midnight UTC
        if last_report_date != today:
            if last_report_date is not None:
                daily_report()
            last_report_date = today

        log(f"── Cycle {cycle} | {now.strftime('%H:%M:%S')} UTC | Balance: ${balance:.2f} | Open: {list(positions.keys())}")

        for pair in PAIRS:
            try:
                closes = get_candles(pair)
                if not closes or len(closes) < LOOKBACK:
                    log(f"  {pair}: insufficient data ({len(closes)} candles)")
                    continue

                current_price = closes[-1]

                # ── CHECK EXIT FIRST ──
                if pair in positions:
                    pos = positions[pair]
                    sell_signal, r = should_sell(closes, pos["entry_price"])
                    change_pct = (current_price - pos["entry_price"]) / pos["entry_price"] * 100

                    if sell_signal:
                        # Determine reason
                        if current_price < pos["entry_price"] * 0.98:
                            reason = "stop_loss"
                        elif current_price > pos["entry_price"] * 1.03:
                            reason = "take_profit"
                        elif r and r < RSI_SELL_THRESH:
                            reason = "rsi_weak"
                        else:
                            reason = "ema_cross"

                        # Execute sell
                        proceeds = pos["qty"] * current_price
                        balance += proceeds
                        trade = record_trade(
                            pair, pos["entry_price"], current_price,
                            pos["qty"], pos["entry_time"], now, reason
                        )
                        del positions[pair]
                        emoji = "✅" if trade["pnl_usd"] > 0 else "❌"
                        log(f"  {emoji} SELL {pair} @ ${current_price:.4f} | PnL: ${trade['pnl_usd']:+.4f} ({trade['pnl_pct']:+.2f}%) | Reason: {reason} | RSI: {r:.1f}")

                    else:
                        log(f"  📌 HOLD {pair} @ ${current_price:.4f} | Entry: ${pos['entry_price']:.4f} | Change: {change_pct:+.2f}% | RSI: {r:.1f if r else 'n/a'}")

                # ── CHECK ENTRY ──
                elif pair not in positions:
                    buy_signal, r = should_buy(closes)
                    if buy_signal:
                        max_spend = balance * POSITION_PCT
                        if max_spend < 1.0:
                            log(f"  ⚠️  Insufficient balance for {pair} (${balance:.2f})")
                            continue
                        qty = max_spend / current_price
                        balance -= max_spend
                        positions[pair] = {
                            "entry_price": current_price,
                            "qty": qty,
                            "entry_time": now,
                            "entry_rsi": r
                        }
                        log(f"  🟢 BUY  {pair} @ ${current_price:.4f} | Qty: {qty:.6f} | Cost: ${max_spend:.2f} | RSI: {r:.1f}")
                    else:
                        log(f"  ⏸️  WAIT {pair} @ ${current_price:.4f} | RSI: {r:.1f if r else 'n/a'} | No signal")

                time.sleep(0.5)  # rate limit between pairs

            except Exception as e:
                log(f"  ⚠️  Error processing {pair}: {e}")

        if max_cycles and cycle >= max_cycles:
            log(f"✅ Reached max_cycles={max_cycles}, stopping.")
            break

        time.sleep(cycle_sleep)

    # Final report
    final = daily_report()
    return final


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=None, help="Max cycles (default: run forever)")
    parser.add_argument("--sleep", type=int, default=60, help="Seconds between cycles (default: 60)")
    args = parser.parse_args()
    run(max_cycles=args.cycles, cycle_sleep=args.sleep)
