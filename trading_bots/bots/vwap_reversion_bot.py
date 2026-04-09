#!/usr/bin/env python3
"""
VWAP Reversion Bot — BTC strategy
Simulates VWAP using price-weighted rolling accumulator.
Enters when price deviates from VWAP, exits on reversion to mean.
$100 starting capital. No config.json dependency.

Price sources (in priority order):
  1. Coinbase  — api.coinbase.com (free, no auth)
  2. Kraken    — api.kraken.com   (free, no auth)
  3. CoinGecko — api.coingecko.com (free, no auth)
"""

import time
import requests
from datetime import datetime
import os

# ─── Config ───────────────────────────────────────────────────────────────────
SYMBOL           = "BTC-USDT"
STARTING_BALANCE = 1000.0
TRADE_FRACTION   = 0.95
VWAP_WINDOW      = 20         # reset VWAP accumulator every N ticks
ENTRY_DEV_PCT    = 0.003      # enter when price >0.3% from VWAP
EXIT_DEV_PCT     = 0.001      # exit when within 0.1% of VWAP
STOP_LOSS_PCT    = 0.005      # hard stop at -0.5%
CHECK_INTERVAL   = 30
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'vwap_rev.log')
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
    balance  = STARTING_BALANCE
    position = None

    # VWAP accumulators (treat each tick as equal volume)
    price_sum = 0.0
    tick_count = 0

    log(f"VWAP Reversion Bot started | Balance: ${balance:.2f}")

    while True:
        try:
            price = get_price()
            tick_count += 1
            price_sum  += price

            # Reset VWAP window periodically
            if tick_count % VWAP_WINDOW == 0:
                vwap       = price_sum / tick_count
                price_sum  = 0.0
                tick_count = 0
            else:
                vwap = price_sum / tick_count if tick_count > 0 else price

            dev = (price - vwap) / vwap

            if position is None:
                if dev <= -ENTRY_DEV_PCT:
                    # Price below VWAP → expect reversion up → long
                    size = round((balance * TRADE_FRACTION) / price, 6)
                    position = {'price': price, 'size': size, 'side': 'long'}
                    log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
                elif dev >= ENTRY_DEV_PCT:
                    # Price above VWAP → expect reversion down → short
                    size = round((balance * TRADE_FRACTION) / price, 6)
                    position = {'price': price, 'size': size, 'side': 'short'}
                    log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")
            else:
                entry = position['price']
                size  = position['size']
                side  = position['side']

                if side == 'long':
                    pct      = (price - entry) / entry
                    reverted = dev >= -EXIT_DEV_PCT
                    if reverted or pct <= -STOP_LOSS_PCT:
                        pnl = round((price - entry) * size, 4)
                        balance = round(balance + pnl, 2)
                        log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                        position = None
                else:  # short
                    pct      = (entry - price) / entry
                    reverted = dev <= EXIT_DEV_PCT
                    if reverted or pct <= -STOP_LOSS_PCT:
                        pnl = round((entry - price) * size, 4)
                        balance = round(balance + pnl, 2)
                        log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                        position = None

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
