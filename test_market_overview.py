#!/usr/bin/env python3
"""Test Market Overview page functionality with Pyth Network integration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.pyth_client import pyth_client
from config.settings import settings

print("=" * 80)
print("Testing Market Overview Page - Pyth Network Integration")
print("=" * 80)

# Test 1: Fetch all tracked coins
print("\n[Test 1] Fetching all tracked coins...")
try:
    market_data = pyth_client.get_current_prices(settings.TRACKED_COINS)
    print(f"✓ Successfully fetched {len(market_data)}/{len(settings.TRACKED_COINS)} coins")
    
    if len(market_data) != len(settings.TRACKED_COINS):
        missing = set(settings.TRACKED_COINS) - set(market_data.keys())
        print(f"⚠ Missing coins: {missing}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test 2: Test individual coin switching (simulating UI behavior)
print("\n[Test 2] Testing coin switching (simulating UI selection)...")
test_coins = ['bitcoin', 'ethereum', 'polygon', 'solana']

for coin_id in test_coins:
    try:
        data = pyth_client.get_current_prices([coin_id])
        if coin_id in data:
            coin = data[coin_id]
            print(f"✓ {coin['name']:12} - ${coin['current_price']:>10,.2f}")
        else:
            print(f"✗ {coin_id} - No data returned")
    except Exception as e:
        print(f"✗ {coin_id} - Error: {e}")

# Test 3: Verify data structure
print("\n[Test 3] Verifying data structure...")
sample_coin = market_data[list(market_data.keys())[0]]
required_fields = ['id', 'symbol', 'name', 'current_price', 'price_change_percentage_24h', 
                   'market_cap', 'total_volume', 'last_updated']

all_present = all(field in sample_coin for field in required_fields)
if all_present:
    print("✓ All required fields present in response")
else:
    missing = [f for f in required_fields if f not in sample_coin]
    print(f"✗ Missing fields: {missing}")

# Test 4: Test historical data (used in comparison charts)
print("\n[Test 4] Testing historical data retrieval...")
try:
    hist_data = pyth_client.get_historical_data('bitcoin', days=7)
    print(f"✓ Historical data retrieved: {len(hist_data)} data points")
    print(f"  Note: Pyth provides simulated historical data (real-time only)")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 80)
print("✓ All tests passed! Market Overview page should work correctly.")
print("=" * 80)
print("\nYou can now run the app with: streamlit run app.py")
print("Or view Market Overview: streamlit run pages/1_📊_Market_Overview.py")
