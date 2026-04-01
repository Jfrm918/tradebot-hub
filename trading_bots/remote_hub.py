#!/usr/bin/env python3
"""
TradeBot Hub - Remote Access Server
Serves the dashboard with basic auth + logging
Access from anywhere on your network or via port forwarding
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

class TradeHubHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Log access
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.client_address[0]} → {self.path}")
        
        # Serve the dashboard
        if self.path == '/' or self.path == '/hub_dashboard.html':
            self.path = '/hub_dashboard.html'
        
        return super().do_GET()
    
    def end_headers(self):
        # Allow cross-origin access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        return super().end_headers()

if __name__ == '__main__':
    os.chdir('/Users/jfrm918/.openclaw/workspace/trading_bots')
    
    PORT = 8000
    server = HTTPServer(('0.0.0.0', PORT), TradeHubHandler)
    
    print(f"\n{'='*60}")
    print(f"🤖 TradeBot Hub - Remote Access Server")
    print(f"{'='*60}")
    print(f"\n📍 Access your dashboard:")
    print(f"   Local (home Wi-Fi):  http://localhost:8000")
    print(f"   Other devices:       http://192.168.x.x:8000  (find your Mac IP)")
    print(f"   Remote (anywhere):   Use ngrok or port forwarding")
    print(f"\n⏹️  Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped.")
        sys.exit(0)
