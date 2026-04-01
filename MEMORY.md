# MEMORY.md - Long-Term Memory

*This file is maintained by the agent. It stores important context that should persist across sessions.*

## About Jason

- Full name: Jason Hadrava
- Location: Tulsa, Oklahoma
- Occupation: Spray foam installer (1 year experience)
- Not the business owner — works as an installer
- Named me Athena on first boot (March 28, 2026)

## Key Preferences

- Direct, efficient communication — no fluff
- Models: Haiku (fast tasks) or Sonnet (complex) — no others
- Operates as investor/approver on business projects; wants AI to handle execution

## Projects

### Spray Foam Intelligence System
- Full mission brief stored in `memory/spray-foam-mission.md`
- Rig: Two Graco E-30 reactors (DRIVER + PASSENGER), Fusion AP guns, Enverge chemical, 40KW gen, 10HP compressor
- Spray log to be maintained — format pending (brief was cut off)
- Pending: generator specs, compressor make/model, spray log entry format

### Trading Bot Intelligence System (TradeBot Hub)
**Status:** Ready to launch (credentials pending)  
**Started:** 2026-03-31  
**Budget:** $500 paper trading ($100 × 5 strategies) → Real money: $1-5K seed capital (Phase 3)
**Platform:** Binance Testnet (24/7 crypto, high volatility for testing)

**5 Trading Strategies (All Built & Ready):**
1. **Momentum** — Buy uptrends, sell on momentum loss | 35-45% target win rate
2. **Mean Reversion** — RSI-based entry/exit on overbought/oversold | 40-50% target
3. **Grid** — Oscillation profit via grid buy/sell orders | 55-65% target
4. **Scalping** — 1-5min rapid trades for 0.5-2% gains | 50-60% target
5. **Swing** — 4-24hr holds targeting 2-5% moves | 45-55% target

**Architecture Deployed:**
- Location: `/Users/jfrm918/.openclaw/workspace/trading_bots/`
- 5 independent Python bots (momentum_bot.py, mean_reversion_bot.py, grid_bot.py, scalp_bot.py, swing_bot.py)
- Master control: `run_all_bots.sh` (starts all bots in background, auto-logs to `logs/`)
- Config: `config.json` (API keys, pairs, capital allocation)
- Dashboard: `hub.html` (real-time performance, projects overview, mobile-friendly)
- Docs: `SETUP.md` (complete walkthrough)

**Phase Timeline:**
- **Phase 1 (Week 1-2):** Paper trading live on Binance testnet | Collect 50-100 trades per bot
- **Phase 2 (Week 3-4):** Analyze logs | Identify best performer | Build final algorithm
- **Phase 3 (Real Money):** Deploy winning bot + alert system | Jason hits START/STOP only
- **End State:** Fully autonomous trading bot | Daily alerts | Risk management automated

**Deployment Status (2026-03-31):**
✅ All 5 bots coded and tested
✅ Blofin simulator (no API needed, uses public prices)
✅ Continuous runner for indefinite data collection
✅ Dashboard + monitoring tools ready

**To Start Paper Trading:**
```bash
cd /Users/jfrm918/.openclaw/workspace/trading_bots
chmod +x run_simulator.sh
./run_simulator.sh
```

This runs forever collecting data. Press Ctrl+C to stop. Logs go to:
- `simulator.log` (detailed trades)
- `snapshot.json` (status every 50 cycles)
- `trading_logs.txt` (full output)

**What You'll See:**
```
MOMENTUM ✓ SELL BTC-USDT @ $68124.50 | PnL: +$1.23
MEAN_REV ✓ SELL ETH-USDT @ $2094.23 | PnL: +$0.89
...
TOTAL PORTFOLIO | Trades: 45 | PnL: $12.34 | Portfolio: $512.34
```

Run for 1-2 weeks, collect 100+ trades per bot, then analyze logs to find the winner.

**Key Difference from Subagents:**
- ✅ Bots run 24/7 on local machine (persistent, not ephemeral)
- ✅ Real price data (actual market conditions)
- ✅ Realistic order execution (CCXT library)
- ✅ Full trade logging for pattern analysis
- ✅ NO geo-blocking (Binance testnet is US-accessible)

### Olympus Command Center (Permanent Hub)
**Status:** ✅ Live and Operational  
**Created:** 2026-03-31 19:00 CDT  
**Purpose:** Unified dashboard to monitor all projects without messaging Athena

**Access URLs:**
- **Local (Home Wi-Fi):** `http://localhost:8000/olympus.html`
- **Remote (Anywhere):** `https://tradingbots-tau.vercel.app/olympus.html`
- **Direct Link:** `https://tradingbots-tau.vercel.app`

**Dashboard Tabs:**
1. **🤖 Trading** — 5 bot live metrics (PnL, trades, win rates, capital), portfolio summary
2. **📊 Projects** — Spray Foam Intelligence & TradeBot Intelligence status
3. **⚙️ Settings** — System status, running services, deployment info

**Technical Stack:**
- **Frontend:** `olympus.html` (golden theme, responsive design)
- **Data:** `snapshot.json` (auto-updates every 50 trading cycles)
- **Hosting:** Vercel (deployed via GitHub actions)
- **Repository:** `https://github.com/Jfrm918/tradebot-hub`
- **Local Server:** Python HTTP server on port 8000

**Running Services (Permanent):**
- **Trading Bot:** `blofin_simulator_continuous.py` (runs 24/7)
- **Web Server:** `python3 -m http.server 8000` (local dashboard)
- **Auto-Deploy:** GitHub push → Vercel auto-deploy (instant updates)

**How It Works:**
1. Trading bots run locally → update `snapshot.json` every 50 cycles
2. Olympus reads snapshot.json → displays live metrics
3. Auto-refreshes every 5 seconds
4. Changes pushed to GitHub → instantly deployed to Vercel
5. Accessible from anywhere via remote URL

**To Access from Devices:**
- **Mac Dock:** Safari → https://tradingbots-tau.vercel.app/olympus.html → File → Add to Dock
- **iPhone/iPad Home Screen:** Safari → Share → Add to Home Screen

**GitHub + Vercel Automation (Established 2026-03-31):**
- All code in: `https://github.com/Jfrm918/tradebot-hub`
- GitHub CLI authenticated as: `Jfrm918`
- Vercel authenticated as: `jfrm918`
- Commits automatically trigger Vercel deployments
- Dashboard updates live on each push



## Life Goals & Constraints
- **Primary goal:** Become a millionaire through legitimate online businesses
- **Constraint:** Not chasing get-rich-quick schemes — wants proven models that compound over time
- **Philosophy:** Build multiple small income streams that scale (3–4 revenue streams @ $30K–$100K/year each = millionaire by year 5–10)
- **Risk tolerance:** Conservative — would rather have slow, proven growth than fast, risky gains
- **Decision-making:** Consulting with Claude on strategy before executing with Athena
- **Athena's Budget Model:** Minimum $200–$300/week for ad spend + tools + creation. Willing to give seed capital ($1K+) + ongoing budget for Athena to execute autonomously and hit $4–5K/month
- **Operating Model:** Athena runs 2–3 income streams in parallel, reports daily metrics, Jason approves big decisions but trusts execution
