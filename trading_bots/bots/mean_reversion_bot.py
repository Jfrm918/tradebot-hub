#!/usr/bin/env python3
"""
Mean Reversion Trading Bot
Identifies overbought/oversold conditions using RSI, enters on extremes, exits on reversion
"""

import json
import time
import logging
from datetime import datetime
import ccxt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MEAN_REVERSION - %(levelname)s - %(message)s'
)

class MeanReversionBot:
    def __init__(self, config_path='/Users/jfrm918/.openclaw/workspace/trading_bots/config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.strategy = self.config['strategies']['mean_reversion']
        self.capital = self.strategy['capital']
        self.exchange = self._init_exchange()
        self.trades = []
        self.balance = self.capital
        self.pnl = 0
        self.position_rsi = None
        
        logging.info(f"Mean Reversion Bot initialized | Capital: ${self.capital}")
    
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
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        if len(prices) < period:
            return None
        
        deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
        gains = sum([d for d in deltas[-period:] if d > 0]) / period
        losses = sum([abs(d) for d in deltas[-period:] if d < 0]) / period
        
        if losses == 0:
            return 100 if gains > 0 else 0
        
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _is_oversold(self, rsi, threshold=30):
        return rsi is not None and rsi < threshold
    
    def _is_overbought(self, rsi, threshold=70):
        return rsi is not None and rsi > threshold
    
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
        
        logging.info(f"{action} {amount:.4f} {pair} @ ${price:.2f} | RSI: {self.position_rsi:.1f} | PnL: ${self.pnl:.2f}")
        return trade
    
    def run(self):
        if not self.exchange:
            logging.error("Cannot run without exchange connection")
            return
        
        try:
            for pair in self.config['trading_pairs']:
                try:
                    ohlcv = self.exchange.fetch_ohlcv(pair, '1h', limit=50)
                    prices = [o[4] for o in ohlcv]
                    
                    rsi = self._calculate_rsi(prices)
                    self.position_rsi = rsi
                    
                    current_price = prices[-1]
                    
                    # Entry on oversold
                    if self._is_oversold(rsi):
                        amount = (self.capital * 0.5) / current_price
                        self.execute_trade(pair, 'BUY', current_price, amount)
                        logging.info(f"✅ OVERSOLD entry on {pair} (RSI: {rsi:.1f})")
                    
                    # Exit on overbought or reversion
                    if self._is_overbought(rsi) and len(self.trades) > 0:
                        last_buy = [t for t in self.trades if t['action'] == 'BUY'][-1]
                        if last_buy not in [t for t in self.trades if t['action'] == 'SELL']:
                            self.execute_trade(pair, 'SELL', current_price, last_buy['amount'])
                            logging.info(f"✅ OVERBOUGHT exit on {pair} (RSI: {rsi:.1f})")
                
                except Exception as e:
                    logging.warning(f"Error processing {pair}: {e}")
        
        except Exception as e:
            logging.error(f"Bot error: {e}")
    
    def report(self):
        wins = len([t for t in self.trades if t['action'] == 'SELL'])
        report = {
            'strategy': 'Mean Reversion',
            'total_trades': len(self.trades),
            'completed_pairs': wins,
            'pnl': f"${self.pnl:.2f}",
            'balance': f"${self.balance:.2f}",
            'recent_trades': self.trades[-5:]
        }
        logging.info(f"Report: {json.dumps(report, indent=2)}")
        return report

if __name__ == '__main__':
    bot = MeanReversionBot()
    while True:
        try:
            bot.run()
            time.sleep(300)
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(60)
