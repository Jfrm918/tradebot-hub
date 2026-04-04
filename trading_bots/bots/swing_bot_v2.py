#!/usr/bin/env python3
"""
Swing Bot v2 — BTC medium-term swing strategy
Uses EMA crossover (fast vs slow) as entry/exit signal with wider profit targets.
$100 starting capital. No config.json dependency.

Price sources (in priority order):
  1. Coinbase  — api.coinbase.com (free, no auth)
  2. Kraken    — api.kraken.com   (free, no auth)
  3. CoinGecko — api.coingecko.com (free, no auth)
"""

import time
import requests
from datetime import datetime
from collections import deque
import os

# ─── Config ───────────────────────────────────────────────────────────────────
SYMBOL           = "BTC-USDT"
STARTING_BALANCE = 100.0
TRADE_FRACTION   = 0.95
EMA_FAST         = 5          # fast EMA period
EMA_SLOW         = 12         # slow EMA period
PROFIT_TARGET    = 0.012      # exit at +1.2%
STOP_LOSS        = 0.006      # exit at -0.6%
CHECK_INTERVAL   = 30
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'swing.log')
# ──────────────────────────────────────────────────────────────────────────────


def get_price():
    try:
        r = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot', timeout=10)
        r.raise_for_status()
        return float(r.json()['data']['amount'])
    except Exception:
        pass
    try:
        r = requests.get('https://api.kraken.com/0/public/Ticker?pair=XBTUSD', timeout=10)
        r.raise_for_status()
        return float(r.json()['result']['XXBTZUSD']['c'][0])
    except Exception:
        pass
    r = requests.get(
        'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
        timeout=15
    )
    r.raise_for_status()
    return float(r.json()['bitcoin']['usd'])


def compute_ema(prices_list, period):
    """Compute EMA from a list of prices over given period."""
    if len(prices_list) < period:
        return None
    k = 2 / (period + 1)
    ema = prices_list[0]
    for p in prices_list[1:]:
        ema = p * k + ema * (1 - k)
    return ema


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def main():
    balance = STARTING_BALANCE
    position = None
    prices = deque(maxlen=EMA_SLOW)
    prev_cross = None   # 'above' or 'below'

    log(f"Swing Bot v2 started | Balance: ${balance:.2f}")

    while True:
        try:
            price = get_price()
            prices.append(price)

            if len(prices) < EMA_SLOW:
                time.sleep(CHECK_INTERVAL)
                continue

            price_list = list(prices)
            ema_fast = compute_ema(price_list[-EMA_FAST:], EMA_FAST)
            ema_slow = compute_ema(price_list, EMA_SLOW)

            if ema_fast is None or ema_slow is None:
                time.sleep(CHECK_INTERVAL)
                continue

            cross = 'above' if ema_fast > ema_slow else 'below'

            if position is None:
                # Golden cross: fast crosses above slow → long
                if prev_cross == 'below' and cross == 'above':
                    size = round((balance * TRADE_FRACTION) / price, 6)
                    position = {'price': price, 'size': size}
                    log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
            else:
                entry = position['price']
                size  = position['size']
                pct   = (price - entry) / entry

                # Death cross exit, or profit/stop hit
                if (prev_cross == 'above' and cross == 'below') or pct >= PROFIT_TARGET or pct <= -STOP_LOSS:
                    pnl = round((price - entry) * size, 4)
                    balance = round(balance + pnl, 2)
                    log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                    position = None

            prev_cross = cross

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
