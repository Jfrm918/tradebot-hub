"""
scalp_v2.py — Improved Scalping Strategy
==========================================
Key changes from v1:
  - TP raised to 0.45% (was 0.12%) → fixes the fee problem
  - SL raised to 0.15% (was 0.08%) → gives trade room to breathe
  - RSI(14) replaces RSI(7) — less noise
  - Volume spike filter added — only trade on conviction
  - VWAP context filter — trend alignment
  - Spread check — skip bad fill environments
  - RSI cross signal — replaces "3 ticks up"
  - Rolling performance monitor — auto-pause if on a cold streak

Math:
  Breakeven WR = (SL + fee) / (TP + SL) = (0.15 + 0.11) / (0.45 + 0.15) = 43.3%
  At 50% WR: EV/trade = 0.50*$1.02 - 0.50*$0.78 = +$0.12 per trade
  At 55% WR: EV/trade = 0.55*$1.02 - 0.45*$0.78 = +$0.21 per trade
  (position = $30)
"""

import collections
import numpy as np

# ─── CONFIG ──────────────────────────────────────────────────────────────────
TP_PCT          = 0.0045   # +0.45% take profit (was 0.12%)
SL_PCT          = 0.0015   # -0.15% stop loss (was 0.08%)
FEE_RT          = 0.0011   # 0.11% roundtrip fee
CAPITAL_ALLOC   = 0.30     # 30% per trade
MAX_HOLD_CYCLES = 240      # 20 min max hold (was 10 min — give trade time)

# Entry filters
RSI_PERIOD      = 14       # RSI period (was 7 — more stable)
RSI_LOWER       = 40       # RSI must be above this (was 30)
RSI_UPPER       = 65       # RSI must be below this (relaxed from 62)
RSI_CROSS_ABOVE = 50       # RSI must have crossed above 50 in last N bars
RSI_CROSS_BARS  = 3        # how many bars back to look for cross

VOLUME_PERIOD   = 20       # bars for average volume
VOLUME_MULT     = 1.5      # volume must be this multiple of avg

VWAP_PERIOD     = 200      # bars for rolling VWAP (~16 min on 5s)
MAX_SPREAD_PCT  = 0.0005   # 0.05% max spread to enter

# Rolling performance monitor
ROLLING_WR_WINDOW = 20     # check last N trades
PAUSE_IF_WR_BELOW = 0.38   # pause if rolling WR < 38% (cold streak)


# ─── INDICATORS ──────────────────────────────────────────────────────────────

def compute_rsi(prices: list, period: int = 14) -> float:
    """Compute RSI from a list of close prices. Returns float or None."""
    if len(prices) < period + 1:
        return None
    deltas = np.diff(prices[-(period + 1):])
    gains  = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    if avg_loss == 0:
        return 100.0
    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)


def compute_ema(prices: list, period: int) -> float:
    """Compute EMA from price list."""
    if len(prices) < period:
        return None
    k   = 2 / (period + 1)
    ema = prices[-period]  # seed
    for p in prices[-period + 1:]:
        ema = p * k + ema * (1 - k)
    return ema


def compute_vwap(prices: list, volumes: list, period: int = 200) -> float:
    """Rolling VWAP over last N bars."""
    n = min(period, len(prices), len(volumes))
    if n == 0:
        return None
    p = np.array(prices[-n:])
    v = np.array(volumes[-n:])
    if v.sum() == 0:
        return None
    return float(np.sum(p * v) / np.sum(v))


def rsi_crossed_above(rsi_history: list, level: float = 50, lookback: int = 3) -> bool:
    """True if RSI crossed above `level` within last `lookback` bars."""
    if len(rsi_history) < lookback + 1:
        return False
    recent = rsi_history[-(lookback + 1):]
    for i in range(len(recent) - 1):
        if recent[i] < level and recent[i + 1] >= level:
            return True
    return False


def volume_spike(volumes: list, period: int = 20, mult: float = 1.5) -> bool:
    """True if latest volume > mult * rolling average."""
    if len(volumes) < period + 1:
        return False
    avg_vol = np.mean(volumes[-(period + 1):-1])
    return volumes[-1] > mult * avg_vol if avg_vol > 0 else False


# ─── SCALPER CLASS ────────────────────────────────────────────────────────────

class ScalpV2:
    def __init__(self, capital: float = 100.0):
        self.capital       = capital
        self.in_trade      = False
        self.entry_price   = None
        self.hold_cycles   = 0
        self.position_size = 0.0

        # Price/volume history
        self.prices  = collections.deque(maxlen=max(RSI_PERIOD * 3, VWAP_PERIOD) + 10)
        self.volumes = collections.deque(maxlen=VWAP_PERIOD + 10)
        self.rsi_history = collections.deque(maxlen=RSI_CROSS_BARS + 5)

        # Trade log for rolling WR monitor
        self.trade_results = collections.deque(maxlen=ROLLING_WR_WINDOW)
        self.paused        = False
        self.trades_total  = 0
        self.pnl_total     = 0.0

    # ── State properties ──────────────────────────────────────────────────

    @property
    def rolling_win_rate(self) -> float:
        if len(self.trade_results) < 5:
            return 1.0  # not enough data, don't pause
        return sum(self.trade_results) / len(self.trade_results)

    # ── Per-tick update ───────────────────────────────────────────────────

    def on_tick(self, price: float, volume: float, spread: float) -> dict:
        """
        Call on every 5-second tick.
        Returns action dict: {'action': 'buy'|'sell'|'hold', 'reason': str}
        """
        self.prices.append(price)
        self.volumes.append(volume)

        prices_list  = list(self.prices)
        volumes_list = list(self.volumes)

        rsi  = compute_rsi(prices_list, RSI_PERIOD)
        vwap = compute_vwap(prices_list, volumes_list, VWAP_PERIOD)

        if rsi is not None:
            self.rsi_history.append(rsi)

        # ── EXIT LOGIC (priority over entry) ──────────────────────────────
        if self.in_trade:
            self.hold_cycles += 1
            pct_change = (price - self.entry_price) / self.entry_price

            exit_reason = None
            if pct_change >= TP_PCT:
                exit_reason = f"TP hit +{pct_change*100:.3f}%"
                result = 1  # win
            elif pct_change <= -SL_PCT:
                exit_reason = f"SL hit {pct_change*100:.3f}%"
                result = 0  # loss
            elif self.hold_cycles >= MAX_HOLD_CYCLES:
                exit_reason = f"Max hold ({self.hold_cycles} cycles)"
                result = 1 if pct_change > 0 else 0

            if exit_reason:
                net_pct   = pct_change - FEE_RT
                pnl       = self.position_size * net_pct
                self.pnl_total += pnl
                self.trade_results.append(result)
                self.trades_total += 1
                self.in_trade    = False
                self.entry_price = None
                self.hold_cycles = 0

                # Check if we should pause
                self.paused = self.rolling_win_rate < PAUSE_IF_WR_BELOW

                return {
                    'action': 'sell',
                    'reason': exit_reason,
                    'pnl':    round(pnl, 4),
                    'pnl_total': round(self.pnl_total, 4),
                    'rolling_wr': round(self.rolling_win_rate, 3),
                    'paused': self.paused,
                }
            return {'action': 'hold', 'cycles': self.hold_cycles}

        # ── ENTRY LOGIC ───────────────────────────────────────────────────
        if self.paused:
            # Unpause if rolling WR recovered
            self.paused = self.rolling_win_rate < PAUSE_IF_WR_BELOW
            if self.paused:
                return {'action': 'hold', 'reason': 'paused — cold streak'}

        if rsi is None or vwap is None:
            return {'action': 'hold', 'reason': 'insufficient data'}

        reasons_failed = []

        # Filter 1: Spread check
        if spread > MAX_SPREAD_PCT:
            reasons_failed.append(f'spread {spread*100:.3f}% > {MAX_SPREAD_PCT*100:.3f}%')

        # Filter 2: RSI in range
        if not (RSI_LOWER <= rsi <= RSI_UPPER):
            reasons_failed.append(f'RSI {rsi:.1f} out of range [{RSI_LOWER},{RSI_UPPER}]')

        # Filter 3: RSI crossed above 50 recently (momentum shift)
        if not rsi_crossed_above(list(self.rsi_history), 50, RSI_CROSS_BARS):
            reasons_failed.append('RSI did not cross 50 recently')

        # Filter 4: Volume spike
        if not volume_spike(volumes_list, VOLUME_PERIOD, VOLUME_MULT):
            reasons_failed.append(f'no volume spike (need {VOLUME_MULT}x avg)')

        # Filter 5: Price above VWAP (trend alignment for longs)
        if price < vwap:
            reasons_failed.append(f'price ${price:.4f} below VWAP ${vwap:.4f}')

        if reasons_failed:
            return {'action': 'hold', 'reason': '; '.join(reasons_failed)}

        # ── ENTER ─────────────────────────────────────────────────────────
        self.in_trade      = True
        self.entry_price   = price
        self.hold_cycles   = 0
        self.position_size = self.capital * CAPITAL_ALLOC

        return {
            'action':    'buy',
            'price':     price,
            'tp':        round(price * (1 + TP_PCT), 6),
            'sl':        round(price * (1 - SL_PCT), 6),
            'rsi':       round(rsi, 1),
            'vwap':      round(vwap, 4),
            'position':  round(self.position_size, 2),
        }


# ─── QUICK BACKTEST SIMULATOR ────────────────────────────────────────────────

def simulate_strategy(n_trades=200, win_rate=0.55, tp=TP_PCT, sl=SL_PCT,
                      fee=FEE_RT, capital=100.0, alloc=CAPITAL_ALLOC, seed=42):
    """
    Monte Carlo sim of the improved strategy given expected WR.
    Returns dict with PnL stats.
    """
    rng = np.random.default_rng(seed)
    position = capital * alloc
    pnls = []
    for _ in range(n_trades):
        if rng.random() < win_rate:
            pnl = position * (tp - fee)
        else:
            pnl = -position * (sl + fee)
        pnls.append(pnl)

    pnls   = np.array(pnls)
    cumsum = np.cumsum(pnls)
    return {
        'n_trades':    n_trades,
        'win_rate':    win_rate,
        'total_pnl':   round(float(cumsum[-1]), 2),
        'avg_pnl':     round(float(pnls.mean()), 4),
        'sharpe_proxy': round(float(pnls.mean() / pnls.std()), 4) if pnls.std() > 0 else 0,
        'max_drawdown': round(float((cumsum - np.maximum.accumulate(cumsum)).min()), 2),
        'pnl_per_100': round(float(pnls.mean() * 100), 2),
    }


# ─── EXAMPLE USAGE ───────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("SCALP V2 — SIMULATION PROJECTIONS")
    print("=" * 60)
    print(f"TP={TP_PCT*100:.2f}%  SL={SL_PCT*100:.2f}%  Fee={FEE_RT*100:.2f}% RT")
    print(f"Breakeven WR = {(SL_PCT+FEE_RT)/(TP_PCT+SL_PCT)*100:.1f}%")
    print()

    for wr in [0.44, 0.48, 0.50, 0.55, 0.58, 0.60]:
        r = simulate_strategy(n_trades=100, win_rate=wr)
        status = "✅" if r['total_pnl'] > 0 else "❌"
        print(f"  WR={wr*100:.0f}%  → PnL/100 trades: ${r['pnl_per_100']:+.2f}  "
              f"MaxDD: ${r['max_drawdown']:.2f}  {status}")

    print()
    print("Expected with improved entry (55% WR):")
    r = simulate_strategy(n_trades=500, win_rate=0.55)
    print(f"  500 trades: ${r['total_pnl']:+.2f} on $100 capital")
    print(f"  Avg per trade: ${r['avg_pnl']:+.4f}")
    print(f"  Max Drawdown: ${r['max_drawdown']:.2f}")
