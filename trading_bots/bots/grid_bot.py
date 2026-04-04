#!/usr/bin/env python3
"""
Grid Trading Bot
Sets up buy/sell orders in a grid pattern on volatile pairs
"""

import json
import time
import logging
from datetime import datetime
import ccxt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - GRID - %(levelname)s - %(message)s'
)

class GridBot:
    def __init__(self, config_path='/Users/jfrm918/.openclaw/workspace/trading_bots/config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.strategy = self.config['strategies']['grid_trading']
        self.capital = self.strategy['capital']
        self.exchange = self._init_exchange()
        self.trades = []
        self.balance = self.capital
        self.pnl = 0
        self.grid_orders = {}
        
        logging.info(f"Grid Trading Bot initialized | Capital: ${self.capital}")
    
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
    
    def _create_grid(self, pair, current_price, grid_levels=5, grid_range=0.02):
        """Create buy/sell grid around current price"""
        grid = []
        step = (current_price * grid_range) / grid_levels
        
        for i in range(1, grid_levels + 1):
            buy_price = current_price - (step * i)
            sell_price = current_price + (step * i)
            grid.append({
                'buy': buy_price,
                'sell': sell_price,
                'level': i
            })
        
        return grid
    
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
        
        logging.info(f"{action} GRID {pair} Level | Price: ${price:.2f} | PnL: ${self.pnl:.2f}")
        return trade
    
    def run(self):
        if not self.exchange:
            logging.error("Cannot run without exchange connection")
            return
        
        try:
            for pair in self.config['trading_pairs']:
                try:
                    # Get current market price
                    ticker = self.exchange.fetch_ticker(pair)
                    current_price = ticker['last']
                    
                    # Create or update grid
                    if pair not in self.grid_orders:
                        grid = self._create_grid(pair, current_price)
                        self.grid_orders[pair] = grid
                        logging.info(f"Grid created for {pair} | Center: ${current_price:.2f}")
                    
                    grid = self.grid_orders[pair]
                    
                    # Simulate grid order fills based on current price
                    for level_order in grid:
                        # Buy fills
                        if current_price <= level_order['buy'] * 1.001:  # Allow 0.1% slippage
                            amount = (self.capital * 0.1) / level_order['buy']
                            self.execute_trade(pair, 'BUY', level_order['buy'], amount)
                        
                        # Sell fills (paired with buys)
                        if current_price >= level_order['sell'] * 0.999:
                            self.execute_trade(pair, 'SELL', level_order['sell'], amount if 'amount' in locals() else 0)
                
                except Exception as e:
                    logging.warning(f"Error processing {pair}: {e}")
        
        except Exception as e:
            logging.error(f"Bot error: {e}")
    
    def report(self):
        report = {
            'strategy': 'Grid Trading',
            'total_trades': len(self.trades),
            'active_grids': len(self.grid_orders),
            'pnl': f"${self.pnl:.2f}",
            'balance': f"${self.balance:.2f}",
            'recent_trades': self.trades[-5:]
        }
        logging.info(f"Report: {json.dumps(report, indent=2)}")
        return report

if __name__ == '__main__':
    bot = GridBot()
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
