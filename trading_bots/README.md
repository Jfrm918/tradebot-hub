# TradeBot Hub 🤖

Autonomous trading bot system with live dashboard. Paper trading 5 different strategies simultaneously on realistic market conditions.

## Overview

- **5 Trading Strategies**: Momentum, Mean Reversion, Grid, Scalping, Swing
- **Paper Trading**: $100 per strategy × 5 = $500 total capital
- **Live Dashboard**: Real-time PnL, win rates, trade history
- **Fully Autonomous**: Runs 24/7, collects data for analysis

## Quick Start

### Local Development

```bash
# Start the trading simulator
python3 blofin_simulator_continuous.py

# In another terminal, start the web server
python3 -m http.server 8000

# Open http://localhost:8000 in your browser
```

### View Dashboard

```
http://localhost:8000/hub_dashboard.html
```

## Architecture

### Bots
- `blofin_simulator_continuous.py` — 5 trading bots running simultaneously
- Generates realistic price movements
- Logs every trade with full P&L tracking

### Dashboard
- `hub_dashboard.html` — Live trading metrics
- `snapshot.json` — Status snapshots every 50 cycles
- Auto-refreshes every 5 seconds

### Web Server
- `start_hub.sh` — Lightweight HTTP server on port 8000

## Monitoring

### Real-time Logs
```bash
tail -f simulator.log
```

### Status Snapshots
```bash
cat snapshot.json
```

### Stop the Bots
```bash
pkill -f blofin_simulator_continuous
```

## Data Collection

After 1-2 weeks of trading data:
1. Analyze which strategy performs best
2. Extract the top performer's logic
3. Build real-money bot from winning strategy
4. Deploy alert system for live trading

## Phase Timeline

**Phase 1 (Current)**: Paper trading 5 strategies, collect data  
**Phase 2**: Analyze logs, identify best performer  
**Phase 3**: Build real-money bot, deploy to production

## Technologies

- **Python 3.9+** — Bot engine
- **HTML/CSS/JS** — Dashboard UI
- **Vercel** — Production deployment
- **GitHub** — Version control

## Author

Jason Hadrava

## License

MIT
