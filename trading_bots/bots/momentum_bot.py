#!/usr/bin/env python3
"""
Momentum Trading Bot
Buys on uptrend confirmation, sells on momentum loss
"""

import json
import time
import logging
from datetime import datetime
import ccxt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MOMENTUM - %(levelname)s - %(message)s'
)

class MomentumBot:
    def __init__(self, config_path='../config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.strategy = self.config['strategies']['momentum']
        self.capital = self.strategy['capital']
        self.exchange = self._init_exchange()
        self.trades = []
        self.balance = self.capital
        self.pnl = 0
        
        logging.info(f"Momentum Bot initialized | Capital: ${self.capital}")
    
    def _init_exchange(self):
        """Initialize exchange connection (Binance testnet)"""
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
    
    def _detect_uptrend(self, ticker_data):
        """Detect uptrend using simple moving average"""
        if len(ticker_data) < 20:
            return False
        prices = [t['close'] for t in ticker_data[-20:]]
        ma_short = sum(prices[-5:]) / 5
        ma_long = sum(prices) / 20
        return ma_short > ma_long
    
    def _detect_momentum_loss(self, ticker_data):
        """Detect momentum loss using price change velocity"""
        if len(ticker_data) < 5:
            return False
        recent = [t['close'] for t in ticker_data[-5:]]
        momentum = sum([recent[i+1] - recent[i] for i in range(4)]) / 4
        return momentum < 0
    
    def execute_trade(self, pair, action, price, amount):
        """Log and execute trade"""
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
        else:  # SELL
            self.balance += trade['cost']
            self.pnl += trade['cost'] - (self.trades[-2]['cost'] if len(self.trades) > 1 else 0)
        
        logging.info(f"{action} {amount} {pair} @ ${price} | Balance: ${self.balance:.2f} | PnL: ${self.pnl:.2f}")
        return trade
    
    def run(self):
        """Main bot loop"""
        if not self.exchange:
            logging.error("Cannot run without exchange connection")
            return
        
        try:
            for pair in self.config['trading_pairs']:
                logging.info(f"Scanning {pair} for momentum trades...")
                
                try:
                    # Fetch OHLCV data
                    ohlcv = self.exchange.fetch_ohlcv(pair, '1h', limit=50)
                    ticker_data = [{'close': o[4]} for o in ohlcv]
                    
                    # Check for entry signal
                    if self._detect_uptrend(ticker_data):
                        amount = (self.capital * 0.5) / ticker_data[-1]['close']
                        self.execute_trade(pair, 'BUY', ticker_data[-1]['close'], amount)
                        logging.info(f"✅ BUY signal on {pair}")
                    
                    # Check for exit signal
                    if len(self.trades) > 0 and self._detect_momentum_loss(ticker_data):
                        last_buy = [t for t in self.trades if t['action'] == 'BUY'][-1]
                        self.execute_trade(pair, 'SELL', ticker_data[-1]['close'], last_buy['amount'])
                        logging.info(f"✅ SELL signal on {pair}")
                
                except Exception as e:
                    logging.warning(f"Error processing {pair}: {e}")
        
        except Exception as e:
            logging.error(f"Bot error: {e}")
    
    def report(self):
        """Generate performance report"""
        wins = len([t for t in self.trades if t['action'] == 'SELL' and self.pnl > 0])
        total = len([t for t in self.trades if t['action'] == 'SELL'])
        win_rate = (wins / total * 100) if total > 0 else 0
        
        report = {
            'strategy': 'Momentum Trading',
            'total_trades': len(self.trades),
            'win_rate': f"{win_rate:.1f}%",
            'pnl': f"${self.pnl:.2f}",
            'balance': f"${self.balance:.2f}",
            'trades': self.trades[-10:]  # Last 10 trades
        }
        
        logging.info(f"Report: {json.dumps(report, indent=2)}")
        return report

if __name__ == '__main__':
    bot = MomentumBot()
    
    # Run continuously
    while True:
        try:
            bot.run()
            time.sleep(300)  # Update every 5 minutes
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(60)  # Wait before retrying
