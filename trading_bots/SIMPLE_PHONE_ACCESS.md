# Access TradeBot Hub from Your Phone - Simple

## The Simplest Way (No Extra Apps)

Your Mac's web server is already running on port 8000.

### Step 1: Find Your Mac's IP Address

Open Terminal on your Mac:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

You'll see something like: `192.168.1.100`

### Step 2: On Your Phone

Open Safari and go to:
```
http://192.168.1.100:8000/hub_dashboard.html
```

(Replace 192.168.1.100 with your actual IP from Step 1)

### Step 3: Add to Home Screen

- Tap the Share button (arrow)
- Scroll down → "Add to Home Screen"
- Name it "TradeBot Hub"
- Tap "Add"

**Done.** You now have a home screen shortcut.

---

## But This Only Works on Home Wi-Fi

If you want to check from outside your home, you need remote access.

### Option A: Tailscale (Easiest)

```bash
brew install tailscale
sudo tailscale up
```

Then on your phone:
1. Install Tailscale from App Store
2. Sign in with same account
3. Access via: `http://<your-mac-tailscale-ip>:8000`

Works from anywhere, encrypted, no port forwarding.

### Option B: SSH Port Forward (Advanced)

If you have a server accessible from internet:
```bash
ssh -R 8000:localhost:8000 user@your.server.com
```

Then access via your server's IP.

---

## Recommendation

**For now:** Use home Wi-Fi access (Step 1-3). When you need remote, run Tailscale.

Tailscale is free, secure, and takes 2 minutes.
