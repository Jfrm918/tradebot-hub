#!/usr/bin/env python3
"""
VWAP Reversion Trading Bot
Identifies mean reversion using VWAP + RSI
Entry: Price drops >0.8% below VWAP AND RSI(14) <40
Exit: Price within 0.1% of VWAP OR stop loss at 1.5% below entry
Max 2 open positions (one BTC, one ETH)
Position size: 40% of available capital per trade
Paper trading mode with $100 simulated capital per pair
"""

import json
import time
import logging
from datetime import datetime, timedelta
from collections import deque
import requests
import os

# Logging setup - both console and file
# Use absolute path for log file
bots_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(bots_dir, 'vwap_reversion_bot.log')

# Configure root logger to avoid conflicts
root_logger = logging.getLogger()
root_logger.handlers = []  # Clear existing handlers

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - VWAP_REVERSION - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to root logger
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

class VWAPReversionBot:
    def __init__(self, config_path='../config.json'):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except:
            # Fallback config if file not found
            self.config = {
                'trading_pairs': ['BTC-USDT', 'ETH-USDT'],
                'update_interval': 300
            }
        
        self.trading_pairs = ['BTC-USDT', 'ETH-USDT']
        self.capital_per_pair = 100.0
        self.position_size_ratio = 0.40  # 40% per trade
        self.max_positions = 2
        
        # VWAP & RSI parameters
        self.vwap_window = 24 * 3600  # 24-hour rolling window in seconds
        self.vwap_threshold = 0.008  # 0.8% below VWAP for entry
        self.rsi_entry_threshold = 40
        self.exit_profit_threshold = 0.001  # 0.1% above VWAP for exit
        self.stop_loss_pct = 0.015  # 1.5% below entry
        
        # State per pair
        self.positions = {}  # {pair: {'entry_price': X, 'entry_amount': Y, 'entry_time': Z}}
        self.balances = {pair: self.capital_per_pair for pair in self.trading_pairs}
        self.trades = []
        self.pnl_by_pair = {pair: 0.0 for pair in self.trading_pairs}
        
        # History for VWAP calculation
        self.price_history = {pair: deque(maxlen=1000) for pair in self.trading_pairs}  # Store (price, volume, timestamp)
        
        logging.info(f"VWAP Reversion Bot initialized | Capital per pair: ${self.capital_per_pair}")
    
    def fetch_market_data(self):
        """Fetch current prices from Blofin API"""
        try:
            url = 'https://openapi.blofin.com/api/v1/market/tickers'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                prices = {}
                for ticker in data.get('data', []):
                    if ticker['instId'] in self.trading_pairs:
                        prices[ticker['instId']] = {
                            'price': float(ticker.get('last', 0)),
                            'volume_24h': float(ticker.get('volCcy24h', 0))
                        }
                return prices
        except Exception as e:
            logging.warning(f"Error fetching market data: {e}")
        return None
    
    def fetch_ohlcv(self, pair, timeframe='1h', limit=24):
        """Fetch OHLCV data from Blofin for VWAP calculation"""
        try:
            url = f'https://openapi.blofin.com/api/v1/market/candles'
            params = {'instId': pair, 'bar': timeframe, 'limit': limit}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                candles = response.json().get('data', [])
                return [(float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])) for c in candles]  # o, h, l, c, v
        except Exception as e:
            logging.warning(f"Error fetching OHLCV for {pair}: {e}")
        return []
    
    def calculate_vwap(self, pair):
        """Calculate VWAP over 24-hour rolling window"""
        candles = self.fetch_ohlcv(pair, timeframe='1h', limit=24)
        if not candles or len(candles) < 2:
            return None
        
        # VWAP = sum(price * volume) / sum(volume)
        # Use close price as typical price
        pv_sum = sum(candle[3] * candle[4] for candle in candles)  # close * volume
        volume_sum = sum(candle[4] for candle in candles)
        
        if volume_sum == 0:
            return None
        
        vwap = pv_sum / volume_sum
        return vwap
    
    def calculate_rsi(self, pair, period=14):
        """Calculate RSI(14) from recent price data"""
        candles = self.fetch_ohlcv(pair, timeframe='1h', limit=period + 2)
        if not candles or len(candles) < period + 1:
            return None
        
        closes = [c[3] for c in candles]  # close prices
        deltas = [closes[i+1] - closes[i] for i in range(len(closes) - 1)]
        
        gains = sum(max(d, 0) for d in deltas[-period:]) / period
        losses = sum(abs(min(d, 0)) for d in deltas[-period:]) / period
        
        if losses == 0:
            return 100 if gains > 0 else 0
        
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def check_entry_conditions(self, pair, current_price, vwap, rsi):
        """Check if entry conditions are met"""
        if pair in self.positions:
            return False, None  # Already have position
        
        if vwap is None or rsi is None:
            return False, None
        
        # Price drops >0.8% below VWAP AND RSI <40
        price_below_vwap = (vwap - current_price) / vwap
        
        if price_below_vwap > self.vwap_threshold and rsi < self.rsi_entry_threshold:
            return True, f"VWAP: ${vwap:.2f}, Price: ${current_price:.2f} ({price_below_vwap*100:.2f}% below), RSI: {rsi:.1f}"
        
        return False, None
    
    def check_exit_conditions(self, pair, current_price, vwap):
        """Check if exit conditions are met"""
        if pair not in self.positions:
            return False, None
        
        position = self.positions[pair]
        entry_price = position['entry_price']
        
        if vwap is None:
            return False, None
        
        # Exit 1: Price within 0.1% of VWAP
        price_distance_to_vwap = abs(current_price - vwap) / vwap
        if price_distance_to_vwap < self.exit_profit_threshold:
            return True, f"Price within 0.1% of VWAP (${current_price:.2f} vs ${vwap:.2f})"
        
        # Exit 2: Stop loss at 1.5% below entry
        loss_pct = (entry_price - current_price) / entry_price
        if loss_pct > self.stop_loss_pct:
            return True, f"Stop loss hit: {loss_pct*100:.2f}% below entry (${entry_price:.2f})"
        
        return False, None
    
    def open_position(self, pair, entry_price):
        """Open a new position"""
        if pair in self.positions:
            return False
        
        if len(self.positions) >= self.max_positions:
            return False
        
        # Calculate position size: 40% of available capital
        position_size = self.balances[pair] * self.position_size_ratio
        amount = position_size / entry_price if entry_price > 0 else 0
        
        self.positions[pair] = {
            'entry_price': entry_price,
            'entry_amount': amount,
            'entry_time': datetime.now().isoformat()
        }
        
        self.balances[pair] -= position_size
        
        logging.info(f"BUY {pair} | Entry: ${entry_price:.2f} | Amount: {amount:.6f} | Position size: ${position_size:.2f} | Balance: ${self.balances[pair]:.2f}")
        return True
    
    def close_position(self, pair, exit_price, reason):
        """Close an open position"""
        if pair not in self.positions:
            return False
        
        position = self.positions[pair]
        entry_price = position['entry_price']
        entry_amount = position['entry_amount']
        
        # Calculate PnL
        revenue = entry_amount * exit_price
        cost = entry_amount * entry_price
        pnl = revenue - cost
        
        self.balances[pair] += revenue
        self.pnl_by_pair[pair] += pnl
        
        trade_log = {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'amount': entry_amount,
            'pnl': pnl,
            'reason': reason,
            'balance': self.balances[pair]
        }
        self.trades.append(trade_log)
        
        del self.positions[pair]
        
        pnl_sign = "✅" if pnl > 0 else "❌"
        logging.info(f"{pnl_sign} SELL {pair} | Exit: ${exit_price:.2f} | PnL: ${pnl:.2f} ({pnl/cost*100:+.2f}%) | Reason: {reason} | Balance: ${self.balances[pair]:.2f}")
        return True
    
    def run_cycle(self):
        """Execute one trading cycle"""
        market_data = self.fetch_market_data()
        if not market_data:
            logging.warning("Could not fetch market data, skipping cycle")
            return False
        
        for pair in self.trading_pairs:
            if pair not in market_data:
                continue
            
            current_price = market_data[pair]['price']
            vwap = self.calculate_vwap(pair)
            rsi = self.calculate_rsi(pair)
            
            # Check exit conditions first
            if pair in self.positions:
                should_exit, reason = self.check_exit_conditions(pair, current_price, vwap)
                if should_exit:
                    self.close_position(pair, current_price, reason)
            
            # Check entry conditions
            should_enter, reason = self.check_entry_conditions(pair, current_price, vwap, rsi)
            if should_enter:
                self.open_position(pair, current_price)
                logging.info(f"↓ ENTRY signal for {pair}: {reason}")
        
        return True
    
    def report(self):
        """Generate performance report"""
        total_balance = sum(self.balances.values())
        total_pnl = sum(self.pnl_by_pair.values())
        open_positions_count = len(self.positions)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_trades': len(self.trades),
            'open_positions': open_positions_count,
            'total_balance': round(total_balance, 2),
            'total_pnl': round(total_pnl, 2),
            'pnl_by_pair': {pair: round(self.pnl_by_pair[pair], 2) for pair in self.trading_pairs},
            'balances_by_pair': {pair: round(self.balances[pair], 2) for pair in self.trading_pairs},
            'recent_trades': self.trades[-3:] if self.trades else [],
            'open_positions': {pair: self.positions[pair] for pair in self.positions}
        }
        
        logging.info(f"Report: {json.dumps(report, indent=2)}")
        return report


if __name__ == '__main__':
    bot = VWAPReversionBot()
    logging.info("Starting VWAP Reversion Bot (paper trading mode)")
    
    while True:
        try:
            bot.run_cycle()
            bot.report()
            time.sleep(bot.config.get('update_interval', 300))
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"Cycle error: {e}", exc_info=True)
            time.sleep(60)
