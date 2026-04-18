import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker')
from src.database import TweetDB
from src.analyzer import analyze, COVERAGE
from pathlib import Path
import json
from datetime import datetime, timezone

db = TweetDB()
total = db.total_tweets()
print('DB tweets:', total)

results = analyze(db)
for r in results:
    mid = r['market_id']
    conf = r['confirmed']
    conf_e = r['confirmed_est']
    p = r['p_yes']
    edge = r['edge_pct']
    kq = r['kelly_quarter']
    vel = r['velocity_ratio']
    print('  ' + mid + ': confirmed=' + str(conf) + ' (est=' + str(conf_e) + ') P=' + str(round(p*100)) + '% Edge=' + edge + ' Kelly=' + str(round(kq*100,1)) + '% vel_ratio=' + str(vel) + 'x')

out = Path(r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\output')
out.mkdir(exist_ok=True)
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
fp = out / ('snapshot_' + ts + '.json')
save = {'collected_at': datetime.now(timezone.utc).isoformat(), 'total': total, 'results': results, 'coverage': COVERAGE}
fp.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding='utf-8')
latest = out / 'latest_snapshot.json'
latest.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding='utf-8')
print('Saved:', fp.name)
print('Latest:', latest.name)
