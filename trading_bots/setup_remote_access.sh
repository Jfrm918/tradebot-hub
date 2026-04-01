#!/bin/bash

# Setup Remote Access for TradeBot Hub
# Uses ngrok to expose localhost:8000 to the internet
# Requires ngrok: brew install ngrok

echo "🌐 Setting up remote access for TradeBot Hub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📦 ngrok not found. Installing..."
    brew install ngrok
fi

echo ""
echo "✅ ngrok installed. Starting remote tunnel..."
echo ""
echo "Your TradeBot Hub will be accessible at the URL shown below."
echo "You can bookmark this URL on your phone and access it from anywhere."
echo ""
echo "⚠️  The URL changes each time you restart. Save it or run this script"
echo "   to get a new permanent URL with a paid ngrok account."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start ngrok tunnel to localhost:8000
ngrok http 8000 --region us
