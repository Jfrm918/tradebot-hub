#!/usr/bin/env python3
"""
Grid Bot — BTC range-bound strategy
Places virtual buy/sell grid levels around current price.
Fills grid orders as price crosses levels. $100 starting capital. No config.json.

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
STARTING_BALANCE = 100.0
GRID_LEVELS      = 5          # number of buy/sell levels each side
GRID_SPACING_PCT = 0.002      # 0.2% between grid levels
TRADE_FRACTION   = 0.10       # fraction of balance per grid level
GRID_RESET_PCT   = 0.02       # rebuild grid if price drifts >2% from center
CHECK_INTERVAL   = 30
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'grid.log')
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


def build_grid(center_price):
    """Build buy levels below center and sell levels above."""
    buys  = []
    sells = []
    for i in range(1, GRID_LEVELS + 1):
        buys.append(round(center_price * (1 - i * GRID_SPACING_PCT), 2))
        sells.append(round(center_price * (1 + i * GRID_SPACING_PCT), 2))
    return buys, sells


def main():
    balance = STARTING_BALANCE
    positions    = {}    # buy_level_price -> {price, size}
    prev_price   = None
    grid_center  = None
    buy_levels   = []
    sell_levels  = []

    log(f"Grid Bot started | Balance: ${balance:.2f}")

    while True:
        try:
            price = get_price()

            # Initialize or rebuild grid if price drifts too far from center
            if grid_center is None or abs(price - grid_center) / grid_center > GRID_RESET_PCT:
                grid_center = price
                buy_levels, sell_levels = build_grid(grid_center)
                positions = {}
                log(f"GRID SET center=${grid_center:.2f} | "
                    f"buy_levels={[f'${p:.0f}' for p in buy_levels[:2]]}... "
                    f"sell_levels={[f'${p:.0f}' for p in sell_levels[:2]]}...")

            if prev_price is not None:
                # Check buy triggers — price crossed down through a buy level
                for level in buy_levels:
                    if prev_price > level >= price and level not in positions:
                        alloc = balance * TRADE_FRACTION
                        if alloc < 0.50:
                            continue
                        size = round(alloc / price, 6)
                        positions[level] = {'price': price, 'size': size}
                        log(f"BUY {SYMBOL} @ ${price:.2f} | Size: {size:.6f} | Balance: ${balance:.2f}")

                # Check sell triggers — price crossed up through a sell level
                for sell_level in sell_levels:
                    if prev_price < sell_level <= price:
                        for buy_level, pos in list(positions.items()):
                            if buy_level < sell_level:
                                pnl = round((price - pos['price']) * pos['size'], 4)
                                balance = round(balance + pnl, 2)
                                log(f"SELL {SYMBOL} @ ${price:.2f} | Size: {pos['size']:.6f} | PnL: ${pnl:.4f} | Balance: ${balance:.2f}")
                                del positions[buy_level]
                                break

            prev_price = price

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
