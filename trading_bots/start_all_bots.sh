#!/bin/bash
# Start all 7 trading bots + snapshot writer

cd /Users/jfrm918/.openclaw/workspace/trading_bots

# Create logs directory
mkdir -p logs

# Start all bots in background
echo "Starting all 7 bots + snapshot writer..."
python3 bots/momentum_bot.py >> logs/momentum.log 2>&1 &
python3 bots/mean_reversion_bot.py >> logs/reversion.log 2>&1 &
python3 bots/grid_bot.py >> logs/grid.log 2>&1 &
python3 bots/scalp_bot.py >> logs/scalp.log 2>&1 &
python3 bots/swing_bot_v2.py >> logs/swing.log 2>&1 &
python3 bots/vwap_reversion_bot.py >> logs/vwap_rev.log 2>&1 &
python3 bots/vwap_momentum_bot.py >> logs/vwap_mom.log 2>&1 &
python3 snapshot_writer.py >> logs/snapshot.log 2>&1 &

echo "All bots started. Check logs/ directory for output."
echo "Run: tail -f logs/*.log"
