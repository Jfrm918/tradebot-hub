# VWAP Momentum Bot (Bot 7) - Documentation

## Overview

The VWAP Momentum Bot is a sophisticated trading strategy that combines Volume-Weighted Average Price (VWAP) analysis with volume confirmation for high-probability entry signals. It trades BTC-USDT and ETH-USDT pairs on the Blofin exchange in paper trading mode.

## File Location

```
/Users/jfrm918/.openclaw/workspace/trading_bots/bots/vwap_momentum_bot.py
```

## Key Specifications

### Capital & Position Management
- **Starting Capital**: $100 simulated
- **Position Size**: 35% of available capital per trade
- **Max Open Positions**: 2 (one BTC, one ETH simultaneously)
- **Paper Trading Mode**: No real money at risk
- **Trading Pairs**: BTC-USDT, ETH-USDT

### VWAP Calculation
- **Rolling Window**: 24-hour (1440 minutes)
- **Formula**: VWAP = Σ(Price × Volume) / Σ(Volume)
- **Candle Timeframe**: 1-minute candles for rapid entry/exit

### Entry Conditions (ALL must be true)
1. **Price Breakout**: Current price > VWAP + 0.5%
2. **Volume Confirmation**: Current candle volume > 1.5x 20-period average volume
3. **Position Availability**: Fewer than 2 open positions
4. **Pair-Specific**: Only one BTC and one ETH position max

### Exit Conditions (ANY one triggers exit)
1. **VWAP Reversal**: Price closes below VWAP
2. **Take Profit**: Price reaches entry price + 2%
3. **Stop Loss**: Price drops below entry VWAP - 1%

## Core Components

### Class: VWAPMomentumBot

#### Key Attributes
- `capital` (float): Total starting capital ($100)
- `balance` (float): Current available cash
- `pnl` (float): Cumulative profit/loss from closed trades
- `open_positions` (dict): Active trades keyed by pair
- `closed_trades` (list): Historical completed trades with PnL
- `vwap_windows` (dict): 24-hour rolling VWAP data by pair
- `volume_windows` (dict): 20-period volume averages by pair

#### Key Methods

**`_calculate_vwap(pair)`**
- Returns weighted average price from 24-hour window
- Returns None if insufficient data

**`_get_avg_volume(pair)`**
- Calculates 20-period simple moving average of volume
- Used for volume confirmation threshold

**`_check_entry_signal(pair, price, volume)`**
- Evaluates both entry conditions
- Returns (bool, vwap) tuple

**`_check_exit_conditions(pair, price, vwap)`**
- Checks all three exit scenarios
- Returns reason string or None

**`_execute_buy(pair, price, vwap)`**
- Creates new position
- Records entry with VWAP snapshot
- Updates balance and logs with `open_position=True`

**`_execute_sell(pair, price, exit_reason)`**
- Closes position at market price
- Calculates PnL and win/loss percentage
- Logs with `open_position=False` and exit reason

**`_process_pair(pair)`**
- Single iteration: fetch candles, update windows, check signals
- Called for each trading pair

**`run()`**
- Main bot loop iteration
- Processes both pairs and waits for next interval

## Logging

### Log File
```
/Users/jfrm918/.openclaw/workspace/trading_bots/bots/vwap_momentum_bot.log
```

### Log Fields
All trades include:
- Timestamp (ISO format)
- Pair (BTC-USDT or ETH-USDT)
- Action (BUY or SELL)
- Price and quantity
- VWAP at entry/exit
- Exit reason (for SELL)
- PnL and percentage (for SELL)
- **open_position** field (True for BUY, False for SELL)
- Current balance

### Example Log Entries

**BUY Entry:**
```
2026-04-04 12:50:53,123 - VWAP - INFO - BUY 0.000345 BTC-USDT @ $95234.50 | Size: $35.00 | VWAP: $94800.00 | Balance: $65.00 | open_position=True
```

**SELL Exit (Take Profit):**
```
2026-04-04 12:55:12,456 - VWAP - INFO - ✅ SELL 0.000345 BTC-USDT @ $97139.59 | Reason: take_profit | PnL: $0.66 (1.88%) | Balance: $65.66 | open_position=False
```

## Integration with snapshot_writer.py

The bot automatically integrates with the snapshot export system:
- Log file: `vwap_momentum_bot.log`
- Snapshot key: `vwap`
- Exported to: `/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot.json`

### Snapshot Fields
```json
{
  "vwap": {
    "pnl": 2.45,
    "trades": 8,
    "wins": 6,
    "balance": 102.45,
    "open_position": true
  }
}
```

## Running the Bot

### Direct Execution
```bash
cd /Users/jfrm918/.openclaw/workspace/trading_bots
python3 bots/vwap_momentum_bot.py
```

### With Custom Config
The bot auto-loads `config.json` and expects:
- `exchange`: "blofin"
- `trading_pairs`: ["BTC-USDT", "ETH-USDT"]
- API keys optional (paper trading mode)

### Update Interval
- **Default**: 60 seconds between scans
- **Candle Timeframe**: 1-minute
- **Reason**: Faster signal response and multi-minute position overlap detection

## Performance Metrics

### Tracked Statistics
- Total trades (buy + sell pairs)
- Win/loss count and win rate %
- Cumulative PnL in dollars
- Individual trade PnL and percentage
- Final balance and return

### Example Report
```json
{
  "strategy": "VWAP Momentum",
  "total_trades": 8,
  "wins": 6,
  "losses": 2,
  "win_rate": "75.0%",
  "total_pnl": "$2.45",
  "balance": "$102.45",
  "open_positions": 1
}
```

## Configuration Parameters

All parameters are hardcoded in the class `__init__`:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `capital` | 100.0 | Starting simulated capital |
| `position_size_pct` | 0.35 | 35% per trade |
| `max_positions` | 2 | Max simultaneous pairs |
| `vwap_threshold` | 0.005 | 0.5% above VWAP entry |
| `volume_multiplier` | 1.5 | Volume confirmation threshold |
| `tp_pct` | 0.02 | 2% take profit |
| `sl_pct` | 0.01 | 1% stop loss from VWAP |

## Risk Management

### Built-in Safeguards
1. **Capital Allocation**: Only 35% risk per trade (max $35 on $100)
2. **Position Limits**: Never more than 2 pairs traded simultaneously
3. **Stop Loss**: Hard stop at 1% below entry VWAP
4. **Take Profit**: Automatic exit at +2%
5. **Balance Check**: Refuses trades if insufficient capital
6. **Duplicate Prevention**: Prevents opening two positions on same pair

## Exchange Integration

### Blofin API
- **Mode**: Paper trading (no real transactions)
- **Pairs**: BTC-USDT, ETH-USDT
- **Candle Fetching**: `fetch_ohlcv()` with 1m timeframe
- **Rate Limiting**: Enabled for API respect

### Error Handling
- Graceful candle fetch failures
- Logging of all exceptions
- Automatic retry on next interval
- No position taken on bad data

## Dependencies

```python
import json          # Config loading
import time          # Sleep intervals
import logging       # Trade logging
from datetime import datetime, timedelta
from collections import deque  # Rolling windows
import ccxt         # Blofin exchange connection
```

## Testing

Syntax validation:
```bash
python3 -m py_compile bots/vwap_momentum_bot.py
```

Quick test of initialization:
```python
from bots.vwap_momentum_bot import VWAPMomentumBot
bot = VWAPMomentumBot(config_path='./config.json')
bot.report()
```

## Future Enhancements

Possible improvements (not yet implemented):
- Multiple timeframe VWAP confirmation
- Bollinger Bands for volatility filter
- ATR for dynamic stop loss sizing
- Trade persistence across restarts
- Telegram/Discord notifications
- Live trading mode with real API keys
- Backtesting module with historical data

## Troubleshooting

### Bot Won't Start
- Check `config.json` exists in trading_bots/ directory
- Verify ccxt library installed: `pip3 install ccxt`
- Check file permissions on log directory

### No Trades Executing
- Verify exchange connectivity (check logs for connection errors)
- Check if volume data is available (new pairs may need history)
- Ensure 1440+ minutes of history for VWAP (24-hour window)

### Balance Not Updating
- Each trade execution updates balance immediately in logs
- Balance reflects only completed trades (BUY+SELL pairs)
- Open positions don't affect balance calculation

---

**Bot Version**: 1.0  
**Created**: April 4, 2026  
**Status**: Production Ready (Paper Trading)
