#!/usr/bin/env python3
"""
Olympus Snapshot Writer
Reads bot log files, parses trades, writes snapshot.json every 10 seconds.
Parses standardized format:
  [TIMESTAMP] BUY BTC-USDT @ $84000.00 | Size: 0.001 | Balance: $100.00
  [TIMESTAMP] SELL BTC-USDT @ $84500.00 | Size: 0.001 | PnL: $0.50 | Balance: $100.50
"""

import json
import time
import os
import re
from datetime import datetime

# Working directory — all paths relative to this
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Map bot keys to their log files
BOT_MAP = {
    'momentum': os.path.join(BASE_DIR, 'logs', 'momentum.log'),
    'reversion': os.path.join(BASE_DIR, 'logs', 'reversion.log'),
    'grid': os.path.join(BASE_DIR, 'logs', 'grid.log'),
    'scalp': os.path.join(BASE_DIR, 'logs', 'scalp.log'),
    'swing': os.path.join(BASE_DIR, 'logs', 'swing.log'),
    'vwap_rev': os.path.join(BASE_DIR, 'logs', 'vwap_rev.log'),
    'vwap_mom': os.path.join(BASE_DIR, 'logs', 'vwap_mom.log'),
}

SNAPSHOT_PATH = os.path.join(BASE_DIR, 'snapshot.json')

TOURNAMENT_START = '2026-04-04'
CYCLE = 1
CYCLE_END = '2026-04-18'


def parse_log(log_path):
    """
    Parse a bot log file and return trade statistics.
    Primary: parse Size: and PnL: fields directly from standardized log format.
    """
    result = {
        'pnl': 0.0,
        'trades': 0,
        'wins': 0,
        'balance': 100.0,
        'open_position': False,
        'last_trade': None,
    }

    if not os.path.exists(log_path):
        return result

    try:
        with open(log_path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception:
        return result

    if not lines:
        return result

    total_pnl  = 0.0
    trades     = 0
    wins       = 0
    balance    = 100.0
    last_action = None
    open_buy   = False   # track if last trade action was a buy with no matching sell
    pending_buys = []    # track open long positions for fallback PnL calc

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # ── Extract balance (always present on trade lines) ────────────────
        bal_match = re.search(r'Balance:\s*\$?([\d.]+)', line)
        if bal_match:
            try:
                balance = float(bal_match.group(1))
            except Exception:
                pass

        # ── Check for PnL field (on SELL/close lines) ─────────────────────
        pnl_match = re.search(r'PnL:\s*\$?([-\d.]+)', line)
        size_match = re.search(r'Size:\s*([\d.]+)', line)
        price_match = re.search(r'@\s*\$?([\d.]+)', line)

        is_buy  = bool(re.search(r'\bBUY\b', line, re.IGNORECASE))
        is_sell = bool(re.search(r'\bSELL\b', line, re.IGNORECASE))
        is_close = bool(re.search(r'\b(CLOSE|EXIT|CLOSED)\b', line, re.IGNORECASE))

        # Skip non-trade lines (e.g. startup messages, GRID SET, ERROR)
        if not price_match:
            continue
        if not (is_buy or is_sell or is_close):
            continue

        if pnl_match:
            # Line has explicit PnL — use it directly
            try:
                pnl_val = float(pnl_match.group(1))
                total_pnl = round(total_pnl + pnl_val, 6)
                trades += 1
                if pnl_val > 0:
                    wins += 1
                last_action = 'close'
                open_buy = False
                result['last_trade'] = line
            except Exception:
                pass
        elif is_buy and not is_sell:
            # Opening a long position — record it
            try:
                buy_price = float(price_match.group(1))
                size_val  = float(size_match.group(1)) if size_match else 0.0
                pending_buys.append({'price': buy_price, 'size': size_val})
                last_action = 'BUY'
                open_buy = True
            except Exception:
                pass
        elif (is_sell or is_close) and not pnl_match:
            # Sell without explicit PnL — calculate from pending buy
            try:
                sell_price = float(price_match.group(1))
                size_val   = float(size_match.group(1)) if size_match else 0.0
                if pending_buys:
                    buy = pending_buys.pop(0)
                    pnl_val = round((sell_price - buy['price']) * (size_val or buy['size']), 4)
                    total_pnl = round(total_pnl + pnl_val, 6)
                    trades += 1
                    if pnl_val > 0:
                        wins += 1
                    last_action = 'SELL'
                    open_buy = False
                    result['last_trade'] = line
            except Exception:
                pass

    result['pnl']          = round(total_pnl, 4)
    result['trades']       = trades
    result['wins']         = wins
    result['balance']      = round(balance, 2)
    result['open_position'] = open_buy or (last_action == 'BUY' and len(pending_buys) > 0)

    return result


def write_snapshot():
    bots = {}
    for bot_key, log_path in BOT_MAP.items():
        bots[bot_key] = parse_log(log_path)

    snapshot = {
        'cycle': CYCLE,
        'tournament_start': TOURNAMENT_START,
        'cycle_end': CYCLE_END,
        'last_updated': datetime.now().isoformat(),
        'bots': bots
    }
    tmp_path = SNAPSHOT_PATH + '.tmp'
    with open(tmp_path, 'w') as f:
        json.dump(snapshot, f, indent=2)
    os.replace(tmp_path, SNAPSHOT_PATH)

    # Print summary
    total_trades = sum(b['trades'] for b in bots.values())
    total_pnl    = sum(b['pnl'] for b in bots.values())
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot written — "
          f"{total_trades} trades, PnL: ${total_pnl:.4f}", flush=True)


def main():
    print(f"Snapshot writer starting — monitoring {len(BOT_MAP)} bots", flush=True)
    print(f"Base dir: {BASE_DIR}", flush=True)
    for key, path in BOT_MAP.items():
        exists = os.path.exists(path)
        print(f"  {key}: {path} — {'EXISTS' if exists else 'NOT FOUND'}", flush=True)

    while True:
        try:
            write_snapshot()
        except Exception as e:
            print(f"Error writing snapshot: {e}", flush=True)
        time.sleep(10)


if __name__ == '__main__':
    main()
