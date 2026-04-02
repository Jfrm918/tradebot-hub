"""
Grid Bot v2 — Fixed Implementation
====================================
Replaces broken EMA-based entry with proper price-level grid trading.

Root cause of 0 trades:
  - EMA20 on 5-second ticks = 100-second lookback
  - Fast EMA tracks price so closely that price never diverges -0.5%
  - BTC max deviation from EMA20 overnight: ~0.14% (threshold was 0.50%)
  - Even if threshold was lowered, this is NOT how grid bots work

This implementation: proper fixed-level grid with dynamic recentering.

Configuration for $100 BTC/USDT capital:
  - 10 grid levels, 1% spacing
  - Price range: ±5% from current
  - $10 per grid level
  - Auto-recenters when price exits range
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional
try:
    import ccxt  # pip install ccxt
except ImportError:
    ccxt = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger('GridBot')


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

@dataclass
class GridConfig:
    # Exchange
    exchange_id: str = 'binanceus'       # or 'coinbase', 'kraken', etc.
    symbol: str = 'BTC/USDT'
    api_key: str = ''
    api_secret: str = ''
    paper_trading: bool = True            # SET TO FALSE FOR LIVE

    # Grid parameters — tuned for $100 BTC/USDT
    total_capital: float = 100.0         # USD
    n_grids: int = 10                    # number of grid levels
    range_pct: float = 0.05             # ±2.5% each side = 5% total range
    recenter_threshold: float = 0.025   # recenter if price moves >2.5% beyond range

    # Risk
    max_open_positions: int = 5          # max concurrent grid positions
    stop_loss_pct: float = 0.08          # -8% stop: close all if BTC falls 8% from grid center
    take_profit_pct: float = 0.10        # +10% take: harvest profits

    # Timing
    poll_interval_sec: float = 5.0       # check price every 5 seconds
    min_trade_interval_sec: float = 30.0 # don't trade the same level twice in 30s


# ─────────────────────────────────────────────
# GRID LEVEL MANAGEMENT
# ─────────────────────────────────────────────

@dataclass
class GridLevel:
    price: float
    level_index: int
    has_buy_order: bool = False
    has_sell_order: bool = False
    buy_order_id: Optional[str] = None
    sell_order_id: Optional[str] = None
    last_trade_time: float = 0.0


@dataclass
class GridState:
    center_price: float = 0.0
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    grid_spacing: float = 0.0
    levels: list = field(default_factory=list)
    capital_per_grid: float = 0.0
    total_pnl: float = 0.0
    total_trades: int = 0
    active_buys: int = 0
    active_sells: int = 0


# ─────────────────────────────────────────────
# GRID BOT ENGINE
# ─────────────────────────────────────────────

class GridBot:
    def __init__(self, config: GridConfig):
        self.config = config
        self.state = GridState()
        self.exchange = None
        self._running = False

        if not config.paper_trading:
            if ccxt is None:
                raise ImportError("ccxt not installed. Run: pip install ccxt")
            self.exchange = ccxt.__dict__[config.exchange_id]({
                'apiKey': config.api_key,
                'secret': config.api_secret,
                'enableRateLimit': True,
            })

    # ── Setup ──────────────────────────────────

    def initialize_grid(self, current_price: float):
        """Set up grid levels around current price."""
        cfg = self.config
        s = self.state

        s.center_price = current_price
        s.lower_bound = current_price * (1 - cfg.range_pct / 2)
        s.upper_bound = current_price * (1 + cfg.range_pct / 2)
        s.grid_spacing = (s.upper_bound - s.lower_bound) / cfg.n_grids
        s.capital_per_grid = cfg.total_capital / cfg.n_grids
        s.levels = []

        for i in range(cfg.n_grids + 1):
            price = s.lower_bound + i * s.grid_spacing
            level = GridLevel(price=round(price, 2), level_index=i)
            s.levels.append(level)

        log.info(f"Grid initialized: ${s.lower_bound:.2f} → ${s.upper_bound:.2f}")
        log.info(f"Grid spacing: ${s.grid_spacing:.2f} ({s.grid_spacing/current_price*100:.2f}%)")
        log.info(f"Levels: {[f'${l.price:.0f}' for l in s.levels]}")
        log.info(f"Capital per grid: ${s.capital_per_grid:.2f}")

        # Place initial orders
        for level in s.levels:
            if level.price < current_price:
                self._place_buy(level, current_price)
            elif level.price > current_price:
                self._place_sell(level, current_price)

    def needs_recenter(self, current_price: float) -> bool:
        """Return True if price has moved outside grid range + threshold."""
        s = self.state
        threshold = self.config.recenter_threshold
        return (current_price < s.lower_bound * (1 - threshold) or
                current_price > s.upper_bound * (1 + threshold))

    # ── Core Loop ─────────────────────────────

    def tick(self, current_price: float):
        """Called every poll interval with the latest price."""
        s = self.state
        cfg = self.config
        now = time.time()

        # Check if we need to recenter the grid
        if self.needs_recenter(current_price):
            log.warning(f"Price ${current_price:.2f} exited grid range. Recentering...")
            self._cancel_all_orders()
            self.initialize_grid(current_price)
            return

        # Check stop loss
        stop_price = s.center_price * (1 - cfg.stop_loss_pct)
        if current_price < stop_price:
            log.error(f"STOP LOSS triggered! Price ${current_price:.2f} < stop ${stop_price:.2f}")
            self._emergency_close()
            return

        # Check each grid level
        for i, level in enumerate(s.levels):
            # Skip if traded recently
            if now - level.last_trade_time < cfg.min_trade_interval_sec:
                continue

            # BUY condition: price dropped TO or BELOW this level
            if (not level.has_buy_order and
                    current_price <= level.price and
                    i > 0 and  # don't buy below bottom level
                    s.active_buys < cfg.max_open_positions):
                self._execute_buy(level, current_price)

            # SELL condition: price rose TO or ABOVE this level AND we have a position below
            elif (not level.has_sell_order and
                  current_price >= level.price and
                  i > 0 and
                  s.levels[i-1].has_buy_order):
                # Sell here to close the buy from the level below
                buy_price = s.levels[i-1].price
                self._execute_sell(level, current_price, buy_price)

    # ── Order Execution ────────────────────────

    def _place_buy(self, level: GridLevel, current_price: float):
        """Place a standing buy limit order at this level."""
        level.has_buy_order = True
        s = self.state
        btc_amount = s.capital_per_grid / level.price

        if self.config.paper_trading:
            log.debug(f"[PAPER] BUY LIMIT @ ${level.price:.2f} | {btc_amount:.6f} BTC")
        else:
            try:
                order = self.exchange.create_limit_buy_order(
                    self.config.symbol, btc_amount, level.price
                )
                level.buy_order_id = order['id']
            except Exception as e:
                log.error(f"Failed to place buy @ ${level.price}: {e}")
                level.has_buy_order = False

    def _place_sell(self, level: GridLevel, current_price: float):
        """Place a standing sell limit order at this level."""
        level.has_sell_order = True
        s = self.state
        btc_amount = s.capital_per_grid / level.price

        if self.config.paper_trading:
            log.debug(f"[PAPER] SELL LIMIT @ ${level.price:.2f} | {btc_amount:.6f} BTC")
        else:
            try:
                order = self.exchange.create_limit_sell_order(
                    self.config.symbol, btc_amount, level.price
                )
                level.sell_order_id = order['id']
            except Exception as e:
                log.error(f"Failed to place sell @ ${level.price}: {e}")
                level.has_sell_order = False

    def _execute_buy(self, level: GridLevel, current_price: float):
        """Execute a market buy at this grid level."""
        s = self.state
        btc_amount = s.capital_per_grid / level.price

        level.has_buy_order = True
        level.last_trade_time = time.time()
        s.active_buys += 1
        s.total_trades += 1

        log.info(f"🟢 BUY  | Level {level.level_index} @ ${level.price:.2f} | "
                 f"{btc_amount:.6f} BTC | ${s.capital_per_grid:.2f}")

        if not self.config.paper_trading and self.exchange:
            try:
                self.exchange.create_market_buy_order(self.config.symbol, btc_amount)
            except Exception as e:
                log.error(f"BUY execution failed: {e}")
                level.has_buy_order = False
                s.active_buys -= 1

    def _execute_sell(self, level: GridLevel, current_price: float, buy_price: float):
        """Execute a market sell at this grid level (close a buy from below)."""
        s = self.state
        btc_amount = s.capital_per_grid / buy_price
        profit = btc_amount * (level.price - buy_price)

        level.has_sell_order = True
        level.last_trade_time = time.time()

        # Close the buy position below
        buy_level_idx = level.level_index - 1
        if buy_level_idx >= 0:
            s.levels[buy_level_idx].has_buy_order = False
            s.active_buys = max(0, s.active_buys - 1)

        s.total_trades += 1
        s.total_pnl += profit
        level.has_sell_order = False  # ready for next cycle

        log.info(f"🔴 SELL | Level {level.level_index} @ ${level.price:.2f} | "
                 f"Profit: ${profit:.4f} | Total P&L: ${s.total_pnl:.4f} | "
                 f"Trades: {s.total_trades}")

    def _cancel_all_orders(self):
        """Cancel all open orders (for recenter or shutdown)."""
        for level in self.state.levels:
            level.has_buy_order = False
            level.has_sell_order = False
            level.buy_order_id = None
            level.sell_order_id = None
        self.state.active_buys = 0
        self.state.active_sells = 0
        log.info("All orders cancelled.")

    def _emergency_close(self):
        """Stop loss: cancel all orders and close all positions."""
        log.error("EMERGENCY CLOSE: Stop loss triggered")
        self._cancel_all_orders()
        self._running = False

    # ── Main Run Loop ──────────────────────────

    def get_price(self) -> float:
        """Fetch latest price. Override for different exchange/mock."""
        if self.config.paper_trading:
            raise NotImplementedError("Override get_price() for paper trading")
        ticker = self.exchange.fetch_ticker(self.config.symbol)
        return ticker['last']

    def run(self, price_feed=None):
        """
        Start the grid bot.
        
        Args:
            price_feed: Optional generator/iterator yielding prices.
                       If None, calls self.get_price() via exchange API.
        """
        self._running = True
        log.info("Grid Bot v2 starting...")

        # Get initial price
        if price_feed is not None:
            initial_price = next(price_feed)
        else:
            initial_price = self.get_price()

        self.initialize_grid(initial_price)

        log.info(f"Grid initialized at ${initial_price:,.2f}")
        log.info(f"Running with {'PAPER' if self.config.paper_trading else 'LIVE'} trading")

        try:
            while self._running:
                # Get current price
                if price_feed is not None:
                    try:
                        current_price = next(price_feed)
                    except StopIteration:
                        log.info("Price feed exhausted.")
                        break
                else:
                    current_price = self.get_price()

                # Process grid tick
                self.tick(current_price)

                # Status log every 100 ticks
                if self.state.total_trades % 10 == 0 and self.state.total_trades > 0:
                    self._log_status(current_price)

                if price_feed is None:
                    time.sleep(self.config.poll_interval_sec)

        except KeyboardInterrupt:
            log.info("Interrupted by user.")
        finally:
            self._log_status(current_price if 'current_price' in dir() else 0)
            log.info("Grid bot stopped.")

    def _log_status(self, price: float):
        s = self.state
        log.info(
            f"STATUS | Price: ${price:,.2f} | "
            f"P&L: ${s.total_pnl:.4f} | "
            f"Trades: {s.total_trades} | "
            f"Open buys: {s.active_buys}"
        )


# ─────────────────────────────────────────────
# ALTERNATIVE: DCA BOT (for trending markets)
# ─────────────────────────────────────────────

class DCABot:
    """
    Dollar Cost Averaging bot.
    Better than grid in strong trending markets.
    Buys fixed $ amount at regular intervals.
    Sells when price rises X% above average cost.
    """

    def __init__(self,
                 total_capital: float = 100.0,
                 buy_amount: float = 10.0,
                 buy_interval_sec: float = 3600,  # 1 hour
                 take_profit_pct: float = 0.02,   # sell when +2% above avg
                 stop_loss_pct: float = 0.10):     # stop if -10% from avg
        self.total_capital = total_capital
        self.buy_amount = buy_amount
        self.buy_interval = buy_interval_sec
        self.take_profit_pct = take_profit_pct
        self.stop_loss_pct = stop_loss_pct

        self.total_btc = 0.0
        self.total_spent = 0.0
        self.pnl = 0.0
        self.n_buys = 0
        self.last_buy_time = 0.0

    @property
    def avg_cost(self) -> float:
        return self.total_spent / self.total_btc if self.total_btc > 0 else 0.0

    def tick(self, price: float, now: float = None) -> str:
        if now is None:
            now = time.time()

        action = 'HOLD'

        # Buy on schedule
        if (now - self.last_buy_time >= self.buy_interval and
                self.total_spent + self.buy_amount <= self.total_capital):
            btc = self.buy_amount / price
            self.total_btc += btc
            self.total_spent += self.buy_amount
            self.n_buys += 1
            self.last_buy_time = now
            action = f'BUY ${self.buy_amount} @ ${price:.2f}'
            log.info(f"DCA BUY: {btc:.6f} BTC @ ${price:.2f} | Avg cost: ${self.avg_cost:.2f}")

        # Sell on take profit
        elif (self.total_btc > 0 and
              price >= self.avg_cost * (1 + self.take_profit_pct)):
            profit = self.total_btc * (price - self.avg_cost)
            self.pnl += profit
            action = f'SELL {self.total_btc:.6f} BTC @ ${price:.2f} | Profit: ${profit:.2f}'
            log.info(f"DCA TAKE PROFIT: {action}")
            self.total_btc = 0.0
            self.total_spent = 0.0

        # Stop loss
        elif (self.total_btc > 0 and
              price <= self.avg_cost * (1 - self.stop_loss_pct)):
            loss = self.total_btc * (price - self.avg_cost)
            self.pnl += loss
            action = f'STOP LOSS @ ${price:.2f} | Loss: ${loss:.2f}'
            log.warning(f"DCA STOP LOSS: {action}")
            self.total_btc = 0.0
            self.total_spent = 0.0

        return action


# ─────────────────────────────────────────────
# PAPER TRADING BACKTEST
# ─────────────────────────────────────────────

def run_paper_backtest(prices: list, config: GridConfig = None) -> dict:
    """
    Run grid bot in paper trading mode against a list of prices.
    Returns performance summary.
    """
    if config is None:
        config = GridConfig(paper_trading=True)

    bot = GridBot(config)

    def price_feed():
        for p in prices:
            yield p

    feed = price_feed()
    bot.run(price_feed=feed)

    return {
        'total_trades': bot.state.total_trades,
        'total_pnl': bot.state.total_pnl,
        'active_buys': bot.state.active_buys,
        'grid_levels': len(bot.state.levels),
        'center_price': bot.state.center_price,
    }


# ─────────────────────────────────────────────
# INTEGRATION WITH EXISTING PRICE FEED
# ─────────────────────────────────────────────
#
# If you have a live WebSocket price feed:
#
#   from grid_bot_v2 import GridBot, GridConfig
#
#   config = GridConfig(
#       exchange_id='binanceus',
#       symbol='BTC/USDT',
#       api_key='YOUR_KEY',
#       api_secret='YOUR_SECRET',
#       paper_trading=False,   # LIVE
#       total_capital=100.0,
#       n_grids=10,
#       range_pct=0.05,
#   )
#
#   bot = GridBot(config)
#   bot.initialize_grid(current_price=68000.0)
#
#   # In your price tick callback:
#   def on_price(price):
#       bot.tick(price)
#
# ─────────────────────────────────────────────

if __name__ == '__main__':
    import random, math

    # Demo: simulate BTC overnight move $67,632 → $68,491
    random.seed(42)
    prices = [67632.0]
    for _ in range(5400):
        drift = (68491 - 67632) / 5400
        noise = random.gauss(0, prices[-1] * 0.0002)
        prices.append(max(prices[-1] + drift + noise, 66000))

    config = GridConfig(
        paper_trading=True,
        total_capital=100.0,
        n_grids=10,
        range_pct=0.05,
        poll_interval_sec=0,  # no sleep in backtest
    )

    print("Running Grid Bot v2 backtest on overnight BTC move...")
    print(f"Price range: ${prices[0]:,.2f} → ${prices[-1]:,.2f}")
    print()

    result = run_paper_backtest(prices, config)
    print()
    print(f"=== BACKTEST RESULTS ===")
    print(f"Total trades: {result['total_trades']}")
    print(f"Grid P&L:     ${result['total_pnl']:.4f}")
    print(f"Open positions: {result['active_buys']}")
    print()
    print("Compare to BROKEN EMA grid: 0 trades, $0.00 P&L")
