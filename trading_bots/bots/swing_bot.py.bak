#!/usr/bin/env python3
"""
Swing Trading Bot
4-24 hour holds targeting 2-5% moves using support/resistance and trend
"""

import json
import time
import logging
from datetime import datetime
import ccxt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SWING - %(levelname)s - %(message)s'
)

class SwingBot:
    def __init__(self, config_path='../config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.strategy = self.config['strategies']['swing_trading']
        self.capital = self.strategy['capital']
        self.exchange = self._init_exchange()
        self.trades = []
        self.balance = self.capital
        self.pnl = 0
        self.positions = {}
        
        logging.info(f"Swing Trading Bot initialized | Capital: ${self.capital}")
    
    def _init_exchange(self):
        try:
            exchange_class = getattr(ccxt, self.config['exchange'])
            exchange = exchange_class({
                'apiKey': self.config['api_keys']['key'],
                'secret': self.config['api_keys']['secret'],
                'enableRateLimit': True,
                'test': self.config['testnet'],
            })
            logging.info(f"Connected to {self.config['exchange']} testnet")
            return exchange
        except Exception as e:
            logging.error(f"Failed to initialize exchange: {e}")
            return None
    
    def _find_support_resistance(self, prices, window=20):
        """Find support and resistance levels"""
        recent = prices[-window:]
        support = min(recent)
        resistance = max(recent)
        return support, resistance
    
    def _identify_trend(self, prices):
        """Identify uptrend or downtrend"""
        ma_short = sum(prices[-5:]) / 5
        ma_long = sum(prices[-20:]) / 20
        return 'UP' if ma_short > ma_long else 'DOWN'
    
    def execute_trade(self, pair, action, price, amount):
        trade = {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'action': action,
            'price': price,
            'amount': amount,
            'cost': price * amount,
            'hold_time': None
        }
        self.trades.append(trade)
        
        if action == 'BUY':
            self.balance -= trade['cost']
            self.positions[pair] = {
                'entry_price': price,
                'amount': amount,
                'entry_time': datetime.now(),
                'target': price * 1.03  # 3% target
            }
        else:
            self.balance += trade['cost']
            if pair in self.positions:
                hold_time = (datetime.now() - self.positions[pair]['entry_time']).total_seconds() / 3600
                trade['hold_time'] = f"{hold_time:.1f}h"
                del self.positions[pair]
            
            if len(self.trades) > 1:
                self.pnl += trade['cost'] - self.trades[-2]['cost']
        
        logging.info(f"{action} {amount:.4f} {pair} @ ${price:.2f} | PnL: ${self.pnl:.2f}")
        return trade
    
    def run(self):
        if not self.exchange:
            logging.error("Cannot run without exchange connection")
            return
        
        try:
            for pair in self.config['trading_pairs']:
                try:
                    # Fetch daily candles for swing trading
                    ohlcv = self.exchange.fetch_ohlcv(pair, '1d', limit=30)
                    prices = [o[4] for o in ohlcv]
                    
                    current_price = prices[-1]
                    support, resistance = self._find_support_resistance(prices)
                    trend = self._identify_trend(prices)
                    
                    # Entry: uptrend near support
                    if trend == 'UP' and current_price <= support * 1.01 and pair not in self.positions:
                        amount = (self.capital * 0.4) / current_price
                        self.execute_trade(pair, 'BUY', current_price, amount)
                        logging.info(f"✅ SWING entry on {pair} | Trend: {trend} | Support: ${support:.2f}")
                    
                    # Exit: hit target or hit resistance
                    if pair in self.positions:
                        position = self.positions[pair]
                        if current_price >= position['target']:
                            self.execute_trade(pair, 'SELL', current_price, position['amount'])
                            logging.info(f"✅ SWING target hit on {pair} | +3.0%")
                        elif current_price >= resistance:
                            self.execute_trade(pair, 'SELL', current_price, position['amount'])
                            logging.info(f"✅ SWING resistance exit on {pair}")
                
                except Exception as e:
                    logging.warning(f"Error processing {pair}: {e}")
        
        except Exception as e:
            logging.error(f"Bot error: {e}")
    
    def report(self):
        wins = len([t for t in self.trades if t['action'] == 'SELL' and self.pnl > 0])
        total = len([t for t in self.trades if t['action'] == 'SELL'])
        win_rate = (wins / total * 100) if total > 0 else 0
        avg_hold = sum([float(t['hold_time'].rstrip('h')) for t in self.trades if t['hold_time']]) / max(1, len([t for t in self.trades if t['hold_time']])) if total > 0 else 0
        
        report = {
            'strategy': 'Swing Trading',
            'total_trades': len(self.trades),
            'win_rate': f"{win_rate:.1f}%",
            'avg_hold_hours': f"{avg_hold:.1f}h",
            'pnl': f"${self.pnl:.2f}",
            'balance': f"${self.balance:.2f}",
            'open_positions': len(self.positions)
        }
        logging.info(f"Report: {json.dumps(report, indent=2)}")
        return report

if __name__ == '__main__':
    bot = SwingBot()
    while True:
        try:
            bot.run()
            time.sleep(3600)  # Daily updates
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(300)
