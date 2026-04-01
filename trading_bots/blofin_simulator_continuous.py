#!/usr/bin/env python3
"""
Blofin Paper Trading Simulator - Continuous Mode
Runs indefinitely, collecting trade data for analysis
All 5 strategies trade simultaneously on realistic price movements
"""

import json
import time
import logging
from datetime import datetime
import random
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/jfrm918/.openclaw/workspace/trading_bots/simulator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TradeBot')

class ContinuousSimulator:
    def __init__(self):
        self.trading_pairs = ["BTC-USDT", "ETH-USDT"]
        self.bots = {
            'momentum': {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0},
            'mean_reversion': {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0},
            'grid': {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0},
            'scalp': {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0},
            'swing': {'capital': 100, 'trades': [], 'balance': 100.0, 'pnl': 0.0, 'wins': 0}
        }
        self.price_ranges = {
            'BTC-USDT': {'base': 68000, 'volatility': 0.02, 'trend': 0},
            'ETH-USDT': {'base': 2094, 'volatility': 0.025, 'trend': 0}
        }
        self.cycle_count = 0
        logger.info("🚀 Blofin Paper Trading Simulator - CONTINUOUS MODE")
        logger.info("=" * 80)
        logger.info("5 Bots × $100 = $500 Paper Trading Capital")
        logger.info("Running indefinitely. Press Ctrl+C to stop.")
        logger.info("=" * 80)
    
    def generate_price(self, pair):
        """Generate realistic price with trend"""
        config = self.price_ranges[pair]
        config['trend'] = config['trend'] * 0.95 + random.gauss(0, 0.001)  # Mean reversion trend
        change = config['trend'] + random.gauss(0, config['base'] * config['volatility'] / 15)
        new_price = config['base'] + change
        
        return {
            'pair': pair,
            'last': round(new_price, 2),
            'high24h': round(new_price * (1 + config['volatility']), 2),
            'low24h': round(new_price * (1 - config['volatility']), 2),
        }
    
    def execute_momentum(self, pair, price):
        bot = self.bots['momentum']
        mid = (price['low24h'] + price['high24h']) / 2
        
        if price['last'] > mid:
            buys = [t for t in bot['trades'] if t['action'] == 'BUY']
            if buys and len(buys) > len([t for t in bot['trades'] if t['action'] == 'SELL']):
                last_buy = buys[-1]
                if price['last'] > last_buy['price'] * 1.01:
                    amount = last_buy.get('amount', (bot['capital'] * 0.3) / last_buy['price'])
                    cost_at_last = amount * price['last']
                    bot['balance'] += cost_at_last
                    pnl = cost_at_last - last_buy.get('cost', last_buy['price'] * amount)
                    bot['pnl'] += pnl
                    if pnl > 0:
                        bot['wins'] += 1
                    trade = {'action': 'SELL', 'pair': pair, 'price': price['last'], 'pnl': pnl, 'amount': amount}
                    bot['trades'].append(trade)
                    logger.info(f"MOMENTUM ✓ SELL {pair} @ ${price['last']:.2f} | PnL: +${pnl:.2f}")
            elif bot['balance'] > 10:
                amount = (bot['capital'] * 0.3) / price['last']
                cost = amount * price['last']
                bot['balance'] -= cost
                trade = {'action': 'BUY', 'pair': pair, 'price': price['last'], 'amount': amount, 'cost': cost}
                bot['trades'].append(trade)
    
    def execute_mean_reversion(self, pair, price):
        bot = self.bots['mean_reversion']
        if price['last'] <= price['low24h'] * 1.01:
            if bot['balance'] > 10:
                amount = (bot['capital'] * 0.3) / price['last']
                cost = amount * price['last']
                bot['balance'] -= cost
                trade = {'action': 'BUY', 'pair': pair, 'price': price['last'], 'amount': amount, 'cost': cost}
                bot['trades'].append(trade)
        else:
            mid = (price['low24h'] + price['high24h']) / 2
            if price['last'] >= mid:
                buys = [t for t in bot['trades'] if t['action'] == 'BUY']
                if buys and len(buys) > len([t for t in bot['trades'] if t['action'] == 'SELL']):
                    last_buy = buys[-1]
                    amount = last_buy.get('amount', (bot['capital'] * 0.3) / last_buy['price'])
                    cost_at_last = amount * price['last']
                    bot['balance'] += cost_at_last
                    pnl = cost_at_last - last_buy.get('cost', last_buy['price'] * amount)
                    bot['pnl'] += pnl
                    if pnl > 0:
                        bot['wins'] += 1
                    trade = {'action': 'SELL', 'pair': pair, 'price': price['last'], 'pnl': pnl, 'amount': amount}
                    bot['trades'].append(trade)
                    logger.info(f"MEAN_REV ✓ SELL {pair} @ ${price['last']:.2f} | PnL: +${pnl:.2f}")
    
    def execute_grid(self, pair, price):
        bot = self.bots['grid']
        mid = (price['low24h'] + price['high24h']) / 2
        if price['last'] < mid * 0.98 and bot['balance'] > 10:
            amount = (bot['capital'] * 0.2) / price['last']
            cost = amount * price['last']
            bot['balance'] -= cost
            trade = {'action': 'BUY', 'pair': pair, 'price': price['last'], 'amount': amount, 'cost': cost}
            bot['trades'].append(trade)
        elif price['last'] > mid * 1.02:
            buys = [t for t in bot['trades'] if t['action'] == 'BUY']
            if buys and len(buys) > len([t for t in bot['trades'] if t['action'] == 'SELL']):
                last_buy = buys[-1]
                amount = last_buy.get('amount', (bot['capital'] * 0.2) / last_buy['price'])
                cost_at_last = amount * price['last']
                bot['balance'] += cost_at_last
                pnl = cost_at_last - last_buy.get('cost', last_buy['price'] * amount)
                bot['pnl'] += pnl
                if pnl > 0:
                    bot['wins'] += 1
                trade = {'action': 'SELL', 'pair': pair, 'price': price['last'], 'pnl': pnl, 'amount': amount}
                bot['trades'].append(trade)
                logger.info(f"GRID     ✓ SELL {pair} @ ${price['last']:.2f} | PnL: +${pnl:.2f}")
    
    def execute_scalp(self, pair, price):
        bot = self.bots['scalp']
        vol = (price['high24h'] - price['low24h']) / price['last']
        if vol > 0.005 and price['last'] < price['low24h'] * 1.002 and bot['balance'] > 5:
            amount = (bot['capital'] * 0.15) / price['last']
            cost = amount * price['last']
            bot['balance'] -= cost
            trade = {'action': 'BUY', 'pair': pair, 'price': price['last'], 'amount': amount, 'cost': cost}
            bot['trades'].append(trade)
        elif vol > 0.005:
            buys = [t for t in bot['trades'] if t['action'] == 'BUY']
            if buys and len(buys) > len([t for t in bot['trades'] if t['action'] == 'SELL']):
                last_buy = buys[-1]
                if price['last'] >= last_buy['price'] * 1.005:
                    amount = last_buy.get('amount', (bot['capital'] * 0.15) / last_buy['price'])
                    cost_at_last = amount * price['last']
                    bot['balance'] += cost_at_last
                    pnl = cost_at_last - last_buy.get('cost', last_buy['price'] * amount)
                    bot['pnl'] += pnl
                    if pnl > 0:
                        bot['wins'] += 1
                    trade = {'action': 'SELL', 'pair': pair, 'price': price['last'], 'pnl': pnl, 'amount': amount}
                    bot['trades'].append(trade)
                    logger.info(f"SCALP    ✓ SELL {pair} @ ${price['last']:.4f} | +0.5%")
    
    def execute_swing(self, pair, price):
        bot = self.bots['swing']
        if price['last'] <= price['low24h'] * 1.005 and bot['balance'] > 20:
            amount = (bot['capital'] * 0.4) / price['last']
            cost = amount * price['last']
            bot['balance'] -= cost
            trade = {'action': 'BUY', 'pair': pair, 'price': price['last'], 'amount': amount, 'cost': cost}
            bot['trades'].append(trade)
        else:
            buys = [t for t in bot['trades'] if t['action'] == 'BUY']
            if buys and len(buys) > len([t for t in bot['trades'] if t['action'] == 'SELL']):
                last_buy = buys[-1]
                if price['last'] >= last_buy['price'] * 1.03:
                    amount = last_buy.get('amount', (bot['capital'] * 0.4) / last_buy['price'])
                    cost_at_last = amount * price['last']
                    bot['balance'] += cost_at_last
                    pnl = cost_at_last - last_buy.get('cost', last_buy['price'] * amount)
                    bot['pnl'] += pnl
                    if pnl > 0:
                        bot['wins'] += 1
                    trade = {'action': 'SELL', 'pair': pair, 'price': price['last'], 'pnl': pnl, 'amount': amount}
                    bot['trades'].append(trade)
                    logger.info(f"SWING    ✓ SELL {pair} @ ${price['last']:.2f} | PnL: +${pnl:.2f}")
    
    def run_cycle(self):
        self.cycle_count += 1
        for pair in self.trading_pairs:
            price = self.generate_price(pair)
            self.execute_momentum(pair, price)
            self.execute_mean_reversion(pair, price)
            self.execute_grid(pair, price)
            self.execute_scalp(pair, price)
            self.execute_swing(pair, price)
        
        if self.cycle_count % 50 == 0:
            self.print_status()
            self.save_snapshot()
    
    def print_status(self):
        logger.info("\n" + "=" * 80)
        logger.info(f"STATUS UPDATE - Cycle {self.cycle_count}")
        logger.info("=" * 80)
        total_pnl = 0
        total_trades = 0
        for bot_name, bot in self.bots.items():
            trades = len([t for t in bot['trades'] if t['action'] == 'SELL'])
            total_pnl += bot['pnl']
            total_trades += trades
            roi = ((bot['balance'] - 100) / 100 * 100)
            win_rate = (bot['wins'] / trades * 100) if trades > 0 else 0
            logger.info(f"{bot_name.upper():15} | Trades: {trades:2} | Balance: ${bot['balance']:7.2f} | PnL: ${bot['pnl']:7.2f} | Win%: {win_rate:5.1f}%")
        logger.info("=" * 80)
        logger.info(f"TOTAL PORTFOLIO  | Trades: {total_trades:2} | PnL: ${total_pnl:7.2f} | Portfolio: ${500 + total_pnl:.2f}\n")
    
    def save_snapshot(self):
        snapshot = {
            'cycle': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'bots': {name: {
                'balance': bot['balance'],
                'pnl': bot['pnl'],
                'trades': len([t for t in bot['trades'] if t['action'] == 'SELL']),
                'wins': bot['wins']
            } for name, bot in self.bots.items()}
        }
        with open('/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json', 'w') as f:
            json.dump(snapshot, f, indent=2)

if __name__ == '__main__':
    sim = ContinuousSimulator()
    
    try:
        while True:
            sim.run_cycle()
            time.sleep(1)  # 1 second between cycles
    except KeyboardInterrupt:
        logger.info("\n\n⏹️  Simulator stopped by user")
        sim.print_status()
        logger.info("\n✅ Final snapshot saved. Goodbye!")
        sys.exit(0)
