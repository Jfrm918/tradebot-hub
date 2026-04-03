#!/usr/bin/env python3
"""Core 2-bot simulator — no logging, direct snapshots"""
import json, time, requests, numpy as np
from datetime import datetime
from collections import deque

SNAPSHOT = '/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json'
BLOFIN_TICKERS = 'https://openapi.blofin.com/api/v1/market/tickers'
PAIRS = ['BTC-USDT', 'ETH-USDT']

def fetch_tickers():
    try:
        r = requests.get(BLOFIN_TICKERS, timeout=3)
        if r.status_code != 200: return None
        out = {}
        for t in r.json().get('data', []):
            if t['instId'] in PAIRS:
                out[t['instId']] = float(t['last'])
        return out if len(out) == 2 else None
    except:
        return None

class Bot:
    def __init__(self, name):
        self.name = name
        self.balance = 100.0
        self.pnl = 0.0
        self.trades = 0
        self.wins = 0
        self.position = None

    def open(self, entry, size=0.5):
        cost = self.balance * size
        self.position = {'entry': entry, 'size': cost / entry if entry > 0 else 0}

    def close(self, exit_price):
        if not self.position: return 0
        revenue = self.position['size'] * exit_price
        pnl = revenue - self.position['entry'] * self.position['size']
        self.balance = max(1, self.balance + pnl)
        self.pnl += pnl
        self.trades += 1
        if pnl > 0: self.wins += 1
        self.position = None
        return pnl

class Sim:
    def __init__(self):
        self.momentum = Bot('momentum')
        self.reversion = Bot('reversion')
        self.cycle = 0

    def run_cycle(self):
        self.cycle += 1
        prices = fetch_tickers()
        if not prices: return False

        price_btc = prices.get(PAIRS[0], 0)
        price_eth = prices.get(PAIRS[1], 0)

        # Momentum: Simple cycle-based trading
        if self.cycle % 12 == 1 and price_btc > 0:
            self.momentum.open(price_btc, 0.3)
        elif self.momentum.position and self.cycle % 12 == 7:
            self.momentum.close(price_btc)

        # Reversion: Simple cycle-based trading
        if self.cycle % 15 == 2 and price_eth > 0:
            self.reversion.open(price_eth, 0.3)
        elif self.reversion.position and self.cycle % 15 == 9:
            self.reversion.close(price_eth)

        # Save snapshot every 10 cycles
        if self.cycle % 10 == 0:
            self.save_snapshot()

        return True

    def save_snapshot(self):
        snap = {
            'cycle': self.cycle,
            'timestamp': datetime.now().isoformat(),
            'bots': {
                'momentum': {'balance': round(self.momentum.balance, 2), 'pnl': round(self.momentum.pnl, 2), 'trades': self.momentum.trades, 'wins': self.momentum.wins},
                'reversion': {'balance': round(self.reversion.balance, 2), 'pnl': round(self.reversion.pnl, 2), 'trades': self.reversion.trades, 'wins': self.reversion.wins},
                'grid': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
                'scalp': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
                'swing': {'balance': 100.0, 'pnl': 0.0, 'trades': 0, 'wins': 0},
            }
        }
        with open(SNAPSHOT, 'w') as f:
            json.dump(snap, f, indent=2)

if __name__ == '__main__':
    sim = Sim()
    while True:
        sim.run_cycle()
        time.sleep(5)
