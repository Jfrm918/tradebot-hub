#!/usr/bin/env python3
"""
Blofin LIVE Paper Trading Simulator - Production Grade v4
Real-time market data from Blofin public API (no auth required)
All 5 strategies trade on ACTUAL BTC/ETH prices
"""

import json
import time
import logging
import requests
from datetime import datetime
from collections import deque
import numpy as np
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/Users/jfrm918/.openclaw/workspace/trading_bots/simulator.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('TradeBot')

SNAPSHOT_PATH = '/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json'
BLOFIN_API    = 'https://openapi.blofin.com/api/v1/market/tickers'
PAIRS         = ['BTC-USDT', 'ETH-USDT']

# Transaction cost: 0.04% taker × 2 + 0.03% slippage = 0.11% roundtrip
ROUNDTRIP_COST = 0.0011

STRATEGY_CONFIG = {
    'momentum': {
        'ema_fast': 9, 'ema_slow': 21,
        'rsi_entry': 55, 'rsi_exit': 78,
        'stop_pct': 0.005, 'tp_pct': 0.015,
        'size_pct': 0.40,
    },
    'mean_reversion': {
        'rsi_period': 14,
        'rsi_oversold': 25, 'rsi_overbought': 75,
        'exit_rsi': 50,
        'stop_pct': 0.015, 'tp_pct': 0.008,
        'size_pct': 0.40,
    },
    'grid': {
        'spacing_pct': 0.005,
        'stop_pct': 0.025, 'tp_pct': 0.005,
        'size_pct': 0.20,
    },
    'scalp': {
        'rsi_period': 7,
        'tp_pct': 0.0012, 'stop_pct': 0.0008,
        'max_hold': 120,
        'size_pct': 0.30,
    },
    'swing': {
        'ema_fast': 20, 'ema_slow': 50,
        'tp_pct': 0.040, 'stop_pct': 0.020,
        'size_pct': 0.45,
    },
}


class LiveSimulator:
    def __init__(self):
        self.bots = {
            'momentum':       self._new_bot(),
            'mean_reversion': self._new_bot(),
            'grid':           self._new_bot(),
            'scalp':          self._new_bot(),
            'swing':          self._new_bot(),
        }

        # Price history (600 ticks)
        self.prices = {p: deque(maxlen=600) for p in PAIRS}
        self.ema    = {p: {} for p in PAIRS}
        self.cycle  = 0
        self.errors = 0

        # Pre-fill price history with bootstrap fetch
        log.info("=" * 70)
        log.info("TradeBot v4 — LIVE Blofin Data Feed")
        log.info("Bootstrapping price history...")
        self._bootstrap()
        log.info(f"BTC: ${list(self.prices['BTC-USDT'])[-1]:,.2f}")
        log.info(f"ETH: ${list(self.prices['ETH-USDT'])[-1]:,.2f}")
        log.info(f"Capital: $100 × 5 = $500 | Cost: {ROUNDTRIP_COST*100:.2f}%/trade")
        log.info("=" * 70)

    def _new_bot(self):
        return {
            'balance': 100.0, 'pnl': 0.0,
            'wins': 0, 'trades': [], 'position': None,
        }

    # ── LIVE PRICE FEED ───────────────────────────────────────────────────────

    def _bootstrap(self):
        """Fetch initial prices and seed history + EMAs"""
        try:
            data = self._fetch_prices()
            if data:
                for pair in PAIRS:
                    p = data.get(pair)
                    if p:
                        # Seed 600 ticks with current price (EMAs warm up fast)
                        for _ in range(600):
                            self.prices[pair].append(p)
                        for period in [7, 9, 14, 20, 21, 50]:
                            self.ema[pair][period] = p
        except Exception as e:
            log.error(f"Bootstrap failed: {e}")

    def _fetch_prices(self):
        """Fetch live ticker prices from Blofin public API"""
        try:
            r = requests.get(BLOFIN_API, timeout=5)
            if r.status_code != 200:
                return None
            tickers = r.json().get('data', [])
            result = {}
            for t in tickers:
                if t['instId'] in PAIRS:
                    result[t['instId']] = float(t['last'])
            return result
        except Exception:
            return None

    def update_prices(self):
        """Pull fresh prices from Blofin, return True if successful"""
        data = self._fetch_prices()
        if not data:
            self.errors += 1
            # Fall back to last known price with tiny GBM noise
            for pair in PAIRS:
                if self.prices[pair]:
                    last = list(self.prices[pair])[-1]
                    noise = last * np.random.normal(0, 0.00003)
                    self.prices[pair].append(round(last + noise, 2))
            return False

        self.errors = 0
        for pair in PAIRS:
            if pair in data:
                self.prices[pair].append(data[pair])
        return True

    # ── INDICATORS ────────────────────────────────────────────────────────────

    def update_emas(self):
        for pair in PAIRS:
            if not self.prices[pair]:
                continue
            price = list(self.prices[pair])[-1]
            for period in self.ema.get(pair, {}):
                k = 2.0 / (period + 1)
                self.ema[pair][period] = price * k + self.ema[pair][period] * (1 - k)

    def rsi(self, pair, period=14):
        hist = list(self.prices[pair])
        if len(hist) < period + 1:
            return 50.0
        deltas = np.diff(hist[-(period+1):])
        gains  = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        ag = gains.mean(); al = losses.mean()
        return round(100 - 100 / (1 + ag / al), 1) if al > 0 else 100.0

    def current_price(self, pair):
        return list(self.prices[pair])[-1] if self.prices[pair] else None

    # ── POSITION MANAGEMENT ───────────────────────────────────────────────────

    def open_pos(self, bot_name, pair, price, pct):
        bot = self.bots[bot_name]
        if bot['position']:
            return False
        alloc = min(100.0 * pct, bot['balance'])
        if alloc < 1.0:
            return False
        fee   = alloc * (ROUNDTRIP_COST / 2)
        cost  = alloc - fee
        bot['balance'] -= alloc
        bot['position'] = {
            'pair': pair, 'entry': price,
            'amount': cost / price, 'cost': cost,
            'cycles': 0,
        }
        return True

    def close_pos(self, bot_name, price):
        bot = self.bots[bot_name]
        pos = bot['position']
        if not pos:
            return None
        revenue   = pos['amount'] * price
        fee       = revenue * (ROUNDTRIP_COST / 2)
        net       = revenue - fee
        pnl       = net - pos['cost']
        bot['balance'] += net
        bot['pnl']     += pnl
        if pnl > 0:
            bot['wins'] += 1
        bot['trades'].append({
            'pair': pos['pair'], 'entry': pos['entry'], 'exit': price,
            'pnl': round(pnl, 6), 'pct': round((price-pos['entry'])/pos['entry']*100, 3),
        })
        bot['position'] = None
        return pnl

    # ── STRATEGIES ────────────────────────────────────────────────────────────

    def run_momentum(self):
        c = STRATEGY_CONFIG['momentum']
        for pair in PAIRS:
            price = self.current_price(pair)
            if not price: continue
            e9, e21 = self.ema[pair].get(9, price), self.ema[pair].get(21, price)
            rsi     = self.rsi(pair, 14)
            bot     = self.bots['momentum']
            pos     = bot['position']

            if not pos and e9 > e21 * 1.0005 and rsi > c['rsi_entry'] and bot['balance'] > 5:
                if self.open_pos('momentum', pair, price, c['size_pct']):
                    log.info(f"  MOMENTUM  → {pair} ${price:,.2f} | EMA9:{e9:,.0f} EMA21:{e21:,.0f} RSI:{rsi}")

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']
                if chg >= c['tp_pct'] or chg <= -c['stop_pct'] or e9 < e21 or rsi > c['rsi_exit']:
                    pnl = self.close_pos('momentum', price)
                    tag = "✓TP" if chg >= c['tp_pct'] else ("✗SL" if chg <= -c['stop_pct'] else "~EXIT")
                    log.info(f"  MOMENTUM  ← {pair} ${price:,.2f} {tag} PnL:${pnl:.5f} ({chg*100:+.3f}%)")

    def run_mean_reversion(self):
        c = STRATEGY_CONFIG['mean_reversion']
        for pair in PAIRS:
            price = self.current_price(pair)
            if not price: continue
            rsi = self.rsi(pair, c['rsi_period'])
            bot = self.bots['mean_reversion']
            pos = bot['position']

            if not pos and rsi < c['rsi_oversold'] and bot['balance'] > 5:
                if self.open_pos('mean_reversion', pair, price, c['size_pct']):
                    log.info(f"  MEAN_REV  → {pair} ${price:,.2f} | RSI:{rsi} (oversold)")

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg     = (price - pos['entry']) / pos['entry']
                rsi_now = self.rsi(pair, c['rsi_period'])
                if rsi_now >= c['exit_rsi'] or chg >= c['tp_pct'] or chg <= -c['stop_pct']:
                    pnl = self.close_pos('mean_reversion', price)
                    log.info(f"  MEAN_REV  ← {pair} ${price:,.2f} PnL:${pnl:.5f} RSI:{rsi_now}")

    def run_grid(self):
        c = STRATEGY_CONFIG['grid']
        for pair in PAIRS:
            price = self.current_price(pair)
            if not price: continue
            e20 = self.ema[pair].get(20, price)
            bot = self.bots['grid']
            pos = bot['position']

            below = price < e20 * (1 - c['spacing_pct'])
            above = price > e20 * (1 + c['spacing_pct'])

            if not pos and below and bot['balance'] > 5:
                self.open_pos('grid', pair, price, c['size_pct'])

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']
                if chg >= c['tp_pct'] or above:
                    pnl = self.close_pos('grid', price)
                    if pnl is not None:
                        log.info(f"  GRID      ← {pair} ${price:,.2f} PnL:${pnl:.5f} {'✓' if pnl>0 else '✗'}")
                elif chg <= -c['stop_pct']:
                    pnl = self.close_pos('grid', price)
                    if pnl is not None:
                        log.info(f"  GRID      ← STOP {pair} ${price:,.2f} PnL:${pnl:.5f}")

    def run_scalp(self):
        c = STRATEGY_CONFIG['scalp']
        for pair in PAIRS:
            price = self.current_price(pair)
            if not price: continue
            hist = list(self.prices[pair])
            if len(hist) < 5: continue
            rsi  = self.rsi(pair, c['rsi_period'])
            bot  = self.bots['scalp']
            pos  = bot['position']

            micro_up = hist[-1] > hist[-2] > hist[-3]

            if not pos and micro_up and 30 < rsi < 62 and bot['balance'] > 2:
                self.open_pos('scalp', pair, price, c['size_pct'])

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']
                if chg >= c['tp_pct'] or chg <= -c['stop_pct'] or pos['cycles'] >= c['max_hold']:
                    pnl = self.close_pos('scalp', price)
                    if pnl is not None and abs(pnl) > 0.0005:
                        log.info(f"  SCALP     ← {pair} {'✓' if pnl>0 else '✗'} PnL:${pnl:.6f} ({chg*100:+.4f}%)")

    def run_swing(self):
        c = STRATEGY_CONFIG['swing']
        for pair in PAIRS:
            price = self.current_price(pair)
            if not price: continue
            e20 = self.ema[pair].get(20, price)
            e50 = self.ema[pair].get(50, price)
            rsi = self.rsi(pair, 14)
            bot = self.bots['swing']
            pos = bot['position']

            trend_up = e20 > e50 * 1.001 and rsi > 45

            if not pos and trend_up and bot['balance'] > 5:
                if self.open_pos('swing', pair, price, c['size_pct']):
                    log.info(f"  SWING     → {pair} ${price:,.2f} | EMA20:{e20:,.0f} EMA50:{e50:,.0f}")

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']
                if chg >= c['tp_pct']:
                    pnl = self.close_pos('swing', price)
                    log.info(f"  SWING     ← {pair} ✓TP ${price:,.2f} PnL:${pnl:.4f} (+{chg*100:.2f}%)")
                elif chg <= -c['stop_pct'] or e20 < e50:
                    pnl = self.close_pos('swing', price)
                    log.info(f"  SWING     ← {pair} ✗SL ${price:,.2f} PnL:${pnl:.4f} ({chg*100:.2f}%)")

    # ── MAIN LOOP ─────────────────────────────────────────────────────────────

    def run_cycle(self):
        self.cycle += 1
        live = self.update_prices()
        self.update_emas()

        if live:
            self.run_momentum()
            self.run_mean_reversion()
            self.run_grid()
            self.run_scalp()
            self.run_swing()

        if self.cycle % 200 == 0:
            self.print_status()
            self.save_snapshot()

        if self.cycle % 20 == 0 and not live:
            log.warning(f"  ⚠️  API errors: {self.errors} consecutive — using fallback prices")

    def print_status(self):
        btc = self.current_price('BTC-USDT')
        eth = self.current_price('ETH-USDT')
        log.info(f"\n{'─'*70}")
        log.info(f"  Cycle {self.cycle:,} | {datetime.now().strftime('%H:%M:%S')} | BTC:${btc:,.2f} ETH:${eth:,.2f}")
        log.info(f"{'─'*70}")
        total_pnl = total_t = total_w = 0
        for name, bot in self.bots.items():
            t = len(bot['trades']); w = bot['wins']
            wr = f"{w/t*100:.1f}%" if t > 0 else "—"
            pnl = bot['pnl']
            pos = f"OPEN@${bot['position']['entry']:,.2f}" if bot['position'] else "flat"
            total_pnl += pnl; total_t += t; total_w += w
            log.info(f"  {name.upper():16} | T:{t:3} W:{w:3} WR:{wr:6} | PnL:${pnl:9.5f} | {pos}")
        total_wr = f"{total_w/total_t*100:.1f}%" if total_t else "—"
        log.info(f"  {'TOTAL':16} | T:{total_t:3} W:{total_w:3} WR:{total_wr:6} | PnL:${total_pnl:9.5f} | ${500+total_pnl:.4f}")
        log.info(f"{'─'*70}\n")

    def save_snapshot(self):
        snap = {
            'cycle': self.cycle,
            'timestamp': datetime.now().isoformat(),
            'prices': {
                'BTC': self.current_price('BTC-USDT'),
                'ETH': self.current_price('ETH-USDT'),
            },
            'bots': {
                name: {
                    'balance': round(bot['balance'], 6),
                    'pnl':     round(bot['pnl'], 6),
                    'trades':  len(bot['trades']),
                    'wins':    bot['wins'],
                }
                for name, bot in self.bots.items()
            }
        }
        with open(SNAPSHOT_PATH, 'w') as f:
            json.dump(snap, f, indent=2)


if __name__ == '__main__':
    sim = LiveSimulator()
    try:
        while True:
            sim.run_cycle()
            time.sleep(5)   # Poll Blofin every 5 seconds (respectful rate limiting)
    except KeyboardInterrupt:
        log.info("\n⏹  Stopped.")
        sim.print_status()
        sys.exit(0)
