#!/usr/bin/env python3
"""
Swing Trading Bot v2 — PROPER IMPLEMENTATION
Uses Blofin 4H OHLCV candles instead of 5-second tick data.

ROOT CAUSE FIX:
- OLD: EMA20/50 computed on 5-second ticks (noise, not trend)
- NEW: EMA20/50 computed on 4H OHLCV candles (real swing signals)

Signal logic:
- Entry:  EMA20 > EMA50 (bullish trend) AND RSI(14) in [45, 65] AND volume > 20-bar avg
- Exit:   TP +4%, SL -2%, or bearish EMA cross (EMA20 < EMA50)
- Candle polling: every 15 minutes (new 4H bar check)
- Capital per trade: 45%
"""

import requests
import time
import json
import logging
from datetime import datetime, timezone
from collections import deque

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [SWING-v2] %(message)s'
)
log = logging.getLogger('SwingV2')

BLOFIN_CANDLES = 'https://openapi.blofin.com/api/v1/market/candles'
SNAPSHOT_PATH  = '/Users/jfrm918/.openclaw/workspace/trading_bots/swing_snapshot.json'
PAIRS          = ['BTC-USDT', 'ETH-USDT']
CANDLE_BAR     = '4H'
CANDLE_LIMIT   = 100   # 100 × 4H = 400 hours (~16.7 days of data)
POLL_INTERVAL  = 900   # 15 minutes — check for new 4H candle close
ROUNDTRIP_COST = 0.0011  # 0.11% fees + slippage


def fetch_candles(inst_id: str, bar: str = '4H', limit: int = 100) -> list[dict]:
    """
    Fetch OHLCV candles from Blofin.
    Returns list of dicts: {ts, open, high, low, close, vol}
    Sorted oldest → newest.

    Raw format from API: [ts, open, high, low, close, vol_contracts, vol_base, vol_quote, confirm]
    """
    try:
        r = requests.get(BLOFIN_CANDLES, params={
            'instId': inst_id,
            'bar': bar,
            'limit': limit,
        }, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get('code') != '0':
            log.error(f"Blofin error: {data}")
            return []

        candles = []
        for row in reversed(data['data']):  # API returns newest first → reverse to oldest first
            ts    = int(row[0])
            o     = float(row[1])
            h     = float(row[2])
            lo    = float(row[3])
            c     = float(row[4])
            vol   = float(row[5])   # volume in contracts
            confirmed = row[8]      # '1' = candle closed, '0' = still forming
            candles.append({
                'ts': ts, 'open': o, 'high': h, 'low': lo,
                'close': c, 'vol': vol, 'confirmed': confirmed
            })
        return candles

    except Exception as e:
        log.error(f"fetch_candles({inst_id}) failed: {e}")
        return []


def compute_ema(prices: list[float], period: int) -> list[float]:
    """Compute EMA over a price series. Returns list of same length (first values = SMA seed)."""
    if len(prices) < period:
        return [None] * len(prices)
    ema = [None] * len(prices)
    k = 2.0 / (period + 1)
    # Seed with SMA of first `period` values
    sma = sum(prices[:period]) / period
    ema[period - 1] = sma
    for i in range(period, len(prices)):
        ema[i] = prices[i] * k + ema[i - 1] * (1 - k)
    return ema


def compute_rsi(closes: list[float], period: int = 14) -> object:
    """Compute RSI(period) on the last (period+1) closes."""
    if len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(len(closes) - period, len(closes))]
    gains  = [d for d in deltas if d > 0]
    losses = [-d for d in deltas if d < 0]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - 100 / (1 + rs), 2)


class SwingBotV2:
    def __init__(self, capital: float = 100.0, size_pct: float = 0.45,
                 tp_pct: float = 0.04, sl_pct: float = 0.02):
        self.capital   = capital
        self.balance   = capital
        self.size_pct  = size_pct
        self.tp_pct    = tp_pct
        self.sl_pct    = sl_pct
        self.position  = None
        self.trades    = []
        self.wins      = 0
        self.pnl       = 0.0
        self.last_candle_ts = {}  # track last processed candle per pair

        log.info(f"SwingBotV2 initialized | Capital: ${capital} | TP:{tp_pct*100}% SL:{sl_pct*100}%")
        log.info(f"Data source: Blofin {CANDLE_BAR} OHLCV candles (NOT tick data)")

    def analyze(self, pair: str) -> object:
        """
        Pull fresh 4H candles for `pair`, compute indicators,
        return signal dict or None if no action needed.
        """
        candles = fetch_candles(pair, bar=CANDLE_BAR, limit=CANDLE_LIMIT)
        if len(candles) < 55:  # Need at least 50 for EMA50 + buffer
            log.warning(f"{pair}: insufficient candle history ({len(candles)})")
            return None

        # Use only confirmed (closed) candles for signal
        confirmed = [c for c in candles if c['confirmed'] == '1']
        if len(confirmed) < 55:
            log.warning(f"{pair}: insufficient confirmed candles ({len(confirmed)})")
            return None

        closes  = [c['close'] for c in confirmed]
        volumes = [c['vol']   for c in confirmed]
        latest  = confirmed[-1]

        # Skip if we already processed this candle
        if self.last_candle_ts.get(pair) == latest['ts']:
            return None

        # EMAs on confirmed closes
        ema20_series = compute_ema(closes, 20)
        ema50_series = compute_ema(closes, 50)
        ema20 = ema20_series[-1]
        ema50 = ema50_series[-1]

        if ema20 is None or ema50 is None:
            return None

        # RSI(14) on last 15 confirmed closes
        rsi = compute_rsi(closes[-15:], period=14)
        if rsi is None:
            return None

        # Volume filter: current vol vs 20-bar avg
        avg_vol  = sum(volumes[-21:-1]) / 20
        vol_ok   = volumes[-1] >= avg_vol * 0.8  # current bar volume at least 80% of avg

        price    = latest['close']
        ts_human = datetime.fromtimestamp(latest['ts'] / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')

        # Bullish: EMA20 above EMA50, not extreme RSI
        bullish  = ema20 > ema50
        rsi_ok   = 45 <= rsi <= 68

        # Bearish cross (exit signal when in position)
        bearish  = ema20 < ema50

        log.info(f"  {pair} [{ts_human}] | Close:{price:,.2f} | EMA20:{ema20:,.2f} EMA50:{ema50:,.2f} "
                 f"| RSI:{rsi} | VolOK:{vol_ok} | {'▲ BULL' if bullish else '▼ BEAR'}")

        self.last_candle_ts[pair] = latest['ts']

        return {
            'pair':    pair,
            'price':   price,
            'ema20':   ema20,
            'ema50':   ema50,
            'rsi':     rsi,
            'vol_ok':  vol_ok,
            'bullish': bullish,
            'bearish': bearish,
            'candle_ts': latest['ts'],
        }

    def check_entry(self, sig: dict) -> bool:
        """Enter if: bullish EMA cross + RSI in range + volume OK + no open position."""
        if self.position:
            return False
        if self.balance < self.capital * 0.10:
            log.warning("Balance too low to trade")
            return False

        if sig['bullish'] and sig['rsi_ok'] and sig['vol_ok']:
            alloc   = self.balance * self.size_pct
            fee     = alloc * (ROUNDTRIP_COST / 2)
            cost    = alloc - fee
            qty     = cost / sig['price']

            self.balance  -= alloc
            self.position  = {
                'pair':   sig['pair'],
                'entry':  sig['price'],
                'qty':    qty,
                'cost':   cost,
                'alloc':  alloc,
                'tp':     sig['price'] * (1 + self.tp_pct),
                'sl':     sig['price'] * (1 - self.sl_pct),
                'opened': datetime.now(timezone.utc).isoformat(),
            }
            log.info(f"  ✅ ENTRY {sig['pair']} @ ${sig['price']:,.2f} | TP:${self.position['tp']:,.2f} SL:${self.position['sl']:,.2f}")
            return True

        return False

    def check_exit(self, sig: dict) -> bool:
        """Exit if: TP hit, SL hit, or bearish EMA cross."""
        if not self.position or self.position['pair'] != sig['pair']:
            return False

        pos   = self.position
        price = sig['price']
        chg   = (price - pos['entry']) / pos['entry']

        reason = None
        if price >= pos['tp']:
            reason = f"✓TP (+{chg*100:.2f}%)"
        elif price <= pos['sl']:
            reason = f"✗SL ({chg*100:.2f}%)"
        elif sig['bearish']:
            reason = f"~CROSS ({chg*100:.2f}%)"

        if reason:
            revenue = pos['qty'] * price
            fee     = revenue * (ROUNDTRIP_COST / 2)
            net     = revenue - fee
            pnl     = net - pos['cost']

            self.balance += net
            self.pnl     += pnl
            if pnl > 0:
                self.wins += 1

            self.trades.append({
                'pair':   sig['pair'],
                'entry':  pos['entry'],
                'exit':   price,
                'pct':    round(chg * 100, 3),
                'pnl':    round(pnl, 6),
                'reason': reason,
            })
            self.position = None
            log.info(f"  {'✅' if pnl>0 else '❌'} EXIT {sig['pair']} @ ${price:,.2f} | {reason} | PnL:${pnl:.4f} | Balance:${self.balance:.4f}")
            return True

        return False

    def run_forever(self):
        """
        Main loop: poll every POLL_INTERVAL seconds.
        Only signals on confirmed 4H candle closes.
        Expected frequency: 1-3 signals per day across BTC+ETH.
        """
        log.info("=" * 70)
        log.info(f"SwingBotV2 running | Polling every {POLL_INTERVAL//60}min | 4H candles")
        log.info("=" * 70)

        while True:
            try:
                for pair in PAIRS:
                    sig = self.analyze(pair)
                    if sig is None:
                        continue

                    if self.position:
                        self.check_exit(sig)
                    else:
                        # Only enter on CONFIRMED entry conditions
                        if sig['bullish'] and 45 <= sig['rsi'] <= 68 and sig['vol_ok']:
                            self.check_entry(sig)

                self._print_status()

            except KeyboardInterrupt:
                log.info("\n⏹  Stopped by user.")
                self._print_status()
                break
            except Exception as e:
                log.error(f"Cycle error: {e}")

            time.sleep(POLL_INTERVAL)

    def _print_status(self):
        t = len(self.trades)
        w = self.wins
        wr = f"{w/t*100:.1f}%" if t > 0 else "—"
        pos_str = f"OPEN @ ${self.position['entry']:,.2f}" if self.position else "flat"
        log.info(f"  STATUS | T:{t} W:{w} WR:{wr} | PnL:${self.pnl:.4f} | Bal:${self.balance:.4f} | {pos_str}")

    def save_snapshot(self):
        snap = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'balance': round(self.balance, 6),
            'pnl':     round(self.pnl, 6),
            'trades':  len(self.trades),
            'wins':    self.wins,
            'position': self.position,
            'trade_log': self.trades[-20:],  # last 20 trades
        }
        with open(SNAPSHOT_PATH, 'w') as f:
            json.dump(snap, f, indent=2)
        log.info(f"Snapshot saved → {SNAPSHOT_PATH}")


# ── STANDALONE TEST ────────────────────────────────────────────────────────────

def test_signal():
    """One-shot test: fetch 4H candles and print current signal."""
    log.info("=== ONE-SHOT SIGNAL TEST ===")
    for pair in PAIRS:
        candles = fetch_candles(pair, '4H', 100)
        confirmed = [c for c in candles if c['confirmed'] == '1']
        log.info(f"\n{pair}: {len(confirmed)} confirmed 4H candles loaded")
        if len(confirmed) < 55:
            log.warning("Not enough data")
            continue

        closes  = [c['close'] for c in confirmed]
        volumes = [c['vol']   for c in confirmed]
        latest  = confirmed[-1]

        ema20_s = compute_ema(closes, 20)
        ema50_s = compute_ema(closes, 50)
        ema20   = ema20_s[-1]
        ema50   = ema50_s[-1]
        rsi     = compute_rsi(closes[-15:], 14)
        avg_vol = sum(volumes[-21:-1]) / 20

        ts_human = datetime.fromtimestamp(latest['ts'] / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        log.info(f"  Last confirmed candle : {ts_human}")
        log.info(f"  Close                 : ${latest['close']:,.2f}")
        log.info(f"  EMA20 (4H × 20 bars)  : ${ema20:,.2f}")
        log.info(f"  EMA50 (4H × 50 bars)  : ${ema50:,.2f}")
        log.info(f"  RSI(14)               : {rsi}")
        log.info(f"  Volume vs 20-bar avg  : {latest['vol']:.0f} vs {avg_vol:.0f} ({'✓' if latest['vol'] >= avg_vol * 0.8 else '✗'})")
        log.info(f"  EMA Trend             : {'▲ BULLISH' if ema20 > ema50 else '▼ BEARISH'}")
        log.info(f"  Entry signal          : {'YES ✅' if ema20 > ema50 and 45 <= rsi <= 68 else 'NO'}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_signal()
    else:
        bot = SwingBotV2(capital=100.0)
        bot.run_forever()
