#!/bin/bash

# TradeBot Hub - Master Control Script
# Runs all 5 trading bots in parallel background processes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/.pids"

# Create directories
mkdir -p "$LOG_DIR"

# Trap exit to kill all background processes
trap 'kill_all_bots' EXIT INT TERM

kill_all_bots() {
  echo "🛑 Stopping all trading bots..."
  if [ -f "$PID_FILE" ]; then
    while read pid; do
      kill "$pid" 2>/dev/null || true
    done < "$PID_FILE"
  fi
  rm -f "$PID_FILE"
  echo "All bots stopped."
}

echo "🚀 Starting TradeBot Hub..."
echo "Total Capital: \$500 (5 strategies × \$100)"
echo ""

# Start each bot in the background
echo "📊 Launching Momentum Bot..."
python3 "$SCRIPT_DIR/bots/momentum_bot.py" > "$LOG_DIR/momentum.log" 2>&1 &
echo $! >> "$PID_FILE"

echo "📊 Launching Mean Reversion Bot..."
python3 "$SCRIPT_DIR/bots/mean_reversion_bot.py" > "$LOG_DIR/mean_reversion.log" 2>&1 &
echo $! >> "$PID_FILE"

echo "📊 Launching Grid Trading Bot..."
python3 "$SCRIPT_DIR/bots/grid_bot.py" > "$LOG_DIR/grid.log" 2>&1 &
echo $! >> "$PID_FILE"

echo "📊 Launching Scalping Bot..."
python3 "$SCRIPT_DIR/bots/scalp_bot.py" > "$LOG_DIR/scalp.log" 2>&1 &
echo $! >> "$PID_FILE"

echo "📊 Launching Swing Trading Bot..."
python3 "$SCRIPT_DIR/bots/swing_bot.py" > "$LOG_DIR/swing.log" 2>&1 &
echo $! >> "$PID_FILE"

echo ""
echo "✅ All bots running. Logs in: $LOG_DIR"
echo "PID file: $PID_FILE"
echo ""
echo "To stop: ./run_all_bots.sh (Ctrl+C)"
echo "Hub dashboard: http://localhost:5000"
echo ""

# Keep script alive
wait
