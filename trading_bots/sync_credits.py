#!/usr/bin/env python3
"""
Anthropic Credits Auto-Sync
Fetches current credit balance from Anthropic API and updates usage_tracker.json
Runs every 30 minutes via launchd
"""

import json
import os
import requests
from datetime import datetime
import sys

API_KEY = os.getenv('ANTHROPIC_API_KEY')
TRACKER_PATH = '/Users/jfrm918/.openclaw/workspace/trading_bots/usage_tracker.json'
LOG_PATH = '/Users/jfrm918/.openclaw/workspace/trading_bots/sync_log.txt'

def log_sync(message):
    """Log sync event with timestamp"""
    ts = datetime.now().isoformat()
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{ts}] {message}\n")

def fetch_anthropic_usage():
    """Fetch current usage from Anthropic API"""
    if not API_KEY:
        log_sync("ERROR: ANTHROPIC_API_KEY not set")
        return None
    
    try:
        headers = {
            'x-api-key': API_KEY,
            'anthropic-beta': 'usage-2024-06-01'
        }
        response = requests.get(
            'https://api.anthropic.com/v1/messages/usage',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            log_sync(f"ERROR: API returned {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_sync(f"ERROR: {str(e)}")
        return None

def load_tracker():
    """Load existing usage_tracker.json"""
    try:
        with open(TRACKER_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_sync(f"ERROR: Could not load tracker: {str(e)}")
        return None

def save_tracker(data):
    """Save updated usage_tracker.json"""
    try:
        with open(TRACKER_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        log_sync(f"ERROR: Could not save tracker: {str(e)}")
        return False

def calculate_burn_rate(tracker, new_balance):
    """Calculate rolling burn rates"""
    old_balance = tracker['credits']['current_balance']
    burned = old_balance - new_balance
    
    # Get previous burn data
    prev_daily = tracker['burn_rate'].get('daily_average', 0)
    prev_period = tracker['burn_rate'].get('calculation_period_days', 1)
    
    # Rolling average: weight new burn against historical average
    new_period = prev_period + 1
    new_daily = ((prev_daily * prev_period) + burned) / new_period
    new_hourly = new_daily / 24
    new_weekly = new_daily * 7
    new_monthly = new_daily * 30
    
    days_remaining = max(0, new_balance / new_daily) if new_daily > 0 else 9999
    
    return {
        'daily_average': round(new_daily, 6),
        'hourly_average': round(new_hourly, 6),
        'weekly_average': round(new_weekly, 6),
        'monthly_average': round(new_monthly, 6),
        'calculation_period_days': new_period,
        'days_remaining': int(days_remaining),
        'last_updated': datetime.now().isoformat() + 'Z',
        'note': f'Rolling average over {new_period} days. Burned ${burned:.2f} since last sync.'
    }

def sync():
    """Main sync function"""
    usage = fetch_anthropic_usage()
    if not usage:
        log_sync("Sync failed: Could not fetch Anthropic usage")
        return False
    
    tracker = load_tracker()
    if not tracker:
        log_sync("Sync failed: Could not load tracker")
        return False
    
    # Extract balance from API response
    # Anthropic usage API returns balance in 'balance' field
    new_balance = usage.get('balance', {}).get('amount', tracker['credits']['current_balance'])
    old_balance = tracker['credits']['current_balance']
    
    # Update tracker
    tracker['credits']['current_balance'] = new_balance
    tracker['credits']['last_updated'] = datetime.now().isoformat() + 'Z'
    
    # Update burn rates
    tracker['burn_rate'] = calculate_burn_rate(tracker, new_balance)
    
    # Save
    if save_tracker(tracker):
        log_sync(f"✓ Synced. Balance: ${old_balance:.2f} → ${new_balance:.2f}. Burned: ${old_balance - new_balance:.2f}")
        return True
    else:
        return False

if __name__ == '__main__':
    success = sync()
    sys.exit(0 if success else 1)
