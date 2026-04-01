# TradeBot Hub - Setup Guide

## What You're Getting

5 autonomous trading bots running in parallel:
1. **Momentum** — Buy uptrends, sell momentum loss
2. **Mean Reversion** — Trade RSI extremes
3. **Grid** — Profit from oscillations
4. **Scalp** — Rapid 1-5min micro trades
5. **Swing** — 4-24hr holds for 2-5% moves

**Total Capital:** $500 (paper trading) | **Per Strategy:** $100

---

## Prerequisites

### 1. Install Python 3.8+
```bash
python3 --version  # Should be 3.8 or higher
```

### 2. Install CCXT (Exchange API Library)
```bash
pip3 install ccxt
```

### 3. Choose Your Exchange & Get API Keys

#### Option A: Binance Testnet (Recommended)
1. Go to https://testnet.binance.vision
2. Sign up (or login if you have a regular Binance account)
3. Generate API key and secret
4. Copy the key and secret

#### Option B: Bybit Testnet
1. Go to https://testnet.bybit.com
2. Sign up for testnet
3. Create API key in Settings → API Management
4. Copy the key and secret

---

## Configuration

### 1. Update API Credentials
Edit `config.json` and replace:
```json
"api_keys": {
  "key": "YOUR_API_KEY_HERE",
  "secret": "YOUR_API_SECRET_HERE"
}
```

### 2. Choose Your Exchange
In `config.json`:
```json
"exchange": "binance",  // or "bybit"
"testnet": true         // Always true for paper trading
```

### 3. Adjust Trading Pairs (Optional)
```json
"trading_pairs": ["BTC/USDT", "ETH/USDT"]
```

---

## Running the Bots

### 1. Make the Script Executable
```bash
chmod +x run_all_bots.sh
```

### 2. Start All 5 Bots
```bash
./run_all_bots.sh
```

**You should see:**
```
🚀 Starting TradeBot Hub...
Total Capital: $500 (5 strategies × $100)

📊 Launching Momentum Bot...
📊 Launching Mean Reversion Bot...
📊 Launching Grid Trading Bot...
📊 Launching Scalping Bot...
📊 Launching Swing Trading Bot...

✅ All bots running. Logs in: ./logs
Hub dashboard: http://localhost:5000
```

### 3. Monitor in Real-Time
```bash
# Watch all logs simultaneously
tail -f logs/*.log

# Watch a specific bot
tail -f logs/momentum.log
```

### 4. Stop All Bots
Press `Ctrl+C` in the terminal running `run_all_bots.sh`

---

## Understanding the Logs

Each bot logs:
- **Trades executed** — Entry/exit prices and amounts
- **PnL tracking** — Real-time profit/loss
- **Signals** — When buy/sell conditions are triggered
- **Errors** — API or logic issues

Example log line:
```
2026-03-31 18:15:22 - MOMENTUM - INFO - BUY 0.0015 BTC/USDT @ $68124.50 | Balance: $50.23 | PnL: $2.14
```

---

## What Data Gets Collected

Each bot saves:
- **trades.json** — Complete trade history with entry/exit prices
- **performance.json** — Daily PnL, win rates, best/worst trades

Used to:
1. Find which strategy performs best
2. Identify patterns in market conditions
3. Build the real-money alert algorithm later

---

## Next Steps

### Week 1-2: Gather Data
- Run all 5 bots simultaneously
- Let them trade through different market conditions
- Collect 50-100 trades per strategy

### Week 3: Analyze
- Review which bot had highest win rate
- Look for patterns (times of day, market conditions)
- Identify pairs that trade best

### Week 4: Build Alert Bot
- Create a "best performer" bot
- Generate alerts when trade signals appear
- Prepare for real-money deployment

---

## Troubleshooting

### Bots Won't Start
```bash
# Check Python is installed
python3 --version

# Check CCXT is installed
python3 -c "import ccxt; print(ccxt.__version__)"

# If missing:
pip3 install ccxt
```

### API Key Errors
```
ERROR - Failed to initialize exchange
```
- Double-check key and secret are correct
- Make sure testnet is enabled
- Check exchange IP whitelist (allow your IP)

### No Trades Executing
- Market may be too quiet (low volatility)
- Bots are waiting for correct conditions
- Check logs for "Scanning" messages — these mean bot is active

### Logs Growing Too Large
```bash
# Clear old logs
rm logs/*.log

# Logs auto-clear every 7 days
```

---

## Performance Targets

**Paper Trading Expectations:**
- **Momentum:** 35-45% win rate
- **Mean Reversion:** 40-50% win rate
- **Grid:** 55-65% win rate (oscillation profit)
- **Scalping:** 50-60% win rate (volume-dependent)
- **Swing:** 45-55% win rate (trend-dependent)

**Combined portfolio:** Aiming for 45-50% overall win rate on paper.

Real money comes later once one strategy proves consistently profitable.

---

## Questions?

Check logs for detailed error messages. Each bot reports what it's doing and why.
