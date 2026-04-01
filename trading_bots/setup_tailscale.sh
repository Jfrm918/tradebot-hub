#!/bin/bash

# Setup Tailscale for TradeBot Hub Remote Access
# Private, secure network tunnel - no port forwarding needed

echo "🔐 Setting up Tailscale for TradeBot Hub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Tailscale is installed
if ! command -v tailscale &> /dev/null; then
    echo "📦 Installing Tailscale..."
    brew install tailscale
    echo "✅ Tailscale installed"
fi

echo ""
echo "Starting Tailscale daemon..."
sudo tailscale up

echo ""
echo "✅ Tailscale is running!"
echo ""
echo "Your Mac's Tailscale IP will appear above."
echo "Use that IP + port 8000 on your phone:"
echo "   http://<YOUR_TAILSCALE_IP>:8000/hub_dashboard.html"
echo ""
echo "Install Tailscale on your phone from App Store,"
echo "connect to the same network, and you're done."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
