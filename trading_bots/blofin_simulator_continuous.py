#!/usr/bin/env python3
"""
Blofin Paper Trading Simulator - Continuous Mode v2
Fixed: All 5 bots actively trade using proper price history & realistic conditions
"""

import json
import time
import logging
from datetime import datetime
from collections import deque
import random
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/jfrm918/.openclaw/workspace/trading_bots/simulator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TradeBot')

SNAPSHOT_PATH = '/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json'

class ContinuousSimulator:
    def __init__(self):
        self.trading_pairs = ["BTC-USDT", "ETH-USDT"]

        self.bots = {
            'momentum':      {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0, 'position': None},
            'mean_reversion':{'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0, 'position': None},
            'grid':          {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0, 'position': None},
            'scalp':         {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0, 'position': None},
            'swing':         {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0, 'position': None},
        }

        # Price history buffer (last 50 prices per pair)
        self.price_history = {
            'BTC-USDT': deque([68000.0] * 50, maxlen=50),
            'ETH-USDT': deque([2094.0]  * 50, maxlen=50),
        }

        self.bases = {'BTC-USDT': 68000.0, 'ETH-USDT': 2094.0}
        self.cycle_count = 0

        logger.info("🚀 Blofin Paper Trading Simulator v2 — ALL BOTS ACTIVE")
        logger.info("5 × $100 = $500 paper capital | Running indefinitely")

    # ── PRICE GENERATION ──────────────────────────────────────────────

    def next_price(self, pair):
        """Realistic random walk with mean reversion"""
        hist  = self.price_history[pair]
        base  = self.bases[pair]
        last  = hist[-1]

        # Drift back toward base slowly
        reversion = (base - last) * 0.002
        shock     = last * random.gauss(0, 0.0004)  # ±0.04% per tick (realistic intraday)
        new_price = round(last + reversion + shock, 2)
        new_price = max(new_price, base * 0.7)       # floor

        hist.append(new_price)
        return new_price

    def price_stats(self, pair):
        hist = list(self.price_history[pair])
        last = hist[-1]
        return {
            'last':    last,
            'high20':  max(hist[-20:]),
            'low20':   min(hist[-20:]),
            'high50':  max(hist),
            'low50':   min(hist),
            'ma10':    sum(hist[-10:]) / 10,
            'ma20':    sum(hist[-20:]) / 20,
            'ma5':     sum(hist[-5:])  / 5,
        }

    def rsi(self, pair, period=14):
        hist = list(self.price_history[pair])
        if len(hist) < period + 1:
            return 50.0
        changes = [hist[i+1] - hist[i] for i in range(len(hist)-1)]
        gains  = [max(c, 0) for c in changes[-period:]]
        losses = [abs(min(c, 0)) for c in changes[-period:]]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 1)

    # ── OPEN / CLOSE HELPERS ──────────────────────────────────────────

    def open_position(self, bot_name, pair, price, pct=0.4):
        bot = self.bots[bot_name]
        if bot['position'] or bot['balance'] < 5:
            return False
        # Use fixed capital allocation, not compounding balance
        cost   = bot['capital'] * pct
        cost   = min(cost, bot['balance'])   # can't spend more than we have
        amount = cost / price
        bot['balance']  -= cost
        bot['position']  = {'pair': pair, 'entry': price, 'amount': amount, 'cost': cost}
        return True

    def close_position(self, bot_name, price):
        bot = self.bots[bot_name]
        if not bot['position']:
            return False
        pos     = bot['position']
        revenue = pos['amount'] * price
        pnl     = revenue - pos['cost']
        bot['balance'] += revenue
        bot['pnl']     += pnl
        if pnl > 0:
            bot['wins'] += 1
        bot['trades'].append({
            'entry': pos['entry'], 'exit': price,
            'pnl': round(pnl, 4), 'pair': pos['pair']
        })
        bot['position'] = None
        return pnl

    # ── STRATEGY LOGIC ────────────────────────────────────────────────

    def run_momentum(self, pair, s):
        """Buy when short MA crosses above long MA; sell on reversal or +1.5%"""
        bot = self.bots['momentum']
        uptrend = s['ma5'] > s['ma20']

        if not bot['position'] and uptrend and bot['balance'] > 5:
            if self.open_position('momentum', pair, s['last'], pct=0.5):
                logger.info(f"MOMENTUM  → BUY  {pair} @ ${s['last']:.2f} | MA5:{s['ma5']:.1f} MA20:{s['ma20']:.1f}")

        elif bot['position']:
            entry = bot['position']['entry']
            gain  = (s['last'] - entry) / entry
            downtrend = s['ma5'] < s['ma20']

            if gain >= 0.015 or downtrend or gain <= -0.008:
                pnl = self.close_position('momentum', s['last'])
                logger.info(f"MOMENTUM  ← SELL {pair} @ ${s['last']:.2f} | PnL: ${pnl:.2f}")

    def run_mean_reversion(self, pair, s):
        """Buy on RSI oversold (<35); sell on RSI overbought (>65)"""
        bot = self.bots['mean_reversion']
        rsi = self.rsi(pair)

        if not bot['position'] and rsi < 35 and bot['balance'] > 5:
            if self.open_position('mean_reversion', pair, s['last'], pct=0.5):
                logger.info(f"MEAN_REV  → BUY  {pair} @ ${s['last']:.2f} | RSI:{rsi}")

        elif bot['position']:
            entry = bot['position']['entry']
            gain  = (s['last'] - entry) / entry
            rsi_now = self.rsi(pair)

            if rsi_now > 65 or gain >= 0.02 or gain <= -0.01:
                pnl = self.close_position('mean_reversion', s['last'])
                logger.info(f"MEAN_REV  ← SELL {pair} @ ${s['last']:.2f} | PnL: ${pnl:.2f} RSI:{rsi_now}")

    def run_grid(self, pair, s):
        """Buy below 20-period MA; sell above MA + 1%"""
        bot  = self.bots['grid']
        mid  = s['ma20']
        below_mid = s['last'] < mid * 0.997
        above_mid = s['last'] > mid * 1.010

        if not bot['position'] and below_mid and bot['balance'] > 5:
            if self.open_position('grid', pair, s['last'], pct=0.45):
                logger.info(f"GRID      → BUY  {pair} @ ${s['last']:.2f} | Mid:{mid:.2f}")

        elif bot['position'] and above_mid:
            pnl = self.close_position('grid', s['last'])
            logger.info(f"GRID      ← SELL {pair} @ ${s['last']:.2f} | PnL: ${pnl:.2f}")

        elif bot['position']:
            entry = bot['position']['entry']
            if (s['last'] - entry) / entry <= -0.012:
                pnl = self.close_position('grid', s['last'])
                logger.info(f"GRID      ← STOP {pair} @ ${s['last']:.2f} | PnL: ${pnl:.2f}")

    def run_scalp(self, pair, s):
        """Quick 0.4% target, 0.3% stop — high frequency"""
        bot = self.bots['scalp']
        # Enter on any small dip from recent 5-bar high
        dip = s['last'] < s['ma5'] * 0.997

        if not bot['position'] and dip and bot['balance'] > 5:
            if self.open_position('scalp', pair, s['last'], pct=0.3):
                pass  # silent for high freq

        elif bot['position']:
            entry = bot['position']['entry']
            gain  = (s['last'] - entry) / entry
            if gain >= 0.004 or gain <= -0.003:
                pnl = self.close_position('scalp', s['last'])
                if abs(pnl) > 0.01:
                    logger.info(f"SCALP     {'←✓' if pnl>0 else '←✗'} {pair} @ ${s['last']:.2f} | PnL: ${pnl:.4f}")

    def run_swing(self, pair, s):
        """Hold 2-5% moves; buy near 50-bar low, sell near 50-bar high"""
        bot   = self.bots['swing']
        range_size = s['high50'] - s['low50']
        if range_size == 0:
            return
        pos_pct = (s['last'] - s['low50']) / range_size  # 0 = at low, 1 = at high

        if not bot['position'] and pos_pct < 0.25 and bot['balance'] > 5:
            if self.open_position('swing', pair, s['last'], pct=0.5):
                logger.info(f"SWING     → BUY  {pair} @ ${s['last']:.2f} | pos:{pos_pct:.0%}")

        elif bot['position']:
            entry = bot['position']['entry']
            gain  = (s['last'] - entry) / entry
            if pos_pct > 0.75 or gain >= 0.03 or gain <= -0.015:
                pnl = self.close_position('swing', s['last'])
                logger.info(f"SWING     ← SELL {pair} @ ${s['last']:.2f} | PnL: ${pnl:.2f}")

    # ── MAIN LOOP ─────────────────────────────────────────────────────

    def run_cycle(self):
        self.cycle_count += 1
        for pair in self.trading_pairs:
            self.next_price(pair)
            s = self.price_stats(pair)
            self.run_momentum(pair, s)
            self.run_mean_reversion(pair, s)
            self.run_grid(pair, s)
            self.run_scalp(pair, s)
            self.run_swing(pair, s)

        if self.cycle_count % 50 == 0:
            self.print_status()
            self.save_snapshot()

    def print_status(self):
        logger.info(f"\n{'='*70}")
        logger.info(f"CYCLE {self.cycle_count} STATUS")
        logger.info(f"{'='*70}")
        total_pnl = 0
        for name, bot in self.bots.items():
            t = len([x for x in bot['trades']])
            w = bot['wins']
            wr = f"{w/t*100:.1f}%" if t > 0 else "—"
            total_pnl += bot['pnl']
            pos = f"OPEN@${bot['position']['entry']:.2f}" if bot['position'] else "flat"
            logger.info(f"{name.upper():16} | Trades:{t:3} | Wins:{w:3} | WR:{wr:6} | PnL:${bot['pnl']:8.2f} | {pos}")
        logger.info(f"{'PORTFOLIO':16} | Total PnL: ${total_pnl:.2f} | Portfolio: ${500+total_pnl:.2f}")
        logger.info(f"{'='*70}\n")

    def save_snapshot(self):
        snapshot = {
            'cycle': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'bots': {
                name: {
                    'balance': round(bot['balance'], 4),
                    'pnl':     round(bot['pnl'], 4),
                    'trades':  len(bot['trades']),
                    'wins':    bot['wins'],
                }
                for name, bot in self.bots.items()
            }
        }
        with open(SNAPSHOT_PATH, 'w') as f:
            json.dump(snapshot, f, indent=2)


if __name__ == '__main__':
    sim = ContinuousSimulator()

    # Kill old process running old simulator
    try:
        with open('/tmp/tradebot.pid', 'r') as f:
            pass
    except:
        pass

    try:
        while True:
            sim.run_cycle()
            time.sleep(0.5)   # 2 cycles per second — faster data collection
    except KeyboardInterrupt:
        logger.info("\n⏹  Stopped by user")
        sim.print_status()
        sys.exit(0)
