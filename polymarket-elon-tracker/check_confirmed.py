import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\src')
from full_analyzer import MARKETS, get_market_confirmed
for m in MARKETS:
    cid = m["id"]
    c = get_market_confirmed(m)
    print(cid + ": confirmed=" + str(c))
