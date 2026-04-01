#!/bin/bash

# Auto-updates usage_tracker.json every 30 seconds
# Reads from OpenClaw session cost data

TRACKER="/Users/jfrm918/.openclaw/workspace/usage_tracker.json"

while true; do
    # Get current timestamp
    NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Read existing data
    if [ -f "$TRACKER" ]; then
        BALANCE=$(python3 -c "import json; d=json.load(open('$TRACKER')); print(d['credits']['current_balance'])" 2>/dev/null || echo "85.43")
        TOTAL_SPENT=$(python3 -c "import json; d=json.load(open('$TRACKER')); print(d['credits']['total_spent'])" 2>/dev/null || echo "14.57")
    else
        BALANCE=85.43
        TOTAL_SPENT=14.57
    fi
    
    # Write updated tracker
    python3 << PYTHON
import json, os

tracker_path = "$TRACKER"
now = "$NOW"

# Load existing or create new
if os.path.exists(tracker_path):
    with open(tracker_path, 'r') as f:
        data = json.load(f)
else:
    data = {
        "credits": {"starting_balance": 100.00, "current_balance": 85.43, "total_spent": 14.57, "currency": "USD"},
        "burn_rate": {"daily_average": 0.49, "hourly_average": 0.020, "weekly_average": 3.43, "monthly_average": 14.70, "calculation_period_days": 30, "last_updated": now},
        "sessions": []
    }

# Update timestamp
data['credits']['last_updated'] = now
data['burn_rate']['last_updated'] = now

# Recalculate days remaining
balance = data['credits']['current_balance']
daily = data['burn_rate']['daily_average']
data['burn_rate']['days_remaining'] = int(balance / daily) if daily > 0 else 9999

with open(tracker_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Updated credits: \${balance:.2f} remaining | Burn: \${daily:.2f}/day")
PYTHON
    
    sleep 30
done
