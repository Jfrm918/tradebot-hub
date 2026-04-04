#!/usr/bin/env python3
import json
import re
import time
from pathlib import Path

LOG_DIR = Path('/Users/jfrm918/.openclaw/workspace/trading_bots/bots')
SNAPSHOT_PATH = Path('/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json')

BOT_MAP = {
    'momentum_bot.log': 'momentum',
    'mean_reversion_bot.log': 'reversion',
    'scalp_bot.log': 'scalp',
    'grid_bot.log': 'grid',
    'swing.log': 'swing',
    'vwap_reversion_bot.log': 'vwap_rev',
    'vwap_momentum_bot.log': 'vwap_mom'
}

def parse_bot_log(log_file):
    """Extract PnL, trades, wins, balance, open_position from bot log
    
    CRITICAL FIX: Only count trades from the log (not accumulated history).
    Use balance as the source of truth — it reflects all prior trades.
    """
    pnl = 0.0
    trades = 0
    wins = 0
    balance = 100.0  # Default per-bot allocation
    open_position = False
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
            # Get current balance from the LAST line with a balance field
            # This is the source of truth — it includes all trades so far
            for line in reversed(lines):
                if 'Balance:' in line:
                    match = re.search(r'Balance: \$([0-9.]+)', line)
                    if match:
                        balance = float(match.group(1))
                        break
            
            # Count trades by looking for SELL lines (completed trades)
            sell_lines = [line for line in lines if 'SELL' in line]
            trades = len(sell_lines)
            
            # Count wins from SELL lines that show positive PnL
            for sell_line in sell_lines:
                match = re.search(r'PnL: \$([0-9.-]+)', sell_line)
                if match:
                    pnl_val = float(match.group(1))
                    if pnl_val > 0:
                        wins += 1
            
            # Check if position is open: last line is BUY or last line is SELL?
            if lines:
                last_trade_line = [l for l in reversed(lines) if 'BUY' in l or 'SELL' in l]
                if last_trade_line and 'BUY' in last_trade_line[0]:
                    open_position = True
            
            # PnL is derived from balance change: balance - starting capital (100)
            pnl = balance - 100.0
    except:
        pass
    
    return {
        'pnl': round(pnl, 2),
        'trades': trades,
        'wins': wins,
        'balance': round(balance, 2),
        'open_position': open_position
    }

def write_snapshot():
    """Compile all bot logs into snapshot.json"""
    snapshot = {'cycle': 1, 'bots': {}}
    
    for log_name, bot_key in BOT_MAP.items():
        log_path = LOG_DIR / log_name
        snapshot['bots'][bot_key] = parse_bot_log(log_path)
    
    with open(SNAPSHOT_PATH, 'w') as f:
        json.dump(snapshot, f, indent=2)

if __name__ == '__main__':
    while True:
        write_snapshot()
        time.sleep(60)
