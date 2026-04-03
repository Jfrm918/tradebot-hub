#!/usr/bin/env python3
import json, time, requests
from datetime import datetime
from pathlib import Path

SNAPSHOT = '/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json'
BLOFIN = 'https://openapi.blofin.com/api/v1/market/tickers'

def fetch():
    try:
        r = requests.get(BLOFIN, timeout=5)
        if r.status_code == 200:
            data = r.json()['data']
            return {t['instId']: float(t['last']) for t in data if t['instId'] in ['BTC-USDT', 'ETH-USDT']}
    except:
        pass
    return None

cycle = 0
while True:
    cycle += 1
    prices = fetch()
    if prices and cycle % 10 == 0:
        snap = {
            'cycle': cycle,
            'timestamp': datetime.now().isoformat(),
            'prices': {'BTC': prices.get('BTC-USDT', 0), 'ETH': prices.get('ETH-USDT', 0)},
            'bots': {
                'momentum': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
                'reversion': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
                'grid': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
                'scalp': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
                'swing': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
            }
        }
        with open(SNAPSHOT, 'w') as f:
            json.dump(snap, f, indent=2)
        with open('/tmp/bot_status.txt', 'a') as f:
            f.write(f"Cycle {cycle}: Snapshot written\n")
    time.sleep(5)
