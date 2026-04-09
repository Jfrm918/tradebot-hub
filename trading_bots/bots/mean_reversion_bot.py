#!/usr/bin/env python3
"""
Mean Reversion Bot — BTC strategy
Enters when price deviates significantly from rolling mean, exits on reversion.
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
import statistics

# ─── Config ───────────────────────────────────────────────────────────────────
SYMBOL           = "BTC-USDT"
STARTING_BALANCE = 100.0
TRADE_FRACTION   = 0.95
WINDOW           = 10        # rolling mean window (number of ticks)
ENTRY_ZSCORE     = 1.5       # enter when price is 1.5 std devs from mean
EXIT_ZSCORE      = 0.2       # exit when price reverts near mean
STOP_LOSS        = 0.005     # -0.5% hard stop
CHECK_INTERVAL   = 30
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'reversion.log')
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

    log(f"Mean Reversion Bot started | Balance: ${balance:.2f}")

    while True:
        try:
            price = get_price()
            prices.append(price)

            if len(prices) < WINDOW:
                time.sleep(CHECK_INTERVAL)
                continue

            mean  = statistics.mean(prices)
            stdev = statistics.stdev(prices)

            if stdev == 0:
                time.sleep(CHECK_INTERVAL)
                continue

            zscore = (price - mean) / stdev

            if position is None:
                if zscore <= -ENTRY_ZSCORE:
                    # Price well below mean — expect reversion up → long
                    size = round((balance * TRADE_FRACTION) / price, 6)
                    position = {'price': price, 'size': size, 'side': 'long'}
                    log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
                elif zscore >= ENTRY_ZSCORE:
                    # Price well above mean — expect reversion down → short
                    size = round((balance * TRADE_FRACTION) / price, 6)
                    position = {'price': price, 'size': size, 'side': 'short'}
                    log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
            else:
                entry = position['price']
                size  = position['size']
                side  = position['side']

                if side == 'long':
                    pct = (price - entry) / entry
                    if abs(zscore) <= EXIT_ZSCORE or pct <= -STOP_LOSS:
                        pnl = round((price - entry) * size, 4)
                        balance = round(balance + pnl, 2)
                        log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                        position = None
                else:  # short
                    pct = (entry - price) / entry
                    if abs(zscore) <= EXIT_ZSCORE or pct <= -STOP_LOSS:
                        pnl = round((entry - price) * size, 4)
                        balance = round(balance + pnl, 2)
                        log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                        position = None

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
