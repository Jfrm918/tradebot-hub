#!/usr/bin/env python3
"""Minimal 2-bot simulator: Momentum + Mean Reversion only"""
import json, time, requests, logging, numpy as np
from datetime import datetime
from collections import deque

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Bot] %(message)s',
    handlers=[logging.FileHandler('/Users/jfrm918/.openclaw/workspace/trading_bots/simulator.log')]
)
log = logging.getLogger()

SNAPSHOT = '/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json'
BLOFIN_TICKERS = 'https://openapi.blofin.com/api/v1/market/tickers'
BLOFIN_CANDLES = 'https://openapi.blofin.com/api/v1/market/candles'
PAIRS = ['BTC-USDT', 'ETH-USDT']

def fetch_tickers():
    try:
        r = requests.get(BLOFIN_TICKERS, timeout=5)
        if r.status_code != 200: return None
        out = {}
        for t in r.json().get('data', []):
            if t['instId'] in PAIRS:
                out[t['instId']] = {'price': float(t['last']), 'vol': float(t['volCurrency24h'])}
        return out if len(out) == 2 else None
    except:
        return None

def fetch_candles(pair, bar='1H', limit=50):
    try:
        r = requests.get(BLOFIN_CANDLES,
                         params={'instId': pair, 'bar': bar, 'limit': limit},
                         timeout=5)
        if r.status_code != 200: return []
        candles = []
        for row in reversed(r.json().get('data', [])):
            if row[8] == '1':
                candles.append(float(row[4]))  # close price only
        return candles
    except:
        return []

def compute_rsi(closes, period=14):
    if len(closes) < period + 1: return 50.0
    arr = np.array(closes[-(period+1):])
    deltas = np.diff(arr)
    gains = np.where(deltas > 0, deltas, 0).mean()
    losses = np.where(deltas < 0, -deltas, 0).mean()
    return 100 - 100 / (1 + gains / losses) if losses > 0 else 100.0

class Bot:
    def __init__(self, name, capital=100.0):
        self.name = name
        self.balance = capital
        self.pnl = 0.0
        self.trades = 0
        self.wins = 0
        self.position = None

    def open(self, entry, size=0.5):
        cost = self.balance * size
        self.position = {'entry': entry, 'size': cost / entry}

    def close(self, exit_price):
        if not self.position: return 0
        revenue = self.position['size'] * exit_price
        pnl = revenue - self.position['entry'] * self.position['size']
        self.balance += pnl
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
        self.hist = {p: deque(maxlen=100) for p in PAIRS}
        log.info("=== Momentum + Mean Reversion Simulator ===")

    def run_cycle(self):
        self.cycle += 1
        prices = fetch_tickers()
        if not prices: return False

        for pair in PAIRS:
            self.hist[pair].append(prices[pair]['price'])

        # Momentum: Random entry/exit (no blocking candle fetch)
        price_btc = prices[PAIRS[0]]['price']
        if not self.momentum.position and self.cycle % 12 == 1:
            self.momentum.open(price_btc, 0.3)
        elif self.momentum.position and self.cycle % 12 == 7:
            pnl = self.momentum.close(price_btc)

        # Mean Reversion: Random entry/exit
        price_eth = prices[PAIRS[1]]['price']
        if not self.reversion.position and self.cycle % 15 == 2:
            self.reversion.open(price_eth, 0.3)
        elif self.reversion.position and self.cycle % 15 == 9:
            pnl = self.reversion.close(price_eth)

        if self.cycle % 10 == 0:
            self.save_snapshot()
            log.info(f"Cycle {self.cycle}: MOM pnl={self.momentum.pnl:.2f} REV pnl={self.reversion.pnl:.2f}")

        return True

    def save_snapshot(self):
        snap = {
            'cycle': self.cycle,
            'timestamp': datetime.now().isoformat(),
            'bots': {
                'momentum': {
                    'balance': round(self.momentum.balance, 2),
                    'pnl': round(self.momentum.pnl, 2),
                    'trades': self.momentum.trades,
                    'wins': self.momentum.wins,
                },
                'reversion': {
                    'balance': round(self.reversion.balance, 2),
                    'pnl': round(self.reversion.pnl, 2),
                    'trades': self.reversion.trades,
                    'wins': self.reversion.wins,
                },
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
        if not sim.run_cycle():
            log.warning("API failed")
        time.sleep(5)
