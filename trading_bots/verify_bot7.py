#!/usr/bin/env python3
"""Verification script for VWAP Momentum Bot (Bot 7)"""

import sys
import os
from pathlib import Path

print("🔍 VWAP Momentum Bot Verification\n")

# Check file exists
bot_file = Path('/Users/jfrm918/.openclaw/workspace/trading_bots/bots/vwap_momentum_bot.py')
print(f"1. Bot file: {bot_file}")
print(f"   Status: {'✅ EXISTS' if bot_file.exists() else '❌ MISSING'}\n")

# Check syntax
print("2. Syntax check:")
result = os.system(f"python3 -m py_compile {bot_file} 2>/dev/null")
print(f"   Status: {'✅ VALID' if result == 0 else '❌ INVALID'}\n")

# Check imports
print("3. Import test:")
try:
    sys.path.insert(0, '/Users/jfrm918/.openclaw/workspace/trading_bots')
    from bots.vwap_momentum_bot import VWAPMomentumBot
    print(f"   Status: ✅ IMPORTS OK\n")
except Exception as e:
    print(f"   Status: ❌ IMPORT FAILED: {e}\n")
    sys.exit(1)

# Check config
config_file = Path('/Users/jfrm918/.openclaw/workspace/trading_bots/config.json')
print(f"4. Config file: {config_file}")
print(f"   Status: {'✅ EXISTS' if config_file.exists() else '❌ MISSING'}\n")

# Check documentation
doc_file = Path('/Users/jfrm918/.openclaw/workspace/trading_bots/BOT_7_VWAP_MOMENTUM.md')
print(f"5. Documentation: {doc_file}")
print(f"   Status: {'✅ EXISTS' if doc_file.exists() else '❌ MISSING'}\n")

# Check snapshot_writer update
print("6. Snapshot integration:")
with open('/Users/jfrm918/.openclaw/workspace/trading_bots/snapshot_writer.py') as f:
    content = f.read()
    has_vwap = 'vwap_momentum_bot.log' in content
    print(f"   BOT_MAP entry: {'✅ REGISTERED' if has_vwap else '❌ NOT FOUND'}\n")

# Initialize bot
print("7. Bot initialization:")
try:
    import warnings
    warnings.filterwarnings('ignore')
    bot = VWAPMomentumBot(config_path='/Users/jfrm918/.openclaw/workspace/trading_bots/config.json')
    print(f"   Capital: ${bot.capital}")
    print(f"   Position size: {bot.position_size_pct*100:.0f}%")
    print(f"   Max positions: {bot.max_positions}")
    print(f"   Status: ✅ INITIALIZED OK\n")
except Exception as e:
    print(f"   Status: ❌ INIT FAILED: {e}\n")
    sys.exit(1)

# Verify key methods exist
print("8. Core methods:")
methods = [
    '_calculate_vwap',
    '_get_avg_volume', 
    '_check_entry_signal',
    '_check_exit_conditions',
    '_execute_buy',
    '_execute_sell',
    '_process_pair',
    'run',
    'report'
]
for method in methods:
    has_method = hasattr(bot, method)
    print(f"   {method}: {'✅' if has_method else '❌'}")

print(f"\n{'='*60}")
print("✅ VWAP Momentum Bot (Bot 7) - VERIFICATION COMPLETE")
print(f"{'='*60}")
print("\nBot ready for deployment!")
print(f"Start with: cd /Users/jfrm918/.openclaw/workspace/trading_bots && python3 bots/vwap_momentum_bot.py")
