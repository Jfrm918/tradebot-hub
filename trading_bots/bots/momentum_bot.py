#!/usr/bin/env python3
"""
Momentum Bot — BTC trend-following strategy
Enters on upward price momentum, exits on reversal or profit target.
Logs in standardized format. $100 starting capital. No config.json dependency.

Price sources (in priority order):
  1. Coinbase  — api.coinbase.com (free, no auth)
  2. Kraken    — api.kraken.com   (free, no auth)
  3. CoinGecko — api.coingecko.com (free, no auth)
  [Binance blocked in US — kept as reference only]
"""

import time
import requests
from datetime import datetime
from collections import deque
import os

# ─── Config ───────────────────────────────────────────────────────────────────
SYMBOL           = "BTC-USDT"
STARTING_BALANCE = 1000.0
TRADE_FRACTION   = 0.95       # fraction of balance to deploy per trade
MOMENTUM_WINDOW  = 5          # number of price samples for momentum calc
MOMENTUM_THRESH  = 0.0015     # 0.15% move = signal
PROFIT_TARGET    = 0.005      # exit at +0.5%
STOP_LOSS        = 0.003      # exit at -0.3%
CHECK_INTERVAL   = 30         # seconds between price checks
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'momentum.log')
# ──────────────────────────────────────────────────────────────────────────────


def get_price():
    """Fetch BTC/USD price with multi-source fallback."""
    # 1. Coinbase
    try:
        r = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot', timeout=10)
        r.raise_for_status()
        return float(r.json()['data']['amount'])
    except Exception:
        pass
    # 2. Kraken
    try:
        r = requests.get('https://api.kraken.com/0/public/Ticker?pair=XBTUSD', timeout=10)
        r.raise_for_status()
        return float(r.json()['result']['XXBTZUSD']['c'][0])
    except Exception:
        pass
    # 3. CoinGecko
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
    position = None   # dict: {price, size}
    prices = deque(maxlen=MOMENTUM_WINDOW)

    log(f"Momentum Bot started | Balance: ${balance:.2f}")

    while True:
        try:
            price = get_price()
            prices.append(price)

            if position is None:
                if len(prices) == MOMENTUM_WINDOW:
                    oldest = prices[0]
                    momentum = (price - oldest) / oldest
                    if momentum >= MOMENTUM_THRESH:
                        size = round((balance * TRADE_FRACTION) / price, 6)
                        position = {'price': price, 'size': size}
                        log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
            else:
                entry = position['price']
                size  = position['size']
                pct   = (price - entry) / entry

                if pct >= PROFIT_TARGET or pct <= -STOP_LOSS:
                    pnl = round((price - entry) * size, 4)
                    balance = round(balance + pnl, 2)
                    log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                    position = None

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
