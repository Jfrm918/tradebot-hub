#!/bin/bash

# Start Hub Web Server
# Serves the dashboard on http://localhost:8000
# Accessible from any device on your network

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8000

echo "🚀 Starting TradeBot Hub Web Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Access the hub at:"
echo "   http://localhost:$PORT"
echo "   http://127.0.0.1:$PORT"
echo ""
echo "🌐 On your iPhone/other devices:"
echo "   Find your Mac's local IP (System Settings → Network)"
echo "   Then visit: http://<YOUR_MAC_IP>:$PORT"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SCRIPT_DIR"
python3 -m http.server $PORT
