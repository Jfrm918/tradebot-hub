#!/usr/bin/env python3
"""
VWAP Momentum Trading Bot (Bot 7)
Trades BTC-USDT and ETH-USDT using VWAP with volume confirmation
- Entry: Price > VWAP by 0.5% AND current volume > 1.5x 20-period average
- Exit: Price < VWAP OR +2% take profit OR -1% stop loss (from VWAP)
- Position size: 35% of available capital per trade
- Max 2 open positions (one BTC, one ETH)
"""

import json
import time
import logging
from datetime import datetime, timedelta
from collections import deque
import ccxt

# Configure logging with open_position field
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - VWAP - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/jfrm918/.openclaw/workspace/trading_bots/bots/vwap_momentum_bot.log'),
        logging.StreamHandler()
    ]
)

class VWAPMomentumBot:
    def __init__(self, config_path='/Users/jfrm918/.openclaw/workspace/trading_bots/config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Strategy parameters
        self.capital = 100.0  # $100 simulated capital
        self.position_size_pct = 0.35  # 35% per trade
        self.max_positions = 2
        self.vwap_threshold = 0.005  # 0.5% above VWAP for entry
        self.volume_multiplier = 1.5  # 1.5x volume threshold
        self.tp_pct = 0.02  # 2% take profit
        self.sl_pct = 0.01  # 1% stop loss (from VWAP)
        
        # State
        self.balance = self.capital
        self.pnl = 0.0
        self.open_positions = {}  # {pair: {price, amount, entry_vwap, entry_time}}
        self.closed_trades = []  # Track all closed trades
        self.trades = []  # All trades (BUY/SELL)
        
        # VWAP calculations (24-hour rolling window = 1440 minutes)
        self.vwap_windows = {
            'BTC-USDT': deque(maxlen=1440),
            'ETH-USDT': deque(maxlen=1440)
        }
        
        # Volume tracking (20-period average)
        self.volume_windows = {
            'BTC-USDT': deque(maxlen=20),
            'ETH-USDT': deque(maxlen=20)
        }
        
        self.exchange = self._init_exchange()
        
        logging.info(f"VWAP Momentum Bot initialized")
        logging.info(f"Capital: ${self.capital} | Position size: {self.position_size_pct*100:.0f}% | Max positions: {self.max_positions}")
        logging.info(f"Entry: >VWAP by {self.vwap_threshold*100:.1f}% + {self.volume_multiplier}x volume | Exit: <VWAP or ±{self.tp_pct*100:.0f}%")
    
    def _init_exchange(self):
        """Initialize Blofin exchange connection (paper trading)"""
        try:
            exchange = ccxt.blofin({
                'enableRateLimit': True,
                'test': False,  # Paper trading mode
            })
            logging.info("Connected to Blofin exchange (paper trading)")
            return exchange
        except Exception as e:
            logging.error(f"Failed to initialize exchange: {e}")
            return None
    
    def _calculate_vwap(self, pair):
        """Calculate VWAP from 24-hour rolling window"""
        if not self.vwap_windows[pair]:
            return None
        
        total_pv = sum(pv for pv, v in self.vwap_windows[pair])
        total_volume = sum(v for pv, v in self.vwap_windows[pair])
        
        if total_volume == 0:
            return None
        
        return total_pv / total_volume
    
    def _get_avg_volume(self, pair):
        """Get 20-period average volume"""
        if not self.volume_windows[pair]:
            return 0
        return sum(self.volume_windows[pair]) / len(self.volume_windows[pair])
    
    def _fetch_candles(self, pair, timeframe='1m', limit=50):
        """Fetch OHLCV data from exchange"""
        try:
            if not self.exchange:
                return None
            ohlcv = self.exchange.fetch_ohlcv(pair, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logging.warning(f"Error fetching candles for {pair}: {e}")
            return None
    
    def _update_vwap_window(self, pair, price, volume):
        """Add price×volume to rolling 24-hour window"""
        pv = price * volume
        self.vwap_windows[pair].append((pv, volume))
    
    def _update_volume_window(self, pair, volume):
        """Add volume to 20-period window"""
        self.volume_windows[pair].append(volume)
    
    def _check_entry_signal(self, pair, current_price, current_volume):
        """Check entry conditions: price > VWAP + 0.5% AND volume > 1.5x average"""
        vwap = self._calculate_vwap(pair)
        if not vwap:
            return False, None
        
        avg_volume = self._get_avg_volume(pair)
        vwap_threshold_price = vwap * (1 + self.vwap_threshold)
        
        price_above = current_price > vwap_threshold_price
        volume_high = current_volume > (avg_volume * self.volume_multiplier)
        
        if price_above and volume_high:
            logging.info(f"{pair} Entry signal: Price ${current_price:.2f} > VWAP ${vwap:.2f} + {self.vwap_threshold*100:.1f}% | Volume {current_volume:.0f} > {avg_volume*self.volume_multiplier:.0f}")
            return True, vwap
        
        return False, vwap
    
    def _check_exit_conditions(self, pair, current_price, vwap):
        """Check exit: price < VWAP OR TP hit OR SL hit"""
        if pair not in self.open_positions:
            return None
        
        pos = self.open_positions[pair]
        entry_price = pos['price']
        entry_vwap = pos['entry_vwap']
        
        # Exit condition 1: Price closes below VWAP
        if current_price < vwap:
            logging.info(f"{pair} Exit signal: Price ${current_price:.2f} < VWAP ${vwap:.2f}")
            return 'close_below_vwap'
        
        # Exit condition 2: Take profit at 2% above entry
        tp_price = entry_price * (1 + self.tp_pct)
        if current_price >= tp_price:
            logging.info(f"{pair} Take profit: Price ${current_price:.2f} >= ${tp_price:.2f} (+{self.tp_pct*100:.0f}%)")
            return 'take_profit'
        
        # Exit condition 3: Stop loss at 1% below VWAP (entry VWAP)
        sl_price = entry_vwap * (1 - self.sl_pct)
        if current_price <= sl_price:
            logging.info(f"{pair} Stop loss: Price ${current_price:.2f} <= ${sl_price:.2f} (-{self.sl_pct*100:.0f}% from VWAP)")
            return 'stop_loss'
        
        return None
    
    def _execute_buy(self, pair, price, vwap):
        """Execute BUY trade"""
        if len(self.open_positions) >= self.max_positions:
            logging.warning(f"Max positions ({self.max_positions}) reached. Skipping {pair}")
            return False
        
        if pair in self.open_positions:
            logging.warning(f"{pair} position already open. Skipping")
            return False
        
        position_size = self.capital * self.position_size_pct
        amount = position_size / price
        
        if position_size > self.balance:
            logging.warning(f"Insufficient balance for {pair} (need ${position_size:.2f}, have ${self.balance:.2f})")
            return False
        
        # Record position
        self.open_positions[pair] = {
            'price': price,
            'amount': amount,
            'entry_vwap': vwap,
            'entry_time': datetime.now().isoformat(),
            'entry_price': price
        }
        
        # Update balance
        self.balance -= position_size
        
        # Log trade
        trade = {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'action': 'BUY',
            'price': price,
            'amount': amount,
            'cost': position_size,
            'vwap': vwap,
            'open_position': True
        }
        self.trades.append(trade)
        
        logging.info(f"BUY {amount:.6f} {pair} @ ${price:.2f} | Size: ${position_size:.2f} | VWAP: ${vwap:.2f} | Balance: ${self.balance:.2f} | open_position=True")
        return True
    
    def _execute_sell(self, pair, price, exit_reason):
        """Execute SELL trade"""
        if pair not in self.open_positions:
            return False
        
        pos = self.open_positions[pair]
        amount = pos['amount']
        entry_price = pos['price']
        proceeds = amount * price
        
        # Calculate PnL
        cost = entry_price * amount
        trade_pnl = proceeds - cost
        self.pnl += trade_pnl
        self.balance += proceeds
        
        # Record closed trade
        closed_trade = {
            'pair': pair,
            'entry_price': entry_price,
            'exit_price': price,
            'amount': amount,
            'pnl': trade_pnl,
            'pnl_pct': (trade_pnl / cost) * 100,
            'exit_reason': exit_reason,
            'entry_time': pos['entry_time'],
            'exit_time': datetime.now().isoformat()
        }
        self.closed_trades.append(closed_trade)
        
        # Log trade
        trade = {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'action': 'SELL',
            'price': price,
            'amount': amount,
            'proceeds': proceeds,
            'exit_reason': exit_reason,
            'pnl': trade_pnl,
            'open_position': False
        }
        self.trades.append(trade)
        
        # Remove position
        del self.open_positions[pair]
        
        win_loss = '✅' if trade_pnl > 0 else '❌'
        logging.info(f"{win_loss} SELL {amount:.6f} {pair} @ ${price:.2f} | Reason: {exit_reason} | PnL: ${trade_pnl:.2f} ({closed_trade['pnl_pct']:.2f}%) | Balance: ${self.balance:.2f} | open_position=False")
        return True
    
    def _process_pair(self, pair):
        """Process single trading pair"""
        try:
            # Fetch recent candles (1-minute)
            ohlcv = self._fetch_candles(pair, '1m', limit=50)
            if not ohlcv or len(ohlcv) < 2:
                return
            
            # Get latest candle
            latest = ohlcv[-1]
            current_price = latest[4]  # close
            current_volume = latest[5]  # volume
            
            # Update VWAP and volume windows
            self._update_vwap_window(pair, current_price, current_volume)
            self._update_volume_window(pair, current_volume)
            
            # Get current VWAP
            vwap = self._calculate_vwap(pair)
            if not vwap:
                return
            
            # Check for exit signals on existing positions
            if pair in self.open_positions:
                exit_signal = self._check_exit_conditions(pair, current_price, vwap)
                if exit_signal:
                    self._execute_sell(pair, current_price, exit_signal)
            
            # Check for entry signals (only if no position)
            if pair not in self.open_positions:
                should_enter, entry_vwap = self._check_entry_signal(pair, current_price, current_volume)
                if should_enter:
                    self._execute_buy(pair, current_price, entry_vwap)
        
        except Exception as e:
            logging.error(f"Error processing {pair}: {e}")
    
    def run(self):
        """Main bot loop"""
        if not self.exchange:
            logging.error("Cannot run without exchange connection")
            return
        
        for pair in self.config['trading_pairs']:
            self._process_pair(pair)
    
    def report(self):
        """Generate performance report"""
        wins = len([t for t in self.closed_trades if t['pnl'] > 0])
        total = len(self.closed_trades)
        win_rate = (wins / total * 100) if total > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in self.closed_trades)
        
        report = {
            'strategy': 'VWAP Momentum',
            'total_trades': len(self.closed_trades),
            'wins': wins,
            'losses': total - wins,
            'win_rate': f"{win_rate:.1f}%",
            'total_pnl': f"${total_pnl:.2f}",
            'balance': f"${self.balance:.2f}",
            'open_positions': len(self.open_positions),
            'recent_trades': self.closed_trades[-10:]
        }
        
        logging.info(f"Report: {json.dumps(report, indent=2)}")
        return report

if __name__ == '__main__':
    bot = VWAPMomentumBot()
    
    # Run continuously
    while True:
        try:
            bot.run()
            time.sleep(60)  # Update every minute (1m candles)
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            bot.report()
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(60)
