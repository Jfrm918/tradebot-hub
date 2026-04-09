#!/usr/bin/env python3
"""
Scalp Bot — BTC ultra-short-term strategy
Enters on small micro-momentum, exits quickly at tight profit/stop targets.
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
STARTING_BALANCE = 1000.0
TRADE_FRACTION   = 0.90
WINDOW           = 3          # very short window for micro-momentum
ENTRY_THRESH     = 0.0008     # 0.08% move triggers entry
PROFIT_TARGET    = 0.003      # exit at +0.3%
STOP_LOSS        = 0.002      # exit at -0.2%
CHECK_INTERVAL   = 30
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'scalp.log')
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


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def main():
    balance = STARTING_BALANCE
    position = None   # dict: {price, size, side}
    prices = deque(maxlen=WINDOW)

    log(f"Scalp Bot started | Balance: ${balance:.2f}")

    while True:
        try:
            price = get_price()
            prices.append(price)

            if position is None:
                if len(prices) == WINDOW:
                    oldest = prices[0]
                    move = (price - oldest) / oldest

                    if move >= ENTRY_THRESH:
                        # Micro uptrend → long
                        size = round((balance * TRADE_FRACTION) / price, 6)
                        position = {'price': price, 'size': size, 'side': 'long'}
                        log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
                    elif move <= -ENTRY_THRESH:
                        # Micro downtrend → short
                        size = round((balance * TRADE_FRACTION) / price, 6)
                        position = {'price': price, 'size': size, 'side': 'short'}
                        log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
            else:
                entry = position['price']
                size  = position['size']
                side  = position['side']

                if side == 'long':
                    pct = (price - entry) / entry
                    if pct >= PROFIT_TARGET or pct <= -STOP_LOSS:
                        pnl = round((price - entry) * size, 4)
                        balance = round(balance + pnl, 2)
                        log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                        position = None
                else:  # short
                    pct = (entry - price) / entry
                    if pct >= PROFIT_TARGET or pct <= -STOP_LOSS:
                        pnl = round((entry - price) * size, 4)
                        balance = round(balance + pnl, 2)
                        log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                        position = None

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
