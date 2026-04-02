#!/usr/bin/env python3
"""
Blofin LIVE Paper Trading Simulator - v5 (Rebuilt from Research)

All 5 strategies fixed based on deep quant research:

MOMENTUM:    Aggregates 5s ticks into 5-min candles, EMA20/50 CROSSOVER EVENT
MEAN_REV:    Pulls 1H candles, Fisher RSI + Bollinger Bands + volume spike
GRID:        Real fixed-level grid bot — buys/sells at price grid levels
SCALP:       TP raised from 0.12% → 0.45%, SL from 0.08% → 0.15% (fee ratio fixed)
SWING:       Pulls 4H candles from Blofin OHLCV, polls every 15 minutes

Real data: Blofin public API (no auth, US-accessible)
"""

import json, time, logging, requests
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
BLOFIN_TICKERS = 'https://openapi.blofin.com/api/v1/market/tickers'
BLOFIN_CANDLES  = 'https://openapi.blofin.com/api/v1/market/candles'
PAIRS           = ['BTC-USDT', 'ETH-USDT']
ROUNDTRIP_COST  = 0.0011   # 0.04% taker × 2 + 0.03% slippage


# ── HELPERS ──────────────────────────────────────────────────────────────────

def compute_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0
    arr = np.array(closes[-(period+1):])
    deltas = np.diff(arr)
    gains  = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    ag = gains.mean(); al = losses.mean()
    return round(100 - 100 / (1 + ag / al), 1) if al > 0 else 100.0

def fisher_rsi(rsi_val):
    """Inverse Fisher Transform — amplifies extremes, compresses noise."""
    v = 0.1 * (rsi_val - 50)
    v = max(min(v, 0.999), -0.999)
    f = (np.exp(2*v) - 1) / (np.exp(2*v) + 1)
    return 50 * (f + 1)   # normalized 0-100

def ema_update(prev, price, period):
    k = 2.0 / (period + 1)
    return price * k + prev * (1 - k)

def fetch_tickers():
    try:
        r = requests.get(BLOFIN_TICKERS, timeout=5)
        if r.status_code != 200: return None
        out = {}
        for t in r.json().get('data', []):
            if t['instId'] in PAIRS:
                out[t['instId']] = {
                    'price':  float(t['last']),
                    'volume': float(t['volCurrency24h']),
                    'high24': float(t['high24h']),
                    'low24':  float(t['low24h']),
                }
        return out if len(out) == 2 else None
    except: return None

def fetch_candles(pair, bar='1H', limit=100):
    """Fetch OHLCV candles from Blofin. Returns list of dicts oldest→newest."""
    try:
        r = requests.get(BLOFIN_CANDLES,
                         params={'instId': pair, 'bar': bar, 'limit': limit},
                         timeout=8)
        if r.status_code != 200: return []
        raw = r.json().get('data', [])
        # Blofin returns newest first, only confirmed candles
        candles = []
        for row in reversed(raw):
            if row[8] == '1':   # confirmed candle only
                candles.append({
                    'ts':     int(row[0]),
                    'open':   float(row[1]),
                    'high':   float(row[2]),
                    'low':    float(row[3]),
                    'close':  float(row[4]),
                    'volume': float(row[5]),
                })
        return candles
    except: return []


class LiveSimulator:
    def __init__(self):
        self.bots = {
            'momentum':       self._new_bot(),
            'mean_reversion': self._new_bot(),
            'grid':           self._new_bot(),
            'scalp':          self._new_bot(),
            'swing':          self._new_bot(),
        }

        # Tick price history for scalp
        self.tick_prices  = {p: deque(maxlen=200) for p in PAIRS}
        self.tick_volumes = {p: deque(maxlen=200) for p in PAIRS}

        # 5-min candle accumulators for momentum
        self.candle_buf  = {p: [] for p in PAIRS}
        self.candle_5m   = {p: deque(maxlen=200) for p in PAIRS}
        self.candle_5m_ts = {p: None for p in PAIRS}

        # EMA state for momentum (on 5-min candles)
        self.mom_ema = {p: {'e20': None, 'e50': None,
                            'prev_e20': None, 'prev_e50': None} for p in PAIRS}

        # 1H and 4H candles fetched periodically
        self.candles_1h  = {p: [] for p in PAIRS}
        self.candles_4h  = {p: [] for p in PAIRS}
        self.last_1h_fetch = 0
        self.last_4h_fetch = 0

        # Grid state
        self.grid_levels = {p: [] for p in PAIRS}
        self.grid_center = {p: None for p in PAIRS}

        self.cycle = 0
        self.last_snapshot = time.time()
        self.errors = 0

        log.info("=" * 70)
        log.info("TradeBot v5 — Rebuilt from Quant Research")
        log.info("All 5 strategies fixed. Live Blofin data feed.")
        log.info("=" * 70)

        # Bootstrap candles
        self._refresh_candles()
        # Bootstrap prices
        data = fetch_tickers()
        if data:
            for p in PAIRS:
                self.tick_prices[p].append(data[p]['price'])
                log.info(f"  {p}: ${data[p]['price']:,.2f}")
        log.info("=" * 70)

    def _new_bot(self):
        return {'balance': 100.0, 'pnl': 0.0, 'wins': 0,
                'trades': [], 'position': None}

    # ── CANDLE REFRESH ────────────────────────────────────────────────────────

    def _refresh_candles(self):
        now = time.time()
        # Refresh 1H every 5 minutes
        if now - self.last_1h_fetch > 300:
            for p in PAIRS:
                c = fetch_candles(p, '1H', 100)
                if c: self.candles_1h[p] = c
            self.last_1h_fetch = now

        # Refresh 4H every 15 minutes
        if now - self.last_4h_fetch > 900:
            for p in PAIRS:
                c = fetch_candles(p, '4H', 100)
                if c: self.candles_4h[p] = c
            self.last_4h_fetch = now

    # ── 5-MIN CANDLE AGGREGATOR ───────────────────────────────────────────────

    def _add_tick_to_5m(self, pair, price, volume):
        """Aggregate 5s ticks into 5-min candles for momentum strategy."""
        now = int(time.time())
        bucket = (now // 300) * 300   # 5-min bucket

        if self.candle_5m_ts[pair] is None:
            self.candle_5m_ts[pair] = bucket

        if bucket != self.candle_5m_ts[pair]:
            # Close current candle
            if self.candle_buf[pair]:
                prices = [x[0] for x in self.candle_buf[pair]]
                vols   = [x[1] for x in self.candle_buf[pair]]
                candle = {
                    'ts': self.candle_5m_ts[pair],
                    'open': prices[0], 'high': max(prices),
                    'low': min(prices), 'close': prices[-1],
                    'volume': sum(vols),
                }
                self.candle_5m[pair].append(candle)
                self._update_mom_ema(pair, candle['close'])
                self.candle_buf[pair] = []
            self.candle_5m_ts[pair] = bucket

        self.candle_buf[pair].append((price, volume))

    def _update_mom_ema(self, pair, close):
        s = self.mom_ema[pair]
        s['prev_e20'] = s['e20']
        s['prev_e50'] = s['e50']
        if s['e20'] is None:
            s['e20'] = close; s['e50'] = close
        else:
            s['e20'] = ema_update(s['e20'], close, 20)
            s['e50'] = ema_update(s['e50'], close, 50)

    # ── POSITION MANAGEMENT ───────────────────────────────────────────────────

    def open_pos(self, bot_name, pair, price, pct):
        bot = self.bots[bot_name]
        if bot['position']: return False
        alloc = min(100.0 * pct, bot['balance'])
        if alloc < 1.0: return False
        fee   = alloc * (ROUNDTRIP_COST / 2)
        cost  = alloc - fee
        bot['balance'] -= alloc
        bot['position'] = {'pair': pair, 'entry': price,
                           'amount': cost / price, 'cost': cost, 'cycles': 0}
        return True

    def close_pos(self, bot_name, price):
        bot = self.bots[bot_name]
        pos = bot['position']
        if not pos: return None
        revenue = pos['amount'] * price
        fee     = revenue * (ROUNDTRIP_COST / 2)
        net     = revenue - fee
        pnl     = net - pos['cost']
        bot['balance'] += net
        bot['pnl']     += pnl
        if pnl > 0: bot['wins'] += 1
        bot['trades'].append({'pair': pos['pair'], 'entry': pos['entry'],
                              'exit': price, 'pnl': round(pnl, 6)})
        bot['position'] = None
        return pnl

    # ── STRATEGY 1: MOMENTUM (5-min candles, EMA20/50 crossover) ─────────────

    def run_momentum(self):
        for pair in PAIRS:
            candles = list(self.candle_5m[pair])
            if len(candles) < 60: continue  # warm-up

            s     = self.mom_ema[pair]
            bot   = self.bots['momentum']
            pos   = bot['position']
            price = candles[-1]['close']

            if s['e20'] is None or s['prev_e20'] is None: continue

            # Crossover events
            cross_up   = (s['prev_e20'] <= s['prev_e50']) and (s['e20'] > s['e50'])
            cross_down = (s['prev_e20'] >= s['prev_e50']) and (s['e20'] < s['e50'])

            # Volume filter (current 5m candle volume > 20-bar avg * 1.2)
            vols = [c['volume'] for c in candles[-20:]]
            vol_ok = candles[-1]['volume'] > (sum(vols)/len(vols)) * 1.2

            closes = [c['close'] for c in candles]
            rsi    = compute_rsi(closes, 14)

            if not pos and cross_up and vol_ok and 45 <= rsi <= 65 and bot['balance'] > 5:
                if self.open_pos('momentum', pair, price, 0.20):
                    log.info(f"  MOMENTUM  → {pair} ${price:,.2f} EMA cross↑ RSI:{rsi}")

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']
                if chg >= 0.03 or chg <= -0.03 or cross_down or rsi > 75:
                    pnl = self.close_pos('momentum', price)
                    tag = "✓TP" if chg >= 0.03 else ("✗SL" if chg <= -0.03 else "~EXIT")
                    log.info(f"  MOMENTUM  ← {pair} ${price:,.2f} {tag} PnL:${pnl:.5f}")

    # ── STRATEGY 2: MEAN REVERSION (1H candles, Fisher RSI + BB) ─────────────

    def run_mean_reversion(self):
        for pair in PAIRS:
            candles = self.candles_1h[pair]
            if len(candles) < 40: continue

            closes  = [c['close'] for c in candles]
            volumes = [c['volume'] for c in candles]
            price   = closes[-1]

            rsi  = compute_rsi(closes, 14)
            frsi = fisher_rsi(rsi)

            # Bollinger Bands (20, 2σ)
            ma20  = np.mean(closes[-20:])
            std20 = np.std(closes[-20:])
            bb_lower = ma20 - 2 * std20
            bb_upper = ma20 + 2 * std20
            sma40 = np.mean(closes[-40:])

            # Volume spike
            vol_ma = np.mean(volumes[-20:])
            vol_spike = volumes[-1] > vol_ma * 1.5

            bot = self.bots['mean_reversion']
            pos = bot['position']

            # Entry: Fisher RSI < 20 + below BB + volume spike + below SMA40
            if not pos and frsi < 20 and price <= bb_lower and vol_spike and price < sma40 and bot['balance'] > 5:
                if self.open_pos('mean_reversion', pair, price, 0.35):
                    log.info(f"  MEAN_REV  → {pair} ${price:,.2f} FisherRSI:{frsi:.1f} BB_lower:${bb_lower:,.2f}")

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']
                # Exit: Fisher RSI > 60 (mean restored) or TP or SL
                if frsi > 60 or price > ma20 or chg >= 0.015 or chg <= -0.010:
                    pnl = self.close_pos('mean_reversion', price)
                    log.info(f"  MEAN_REV  ← {pair} ${price:,.2f} FisherRSI:{frsi:.1f} PnL:${pnl:.5f}")

    # ── STRATEGY 3: GRID (Fixed-level, real oscillation captures) ────────────

    def _setup_grid(self, pair, center_price):
        """Place 10 grid levels ±2.5% around center price."""
        n      = 10
        rng    = 0.025  # ±2.5%
        step   = (center_price * rng * 2) / n
        self.grid_center[pair] = center_price
        self.grid_levels[pair] = [
            round(center_price - (center_price * rng) + i * step, 2)
            for i in range(n + 1)
        ]
        log.info(f"  GRID      ⚡ {pair} grid set: ${self.grid_levels[pair][0]:,.2f} – ${self.grid_levels[pair][-1]:,.2f}")

    def run_grid(self, ticker_data):
        for pair in PAIRS:
            if pair not in ticker_data: continue
            price = ticker_data[pair]['price']
            bot   = self.bots['grid']

            # Initialize grid if needed
            if not self.grid_levels[pair]:
                self._setup_grid(pair, price)
                continue

            center = self.grid_center[pair]

            # Recenter grid if price moved > 3% from center
            if abs(price - center) / center > 0.03:
                if bot['position']:
                    pnl = self.close_pos('grid', price)
                    if pnl is not None:
                        log.info(f"  GRID      ↺ Recentering {pair} PnL:${pnl:.5f}")
                self._setup_grid(pair, price)
                continue

            pos = bot['position']
            levels = self.grid_levels[pair]

            # Find which grid band we're in
            below = [l for l in levels if l < price]
            above = [l for l in levels if l > price]
            if not below or not above: continue

            nearest_below = below[-1]
            nearest_above = above[0]
            grid_width = nearest_above - nearest_below

            if not pos and bot['balance'] > 5:
                # Buy when price is in lower third of current grid band
                band_pct = (price - nearest_below) / grid_width
                if band_pct < 0.30:
                    if self.open_pos('grid', pair, price, 0.15):
                        pass   # silent

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']

                # Profit target = 1 grid level up (~0.5%)
                if chg >= 0.005:
                    pnl = self.close_pos('grid', price)
                    if pnl is not None:
                        log.info(f"  GRID      ← {pair} ${price:,.2f} ✓ +0.5% PnL:${pnl:.5f}")
                # Stop loss = -2 grid levels
                elif chg <= -0.010:
                    pnl = self.close_pos('grid', price)
                    if pnl is not None:
                        log.info(f"  GRID      ← {pair} ${price:,.2f} ✗ SL PnL:${pnl:.5f}")

    # ── STRATEGY 4: SCALP (Fixed TP/SL ratio — fee-aware) ────────────────────

    def run_scalp(self, ticker_data):
        for pair in PAIRS:
            if pair not in ticker_data: continue
            price  = ticker_data[pair]['price']
            self.tick_prices[pair].append(price)
            self.tick_volumes[pair].append(ticker_data[pair]['volume'])

            hist = list(self.tick_prices[pair])
            if len(hist) < 20: continue

            vols  = list(self.tick_volumes[pair])
            bot   = self.bots['scalp']
            pos   = bot['position']

            rsi   = compute_rsi(hist, 14)
            vol_avg = np.mean(vols[-20:])
            vol_ok  = vols[-1] > vol_avg * 1.5 if vol_avg > 0 else False

            # VWAP approximation (price * volume / volume sum over 20 ticks)
            vwap = np.average(hist[-20:], weights=vols[-20:]) if sum(vols[-20:]) > 0 else hist[-1]

            # Entry: RSI cross above 50 + volume spike + price above VWAP
            rsi_cross = len(hist) > 2 and compute_rsi(hist[:-1], 14) < 50 and rsi >= 50

            if not pos and rsi_cross and vol_ok and price > vwap and bot['balance'] > 2:
                if self.open_pos('scalp', pair, price, 0.25):
                    pass  # silent high-freq

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']

                # Fixed fee-aware TP/SL: 0.45% TP, 0.15% SL (3:1 R:R, fee = 24% of TP)
                if chg >= 0.0045 or chg <= -0.0015 or pos['cycles'] >= 240:
                    pnl = self.close_pos('scalp', price)
                    if pnl is not None and abs(pnl) > 0.0001:
                        tag = "✓" if pnl > 0 else "✗"
                        log.info(f"  SCALP     ← {pair} {tag} PnL:${pnl:.6f} ({chg*100:+.3f}%)")

    # ── STRATEGY 5: SWING (4H candles, proper trend confirmation) ────────────

    def run_swing(self):
        for pair in PAIRS:
            candles = self.candles_4h[pair]
            if len(candles) < 60: continue

            closes  = [c['close'] for c in candles]
            volumes = [c['volume'] for c in candles]
            price   = closes[-1]

            # EMA20 and EMA50 on 4H candles
            ema20 = ema20_prev = closes[-1]
            ema50 = ema50_prev = closes[-1]
            for i, c in enumerate(closes):
                ema20_prev = ema20
                ema50_prev = ema50
                ema20 = ema_update(ema20, c, 20)
                ema50 = ema_update(ema50, c, 50)

            rsi       = compute_rsi(closes, 14)
            vol_avg   = np.mean(volumes[-20:])
            vol_ok    = volumes[-1] >= vol_avg * 0.8  # swing doesn't need huge spike

            trend_up  = ema20 > ema50
            trend_down = ema20 < ema50

            bot = self.bots['swing']
            pos = bot['position']

            if not pos and trend_up and 45 <= rsi <= 68 and vol_ok and bot['balance'] > 5:
                if self.open_pos('swing', pair, price, 0.40):
                    log.info(f"  SWING     → {pair} ${price:,.2f} 4H EMA20:{ema20:,.0f} EMA50:{ema50:,.0f} RSI:{rsi}")

            elif pos and pos['pair'] == pair:
                pos['cycles'] += 1
                chg = (price - pos['entry']) / pos['entry']
                if chg >= 0.04:
                    pnl = self.close_pos('swing', price)
                    log.info(f"  SWING     ← {pair} ✓TP ${price:,.2f} +{chg*100:.2f}% PnL:${pnl:.4f}")
                elif chg <= -0.02 or trend_down:
                    pnl = self.close_pos('swing', price)
                    log.info(f"  SWING     ← {pair} ✗SL ${price:,.2f} {chg*100:.2f}% PnL:${pnl:.4f}")

    # ── MAIN LOOP ─────────────────────────────────────────────────────────────

    def run_cycle(self):
        self.cycle += 1

        # Refresh higher-timeframe candles
        self._refresh_candles()

        # Fetch live ticker
        data = fetch_tickers()
        if data:
            self.errors = 0
            # Feed ticks into 5-min aggregator for momentum
            for p in PAIRS:
                self.tick_prices[p].append(data[p]['price'])
                self._add_tick_to_5m(p, data[p]['price'], data[p]['volume'])

            self.run_scalp(data)
            self.run_grid(data)
        else:
            self.errors += 1
            if self.errors % 10 == 0:
                log.warning(f"  ⚠️  {self.errors} consecutive API failures")

        # Candle-based strategies (use latest candle data, run every cycle but only act on new candles)
        self.run_momentum()
        self.run_mean_reversion()
        self.run_swing()

        # Snapshot every 10 cycles (~50 seconds) for live hub updates
        now = time.time()
        if self.cycle % 10 == 0 or now - self.last_snapshot > 60:
            self.save_snapshot()
            if self.cycle % 50 == 0:  # Print status every 50 cycles
                self.print_status()
            self.last_snapshot = now

    def print_status(self):
        prices = {p: list(self.tick_prices[p])[-1] if self.tick_prices[p] else 0 for p in PAIRS}
        log.info(f"\n{'─'*70}")
        log.info(f"  Cycle {self.cycle:,} | {datetime.now().strftime('%H:%M:%S')} | "
                 f"BTC:${prices['BTC-USDT']:,.2f} ETH:${prices['ETH-USDT']:,.2f}")
        log.info(f"{'─'*70}")
        total_pnl = total_t = total_w = 0
        for name, bot in self.bots.items():
            t = len(bot['trades']); w = bot['wins']
            wr  = f"{w/t*100:.1f}%" if t > 0 else "—"
            pnl = bot['pnl']
            pos = f"OPEN@${bot['position']['entry']:,.2f}" if bot['position'] else "flat"
            total_pnl += pnl; total_t += t; total_w += w
            log.info(f"  {name.upper():16} | T:{t:3} W:{w:3} WR:{wr:6} | PnL:${pnl:9.5f} | {pos}")
        twr = f"{total_w/total_t*100:.1f}%" if total_t else "—"
        log.info(f"  {'TOTAL':16} | T:{total_t:3} W:{total_w:3} WR:{twr:6} | "
                 f"PnL:${total_pnl:9.5f} | ${500+total_pnl:.4f}")
        log.info(f"{'─'*70}\n")

    def save_snapshot(self):
        prices = {p: list(self.tick_prices[p])[-1] if self.tick_prices[p] else None for p in PAIRS}
        snap = {
            'cycle': self.cycle,
            'timestamp': datetime.now().isoformat(),
            'prices': {'BTC': prices['BTC-USDT'], 'ETH': prices['ETH-USDT']},
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
            time.sleep(5)
    except KeyboardInterrupt:
        log.info("\n⏹  Stopped.")
        sim.print_status()
        sys.exit(0)
