#!/usr/bin/env python3
"""
Scalping Bot
Rapid entry/exit trades on 1-5 minute charts targeting 0.5-2% gains
"""

import json
import time
import logging
from datetime import datetime
import ccxt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SCALP - %(levelname)s - %(message)s'
)

class ScalpBot:
    def __init__(self, config_path='/Users/jfrm918/.openclaw/workspace/trading_bots/config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.strategy = self.config['strategies']['scalping']
        self.capital = self.strategy['capital']
        self.exchange = self._init_exchange()
        self.trades = []
        self.balance = self.capital
        self.pnl = 0
        self.profit_target = 0.015  # 1.5% target
        self.stop_loss = 0.005     # 0.5% stop loss
        
        logging.info(f"Scalping Bot initialized | Capital: ${self.capital} | Target: {self.profit_target*100:.1f}%")
    
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
    
    def _calculate_volatility(self, prices, period=5):
        """Quick volatility check for pair selection"""
        if len(prices) < period:
            return 0
        changes = [abs(prices[i+1] - prices[i]) / prices[i] for i in range(len(prices)-period, len(prices)-1)]
        return sum(changes) / len(changes)
    
    def execute_trade(self, pair, action, price, amount):
        trade = {
            'timestamp': datetime.now().isoformat(),
            'pair': pair,
            'action': action,
            'price': price,
            'amount': amount,
            'cost': price * amount
        }
        self.trades.append(trade)
        
        if action == 'BUY':
            self.balance -= trade['cost']
        else:
            self.balance += trade['cost']
            if len(self.trades) > 1:
                self.pnl += trade['cost'] - self.trades[-2]['cost']
        
        logging.info(f"{action} {amount:.6f} {pair} @ ${price:.4f} | PnL: ${self.pnl:.4f}")
        return trade
    
    def run(self):
        if not self.exchange:
            logging.error("Cannot run without exchange connection")
            return
        
        try:
            for pair in self.config['trading_pairs']:
                try:
                    # Fetch 1-minute candles
                    ohlcv = self.exchange.fetch_ohlcv(pair, '1m', limit=10)
                    prices = [o[4] for o in ohlcv]
                    
                    volatility = self._calculate_volatility(prices)
                    current_price = prices[-1]
                    
                    # Only trade volatile pairs
                    if volatility > 0.001:  # 0.1% volatility threshold
                        # Entry: price spike
                        if current_price > prices[-2] * 1.002:  # 0.2% move up
                            amount = (self.capital * 0.3) / current_price
                            entry_price = current_price
                            self.execute_trade(pair, 'BUY', entry_price, amount)
                            
                            # Exit conditions
                            profit_price = entry_price * (1 + self.profit_target)
                            stop_price = entry_price * (1 - self.stop_loss)
                            
                            # Simulate fill
                            if current_price >= profit_price:
                                self.execute_trade(pair, 'SELL', profit_price, amount)
                                logging.info(f"✅ SCALP win on {pair} | +{self.profit_target*100:.1f}%")
                            elif current_price <= stop_price:
                                self.execute_trade(pair, 'SELL', stop_price, amount)
                                logging.info(f"⚠️ SCALP stop on {pair}")
                
                except Exception as e:
                    logging.warning(f"Error processing {pair}: {e}")
        
        except Exception as e:
            logging.error(f"Bot error: {e}")
    
    def report(self):
        wins = len([t for t in self.trades if t['action'] == 'SELL' and self.pnl > 0])
        total = len([t for t in self.trades if t['action'] == 'SELL'])
        win_rate = (wins / total * 100) if total > 0 else 0
        
        report = {
            'strategy': 'Scalping',
            'total_trades': len(self.trades),
            'win_rate': f"{win_rate:.1f}%",
            'pnl': f"${self.pnl:.4f}",
            'balance': f"${self.balance:.4f}",
            'recent_trades': self.trades[-5:]
        }
        logging.info(f"Report: {json.dumps(report, indent=2)}")
        return report

if __name__ == '__main__':
    bot = ScalpBot()
    while True:
        try:
            bot.run()
            time.sleep(30)  # Rapid updates for scalping
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(10)
