"""Quick analysis check — runs full_analyzer v2."""
import sys
from pathlib import Path

TRACKER_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker")
sys.path.insert(0, str(TRACKER_DIR / "src"))

from full_analyzer import analyze_market, MARKETS, print_report, save_report
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)
results = [analyze_market(m, now_utc) for m in MARKETS]
print_report(results)
save_report(results)
