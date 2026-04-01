# Phone Access - TradeBot Hub Remote

## Option 1: Home Wi-Fi Only (Simplest)

Works when you're home or on your home network from anywhere.

1. On your iMac, your IP is something like `192.168.x.x`
2. Find it: Terminal → `ifconfig | grep "inet " | grep -v 127.0.0.1`
3. On your phone, go to: `http://192.168.x.x:8000`
4. Add to home screen (Safari → Share → Add to Home Screen)

**Limitation:** Only works when your phone is on your home Wi-Fi.

---

## Option 2: Remote Access (Anywhere) — ngrok

Access your dashboard from **anywhere** in the world.

### Setup (one-time, 2 minutes):

1. **Install ngrok:**
   ```bash
   brew install ngrok
   ```

2. **Sign up for free account:**
   - Go to https://ngrok.com
   - Sign up (free tier)
   - Copy your auth token

3. **Add auth token to ngrok:**
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

4. **Start the tunnel:**
   ```bash
   cd /Users/jfrm918/.openclaw/workspace/trading_bots
   ngrok http 8000
   ```

   You'll see output like:
   ```
   Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8000
   ```

5. **Save that URL** and open it on your phone:
   ```
   https://abc123def456.ngrok.io/hub_dashboard.html
   ```

6. **Add to home screen** (Safari → Share → Add to Home Screen)

7. **Done.** Access from anywhere, anytime.

**Notes:**
- Free tier gives you one tunnel at a time
- URL changes if you stop/restart (unless you get a paid plan with static URL)
- Works anywhere with internet

---

## Option 3: SSH Tunnel (Advanced)

If your Mac is exposed via SSH (requires more setup).

---

## Recommended: Option 2 (ngrok)

Simplest for remote access. Takes 2 minutes to set up, then you have access from anywhere.

Once you run `ngrok http 8000`, the URL is valid **indefinitely** until you stop it. Just keep that terminal window open.

For a permanent URL that doesn't change, upgrade to ngrok Pro ($5/month), but free tier works fine for now.
