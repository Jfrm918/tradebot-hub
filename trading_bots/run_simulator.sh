#!/bin/bash

# TradeBot Hub - Blofin Paper Trading Simulator
# Runs continuous paper trading with 5 bots
# Logs to trading_logs.txt

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/trading_logs.txt"
SIMULATOR="$SCRIPT_DIR/blofin_simulator_continuous.py"

echo "🚀 Starting TradeBot Hub - Blofin Paper Trading Simulator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 5 Bots × \$100 = \$500 Total Paper Capital"
echo "📈 Trading on Realistic Price Movements"
echo "📁 Logs: $LOG_FILE"
echo "⏹️  Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run simulator with output to both screen and file
python3 "$SIMULATOR" 2>&1 | tee "$LOG_FILE"
