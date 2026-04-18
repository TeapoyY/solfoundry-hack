import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker')
from src.database import TweetDB
from src.analyzer import analyze, print_results, COVERAGE
from pathlib import Path
import json
from datetime import datetime, timezone

db = TweetDB()
print('Total in DB:', db.total_tweets())
results = analyze(db)
print_results(results)

# Save snapshot
out = Path(r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\output')
out.mkdir(exist_ok=True)
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
fp = out / f'snapshot_{ts}.json'
save = {'collected_at': datetime.now(timezone.utc).isoformat(), 'total': db.total_tweets(), 'coverage_ratio': COVERAGE, 'results': results}
fp.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding='utf-8')
latest = out / 'latest_snapshot.json'
latest.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding='utf-8')
print('Saved:', fp.name)
print()
print('=== ANALYSIS RESULTS ===')
for r in results:
    print(f'  {r["market_id"]}: P={r["p_yes"]*100:.0f}% Edge={r["edge_pct"]} Kelly={r["kelly_quarter"]*100:.1f}%')
