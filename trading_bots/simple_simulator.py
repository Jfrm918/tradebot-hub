#!/usr/bin/env python3
"""
Minimal Trading Bot Simulator - Clean Snapshot Writer
Focuses on: Real price data + clean snapshot writes (no initialization hangs)
"""

import json, time, logging, requests
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Bot] %(message)s',
    handlers=[
        logging.FileHandler('/Users/jfrm918/.openclaw/workspace/trading_bots/simulator.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('Bot')

SNAPSHOT_PATH = '/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json'
BLOFIN_TICKERS = 'https://openapi.blofin.com/api/v1/market/tickers'
PAIRS = ['BTC-USDT', 'ETH-USDT']

def fetch_tickers():
    try:
        r = requests.get(BLOFIN_TICKERS, timeout=5)
        if r.status_code != 200: return None
        out = {}
        for t in r.json().get('data', []):
            if t['instId'] in PAIRS:
                out[t['instId']] = float(t['last'])
        return out if len(out) == 2 else None
    except:
        return None

class SimpleBot:
    def __init__(self, name):
        self.name = name
        self.balance = 100.0
        self.pnl = 0.0
        self.trades = 0
        self.wins = 0
        self.position = None

def main():
    bots = {
        'momentum': SimpleBot('Momentum'),
        'reversion': SimpleBot('Mean Reversion'),
        'grid': SimpleBot('Grid'),
        'scalp': SimpleBot('Scalp'),
        'swing': SimpleBot('Swing'),
    }
    
    cycle = 0
    
    log.info("=" * 70)
    log.info("Simple Trading Bot Simulator")
    log.info("Real Blofin data, clean snapshots")
    log.info("=" * 70)
    
    while True:
        cycle += 1
        
        # Fetch prices
        prices = fetch_tickers()
        if not prices:
            log.warning(f"  Cycle {cycle}: API fetch failed")
            time.sleep(5)
            continue
        
        # Log every 10 cycles
        if cycle % 10 == 0:
            log.info(f"  Cycle {cycle:3} | BTC: ${prices['BTC-USDT']:,.2f} | ETH: ${prices['ETH-USDT']:,.2f}")
        
        # Write snapshot every 10 cycles
        if cycle % 10 == 0:
            snap = {
                'cycle': cycle,
                'timestamp': datetime.now().isoformat(),
                'prices': {
                    'BTC': round(prices['BTC-USDT'], 2),
                    'ETH': round(prices['ETH-USDT'], 2),
                },
                'bots': {
                    name: {
                        'balance': round(bot.balance, 2),
                        'pnl': round(bot.pnl, 2),
                        'trades': bot.trades,
                        'wins': bot.wins,
                    }
                    for name, bot in bots.items()
                }
            }
            with open(SNAPSHOT_PATH, 'w') as f:
                json.dump(snap, f, indent=2)
            log.info(f"  ✓ Snapshot written (Cycle {cycle})")
        
        time.sleep(5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.info("\n⏹ Stopped.")

