#!/usr/bin/env python3
"""Paper Trading Simulator - Random walk prices, no API calls"""
import json, time, random, numpy as np
from datetime import datetime

SNAPSHOT = '/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json'

def random_walk_price(start, volatility=0.005, drift=0.0):
    """Generate next price from random walk"""
    return start * (1 + drift + volatility * np.random.normal(0, 1))

class Bot:
    def __init__(self, name):
        self.name = name
        self.balance = 100.0
        self.pnl = 0.0
        self.trades = 0
        self.wins = 0
        self.position = None

    def open(self, entry, size=0.3):
        if self.balance < 1: return False
        cost = self.balance * size
        self.position = {'entry': entry, 'size': cost / entry if entry > 0 else 0}
        return True

    def close(self, exit_price):
        if not self.position: return 0
        revenue = self.position['size'] * exit_price
        pnl = revenue - (self.position['entry'] * self.position['size'])
        self.balance = max(1, self.balance + pnl)
        self.pnl += pnl
        self.trades += 1
        if pnl > 0: self.wins += 1
        self.position = None
        return pnl

class PaperTrader:
    def __init__(self):
        self.cycle = 0
        self.btc_price = 66800.0
        self.eth_price = 2058.0
        
        self.momentum = Bot('momentum')
        self.reversion = Bot('reversion')
        self.grid = Bot('grid')
        self.scalp = Bot('scalp')
        self.swing = Bot('swing')
        
        self.rsi_btc = 50
        self.rsi_eth = 50

    def update_prices(self):
        """Random walk with realistic volatility"""
        self.btc_price = random_walk_price(self.btc_price, volatility=0.008, drift=0.0001)
        self.eth_price = random_walk_price(self.eth_price, volatility=0.01, drift=0.00005)
        
        # Simulate RSI changes (0-100)
        self.rsi_btc = max(10, min(90, self.rsi_btc + np.random.normal(0, 3)))
        self.rsi_eth = max(10, min(90, self.rsi_eth + np.random.normal(0, 3)))

    def run_momentum(self):
        """Buy oversold, sell overbought"""
        if not self.momentum.position and self.rsi_btc < 35:
            self.momentum.open(self.btc_price, 0.25)
        elif self.momentum.position and self.rsi_btc > 75:
            self.momentum.close(self.btc_price)

    def run_reversion(self):
        """Mean reversion on ETH"""
        if not self.reversion.position and self.rsi_eth > 70:
            self.reversion.open(self.eth_price, 0.3)
        elif self.reversion.position and self.rsi_eth < 30:
            self.reversion.close(self.eth_price)

    def run_grid(self):
        """Grid oscillation trading"""
        if not self.grid.position and self.cycle % 18 == 1:
            self.grid.open(self.btc_price, 0.15)
        elif self.grid.position and self.cycle % 18 == 10:
            self.grid.close(self.btc_price)

    def run_scalp(self):
        """High frequency small trades"""
        if not self.scalp.position and self.cycle % 8 == 2:
            self.scalp.open(self.eth_price, 0.25)
        elif self.scalp.position and self.cycle % 8 == 5:
            self.scalp.close(self.eth_price)

    def run_swing(self):
        """Swing trades on 4H equivalent"""
        if not self.swing.position and self.rsi_btc < 40 and self.cycle % 24 == 3:
            self.swing.open(self.btc_price, 0.4)
        elif self.swing.position and (self.rsi_btc > 65 or self.cycle % 24 == 20):
            self.swing.close(self.btc_price)

    def run_cycle(self):
        self.cycle += 1
        self.update_prices()
        self.run_momentum()
        self.run_reversion()
        self.run_grid()
        self.run_scalp()
        self.run_swing()

    def save_snapshot(self):
        snap = {
            'cycle': self.cycle,
            'timestamp': datetime.now().isoformat(),
            'prices': {
                'BTC': round(self.btc_price, 2),
                'ETH': round(self.eth_price, 2),
            },
            'indicators': {
                'rsi_btc': round(self.rsi_btc, 1),
                'rsi_eth': round(self.rsi_eth, 1),
            },
            'bots': {
                'momentum': {'balance': round(self.momentum.balance, 2), 'pnl': round(self.momentum.pnl, 2), 'trades': self.momentum.trades, 'wins': self.momentum.wins},
                'reversion': {'balance': round(self.reversion.balance, 2), 'pnl': round(self.reversion.pnl, 2), 'trades': self.reversion.trades, 'wins': self.reversion.wins},
                'grid': {'balance': round(self.grid.balance, 2), 'pnl': round(self.grid.pnl, 2), 'trades': self.grid.trades, 'wins': self.grid.wins},
                'scalp': {'balance': round(self.scalp.balance, 2), 'pnl': round(self.scalp.pnl, 2), 'trades': self.scalp.trades, 'wins': self.scalp.wins},
                'swing': {'balance': round(self.swing.balance, 2), 'pnl': round(self.swing.pnl, 2), 'trades': self.swing.trades, 'wins': self.swing.wins},
            }
        }
        with open(SNAPSHOT, 'w') as f:
            json.dump(snap, f, indent=2)

if __name__ == '__main__':
    trader = PaperTrader()
    while True:
        trader.run_cycle()
        if trader.cycle % 12 == 0:  # Save every 60 seconds (5s * 12)
            trader.save_snapshot()
        time.sleep(5)
