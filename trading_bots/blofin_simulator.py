#!/usr/bin/env python3
"""
Blofin Paper Trading Simulator
Uses Blofin's public market API (no auth) + local virtual order book
All 5 strategies trade on real Blofin prices with fake capital
"""

import requests
import json
import time
import logging
from datetime import datetime
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SIMULATOR - %(levelname)s - %(message)s'
)

class BlofinSimulator:
    def __init__(self, total_capital=500):
        self.total_capital = total_capital
        self.blofin_api = "https://openapi.blofin.com/api/v1"
        self.trading_pairs = ["BTC-USDT", "ETH-USDT", "DOGE-USDT"]
        self.bots = {
            'momentum': {'capital': 100, 'trades': [], 'balance': 100, 'pnl': 0},
            'mean_reversion': {'capital': 100, 'trades': [], 'balance': 100, 'pnl': 0},
            'grid': {'capital': 100, 'trades': [], 'balance': 100, 'pnl': 0},
            'scalp': {'capital': 100, 'trades': [], 'balance': 100, 'pnl': 0},
            'swing': {'capital': 100, 'trades': [], 'balance': 100, 'pnl': 0}
        }
        self.market_data = {}
        logging.info(f"Blofin Simulator initialized | Total Capital: ${total_capital}")
    
    def fetch_blofin_prices(self):
        """Fetch real market data from Blofin public API"""
        try:
            url = f"{self.blofin_api}/market/tickers"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == '0':
                    prices = {}
                    for ticker in data['data']:
                        inst_id = ticker['instId']
                        prices[inst_id] = {
                            'last': float(ticker['last']),
                            'bid': float(ticker['bidPrice']),
                            'ask': float(ticker['askPrice']),
                            'high24h': float(ticker['high24h']),
                            'low24h': float(ticker['low24h']),
                            'timestamp': int(ticker['ts'])
                        }
                    self.market_data = prices
                    logging.info(f"✅ Fetched live prices from Blofin | Pairs: {len(prices)}")
                    return True
        except Exception as e:
            logging.warning(f"⚠️ Could not fetch live prices: {e}")
        
        return False
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI for mean reversion"""
        if len(prices) < period:
            return None
        deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
        gains = sum([d for d in deltas[-period:] if d > 0]) / period
        losses = sum([abs(d) for d in deltas[-period:] if d < 0]) / period
        if losses == 0:
            return 100 if gains > 0 else 0
        rs = gains / losses
        return 100 - (100 / (1 + rs))
    
    def execute_momentum_strategy(self, pair, price_data):
        """Momentum: Buy on price spike up"""
        bot = self.bots['momentum']
        if price_data['last'] > price_data['low24h'] * 1.02:  # 2% above low
            amount = (bot['capital'] * 0.3) / price_data['last']
            cost = amount * price_data['last']
            
            if bot['balance'] >= cost:
                bot['balance'] -= cost
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'action': 'BUY',
                    'price': price_data['last'],
                    'amount': amount,
                    'cost': cost
                }
                bot['trades'].append(trade)
                logging.info(f"MOMENTUM: BUY {amount:.6f} {pair} @ ${price_data['last']:.2f}")
                return True
        
        # Sell if in profit
        if len(bot['trades']) > 0:
            last_buy = [t for t in bot['trades'] if t['action'] == 'BUY'][-1]
            profit_target = last_buy['price'] * 1.015  # 1.5% profit
            if price_data['last'] >= profit_target:
                sell_cost = last_buy['amount'] * price_data['last']
                bot['balance'] += sell_cost
                bot['pnl'] += sell_cost - last_buy['cost']
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'action': 'SELL',
                    'price': price_data['last'],
                    'amount': last_buy['amount'],
                    'cost': sell_cost
                }
                bot['trades'].append(trade)
                logging.info(f"MOMENTUM: SELL {last_buy['amount']:.6f} {pair} @ ${price_data['last']:.2f} | PnL: ${bot['pnl']:.2f}")
                return True
        
        return False
    
    def execute_mean_reversion_strategy(self, pair, price_data):
        """Mean Reversion: Buy on dips (low24h proximity)"""
        bot = self.bots['mean_reversion']
        current_range = price_data['high24h'] - price_data['low24h']
        proximity_to_low = price_data['last'] - price_data['low24h']
        
        # Buy near daily low
        if proximity_to_low < (current_range * 0.2):  # In bottom 20% of range
            amount = (bot['capital'] * 0.3) / price_data['last']
            cost = amount * price_data['last']
            
            if bot['balance'] >= cost:
                bot['balance'] -= cost
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'action': 'BUY',
                    'price': price_data['last'],
                    'amount': amount,
                    'cost': cost
                }
                bot['trades'].append(trade)
                logging.info(f"MEAN_REV: BUY {amount:.6f} {pair} @ ${price_data['last']:.2f} (near low)")
                return True
        
        # Sell on recovery to midpoint
        if len(bot['trades']) > 0:
            last_buy = [t for t in bot['trades'] if t['action'] == 'BUY'][-1]
            midpoint = price_data['low24h'] + ((price_data['high24h'] - price_data['low24h']) / 2)
            if price_data['last'] >= midpoint:
                sell_cost = last_buy['amount'] * price_data['last']
                bot['balance'] += sell_cost
                bot['pnl'] += sell_cost - last_buy['cost']
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'action': 'SELL',
                    'price': price_data['last'],
                    'amount': last_buy['amount'],
                    'cost': sell_cost
                }
                bot['trades'].append(trade)
                logging.info(f"MEAN_REV: SELL {last_buy['amount']:.6f} {pair} @ ${price_data['last']:.2f} | PnL: ${bot['pnl']:.2f}")
                return True
        
        return False
    
    def execute_grid_strategy(self, pair, price_data):
        """Grid: Buy dips, sell rallies within range"""
        bot = self.bots['grid']
        mid = (price_data['high24h'] + price_data['low24h']) / 2
        
        # Buy 10% below mid
        if price_data['last'] < mid * 0.90:
            amount = (bot['capital'] * 0.15) / price_data['last']
            cost = amount * price_data['last']
            
            if bot['balance'] >= cost:
                bot['balance'] -= cost
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'action': 'BUY',
                    'price': price_data['last'],
                    'amount': amount,
                    'cost': cost
                }
                bot['trades'].append(trade)
                logging.info(f"GRID: BUY {amount:.6f} {pair} @ ${price_data['last']:.2f}")
                return True
        
        # Sell 10% above mid
        if len(bot['trades']) > 0 and price_data['last'] > mid * 1.10:
            last_buy = [t for t in bot['trades'] if t['action'] == 'BUY'][-1]
            sell_cost = last_buy['amount'] * price_data['last']
            bot['balance'] += sell_cost
            bot['pnl'] += sell_cost - last_buy['cost']
            trade = {
                'timestamp': datetime.now().isoformat(),
                'pair': pair,
                'action': 'SELL',
                'price': price_data['last'],
                'amount': last_buy['amount'],
                'cost': sell_cost
            }
            bot['trades'].append(trade)
            logging.info(f"GRID: SELL {last_buy['amount']:.6f} {pair} @ ${price_data['last']:.2f} | PnL: ${bot['pnl']:.2f}")
            return True
        
        return False
    
    def execute_scalp_strategy(self, pair, price_data):
        """Scalp: Micro trades chasing small moves"""
        bot = self.bots['scalp']
        volatility = (price_data['high24h'] - price_data['low24h']) / price_data['last']
        
        # Only scalp if volatile enough
        if volatility > 0.01:  # 1% range
            # Buy on small dips
            if price_data['last'] < price_data['low24h'] * 1.005:
                amount = (bot['capital'] * 0.2) / price_data['last']
                cost = amount * price_data['last']
                
                if bot['balance'] >= cost:
                    bot['balance'] -= cost
                    trade = {
                        'timestamp': datetime.now().isoformat(),
                        'pair': pair,
                        'action': 'BUY',
                        'price': price_data['last'],
                        'amount': amount,
                        'cost': cost
                    }
                    bot['trades'].append(trade)
                    logging.info(f"SCALP: BUY {amount:.6f} {pair} @ ${price_data['last']:.4f}")
                    return True
            
            # Sell for quick 0.5% gain
            if len(bot['trades']) > 0:
                last_buy = [t for t in bot['trades'] if t['action'] == 'BUY'][-1]
                if price_data['last'] >= last_buy['price'] * 1.005:
                    sell_cost = last_buy['amount'] * price_data['last']
                    bot['balance'] += sell_cost
                    bot['pnl'] += sell_cost - last_buy['cost']
                    trade = {
                        'timestamp': datetime.now().isoformat(),
                        'pair': pair,
                        'action': 'SELL',
                        'price': price_data['last'],
                        'amount': last_buy['amount'],
                        'cost': sell_cost
                    }
                    bot['trades'].append(trade)
                    logging.info(f"SCALP: SELL {last_buy['amount']:.6f} {pair} @ ${price_data['last']:.4f} | +0.5%")
                    return True
        
        return False
    
    def execute_swing_strategy(self, pair, price_data):
        """Swing: Hold for 24h+ targeting 2-5% moves"""
        bot = self.bots['swing']
        
        # Buy on dips
        if price_data['last'] <= price_data['low24h'] * 1.01:
            amount = (bot['capital'] * 0.4) / price_data['last']
            cost = amount * price_data['last']
            
            if bot['balance'] >= cost:
                bot['balance'] -= cost
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'action': 'BUY',
                    'price': price_data['last'],
                    'amount': amount,
                    'cost': cost
                }
                bot['trades'].append(trade)
                logging.info(f"SWING: BUY {amount:.6f} {pair} @ ${price_data['last']:.2f}")
                return True
        
        # Sell on rallies
        if len(bot['trades']) > 0:
            last_buy = [t for t in bot['trades'] if t['action'] == 'BUY'][-1]
            target = last_buy['price'] * 1.03  # 3% target
            if price_data['last'] >= target:
                sell_cost = last_buy['amount'] * price_data['last']
                bot['balance'] += sell_cost
                bot['pnl'] += sell_cost - last_buy['cost']
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'pair': pair,
                    'action': 'SELL',
                    'price': price_data['last'],
                    'amount': last_buy['amount'],
                    'cost': sell_cost
                }
                bot['trades'].append(trade)
                logging.info(f"SWING: SELL {last_buy['amount']:.6f} {pair} @ ${price_data['last']:.2f} | PnL: ${bot['pnl']:.2f}")
                return True
        
        return False
    
    def run_cycle(self):
        """Execute one trading cycle for all bots"""
        if not self.fetch_blofin_prices():
            logging.error("Could not fetch prices, skipping cycle")
            return
        
        for pair in self.trading_pairs:
            if pair in self.market_data:
                price_data = self.market_data[pair]
                
                # Execute all 5 strategies on this pair
                self.execute_momentum_strategy(pair, price_data)
                self.execute_mean_reversion_strategy(pair, price_data)
                self.execute_grid_strategy(pair, price_data)
                self.execute_scalp_strategy(pair, price_data)
                self.execute_swing_strategy(pair, price_data)
    
    def report(self):
        """Print performance summary"""
        logging.info("=" * 80)
        logging.info("PORTFOLIO SUMMARY")
        logging.info("=" * 80)
        
        total_pnl = 0
        total_trades = 0
        
        for bot_name, bot_data in self.bots.items():
            trades = len(bot_data['trades'])
            pnl = bot_data['pnl']
            balance = bot_data['balance']
            total_pnl += pnl
            total_trades += trades
            
            roi = ((balance - bot_data['capital']) / bot_data['capital'] * 100) if bot_data['capital'] > 0 else 0
            
            logging.info(f"{bot_name.upper():20} | Trades: {trades:3} | Balance: ${balance:7.2f} | PnL: ${pnl:7.2f} | ROI: {roi:6.1f}%")
        
        logging.info("=" * 80)
        logging.info(f"TOTAL PORTFOLIO   | Trades: {total_trades:3} | Total PnL: ${total_pnl:7.2f} | Portfolio Value: ${self.total_capital + total_pnl:.2f}")
        logging.info("=" * 80)
        
        # Save detailed logs
        self.save_logs()
    
    def save_logs(self):
        """Save trade logs to JSON"""
        logs = {
            'timestamp': datetime.now().isoformat(),
            'bots': self.bots
        }
        with open('simulator_logs.json', 'w') as f:
            json.dump(logs, f, indent=2)
        logging.info("✅ Trade logs saved to simulator_logs.json")

if __name__ == '__main__':
    simulator = BlofinSimulator(total_capital=500)
    
    logging.info("🚀 Starting Blofin Paper Trading Simulator")
    logging.info("Trading on REAL Blofin prices with virtual $500 capital")
    logging.info("")
    
    # Run for 10 cycles (can adjust)
    for cycle in range(10):
        logging.info(f"\n📊 Trading Cycle {cycle + 1}/10")
        simulator.run_cycle()
        time.sleep(30)  # Wait 30 seconds between cycles
    
    # Final report
    simulator.report()
    logging.info("\n✅ Simulation complete. Logs saved.")
