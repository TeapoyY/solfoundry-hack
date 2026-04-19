import sys, os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\src')

# Fresh import
from full_analyzer import analyze_market, MARKETS, load_live_xtrack

now_utc = datetime.now(timezone.utc)

# Check load_live_xtrack
live = load_live_xtrack()
print('load_live_xtrack result:', live)

# Check get_market_confirmed
from full_analyzer import get_market_confirmed
for m in MARKETS:
    cid = m['id']
    c = get_market_confirmed(m)
    print(cid + ': get_market_confirmed=' + str(c))

# Run one analysis and check output
m = MARKETS[0]  # apr14-21
r = analyze_market(m, now_utc)
print('apr14-21 xtrack_confirmed in result:', r.get('xtrack_confirmed'))
print('apr14-21 confirmed (local var):', r.get('confirmed', 'NOT_IN_RESULT'))
