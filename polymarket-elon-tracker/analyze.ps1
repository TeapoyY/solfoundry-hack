# xTracker Clone - Tweet Analysis
# 用法: python analyze.py
# 数据源: polymarket-elon-analyzer/data/tweets_chrome_relay_latest.json
#        + polymarket-elon-analyzer/output/deep_analysis_latest.json
#        + Browser Relay 实时采集

$ErrorActionPreference = "SilentlyContinue"
$PROJECT = "C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker"
$DATA = "$PROJECT\data"
$ANALYZER = "C:\Users\Administrator\python\analyzer"

Write-Host "xTracker Clone - Polymarket Elon Analysis"
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm')

# Copy latest tweet data
$tweets_src = "C:\Users\Administrator\.openclaw\workspace\polymarket-elon-analyzer\data\tweets_chrome_relay_latest.json"
$tweets_dst = "$DATA\tweets_latest.json"
if (Test-Path $tweets_src) {
    Copy-Item $tweets_src $tweets_dst -Force
    Write-Host "Copied tweet data"
}

# Run Python analysis
$py = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
& $py "-c" @"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

PRICE = {
    'apr14-21': 0.57,
    'apr17-24': 0.50,
    'may2026': 0.50,
}
COV = 42.0 / 22.0
REAL_DAIL = 30.0 * COV
NOW = datetime.now(timezone.utc)

MARKETS = [
    ['apr14-21', 'Elon Apr14-21 >190', 190, '2026-04-14', '2026-04-21', 116],
    ['apr17-24', 'Elon Apr17-24 >200', 200, '2026-04-17', '2026-04-24', 7],
    ['may2026', 'Elon May2026 >800', 800, '2026-05-01', '2026-05-31', 0],
]

DATA = Path(r'$DATA'.replace('\$', r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\data'))
TWEETS = DATA / 'tweets_latest.json'
if not TWEETS.exists():
    print('No tweet data')
    sys.exit(0)

tweets = json.loads(TWEETS.read_text('utf-8'))
print(f'Tweets: {len(tweets)} loaded')

def parse_ts(s):
    if not s: return None
    s = s.replace('Z', '+00:00').replace(' ', 'T')
    try: return datetime.fromisoformat(s)
    except: return None

def cnt(twt, ws, we):
    ws_dt = datetime.fromisoformat(ws + 'T00:00:00+00:00')
    we_dt = datetime.fromisoformat(we + 'T23:59:59+00:00')
    n = 0
    for t in twt:
        ts = t.get('ts') or t.get('timestamp') or ''
        dt = parse_ts(ts)
        if dt and ws_dt <= dt <= we_dt: n += 1
    return n

def kelly(e, p):
    if e <= 0 or e >= 1: return 0
    b = 1.0/e - 1.0
    q = 1.0 - p
    if b <= 0: return 0
    return max(0, (b*p - q) / b)

def sim_mc(cur, tgt, days, daily):
    import random, math
    if days <= 0: return 1.0 if cur >= tgt else 0.0
    sc = [('bear', daily*0.7, 0.2), ('base', daily, 0.5), ('bull', daily*1.5, 0.3)]
    all_vw, tw = [], 0
    prs = {}
    for nm, rt, wt in sc:
        vs = [cur + random.poisson(rt*days) for _ in range(30000)]
        pr = sum(1 for v in vs if v >= tgt) / 30000
        prs[nm] = round(pr, 4)
        all_vw.extend((v, wt) for v in vs)
        tw += wt * 30000
    pw = sum(w for v, w in all_vw if v >= tgt) / tw
    mw = sum(v*w for v, w in all_vw) / tw
    return round(pw, 4), round(mw, 1), prs

for mid, q, tgt, ws, we, xsnap in MARKETS:
    conf = cnt(tweets, ws, we)
    conf_e = int(conf * COV)
    we_dt = datetime.fromisoformat(we + 'T23:59:59+00:00')
    days_r = max((we_dt - NOW).total_seconds() / 86400.0, 0)
    rem = max(tgt - conf, 0)
    req = rem / days_r if days_r > 0 else 999
    p_yes, mean_v, scen = sim_mc(conf, tgt, days_r, REAL_DAIL)
    edge = p_yes - 0.5
    kf = kelly(0.5, p_yes)
    print()
    print(f'=== {q} ===')
    print(f'  Confirmed: {conf} (est {conf_e}) xtracker: {xsnap}')
    print(f'  Remaining: {rem} in {days_r:.1f}d req: {req:.1f}/d real: {REAL_DAIL:.1f}/d')
    for nm, pr in scen.items():
        print(f'  MC {nm}: {pr*100:.0f}%')
    print(f'  P(yes)={p_yes*100:.0f}% Edge={edge*100:+.1f}% Kelly={kf*100:.1f}%')

    # Save
    OUT = DATA.parent / 'output'
    OUT.mkdir(exist_ok=True)
    import json
    res = {
        'id': mid, 'q': q, 'tgt': tgt, 'conf': conf, 'conf_est': conf_e,
        'rem': rem, 'days_r': round(days_r, 2), 'req': round(req, 1),
        'real_daily': round(REAL_DAIL, 1), 'p_yes': round(p_yes, 4),
        'edge': round(edge, 4), 'edge_pct': f'{edge*100:+.1f}%',
        'kelly_full': round(kf, 4), 'kelly_half': round(kf*0.5, 4),
        'kelly_quarter': round(kf*0.25, 4),
        'scen': scen, 'xtracker': xsnap, 'cov': COV,
    }
    fp = OUT / f'{mid}_analysis.json'
    fp.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'  Saved: {fp.name}')

OUT2 = DATA.parent / 'output'
LATEST = OUT2 / 'summary_latest.json'
ALL = [{'id': mid, 'q': q, 'tgt': tgt, 'conf': conf, 'conf_est': conf_e,
        'p_yes': round(p_yes, 4), 'edge': round(edge, 4), 'edge_pct': f'{edge*100:+.1f}%',
        'kelly_full': round(kf, 4), 'kelly_quarter': round(kf*0.25, 4),
        'days_r': round(days_r, 2), 'real_daily': round(REAL_DAIL, 1),
        'req': round(req, 1), 'xtracker': xsnap}
       for mid, q, tgt, ws, we, xsnap in MARKETS]
LATEST.write_text(json.dumps(ALL, ensure_ascii=False, indent=2), encoding='utf-8')
print()
print(f'Summary: {LATEST}')

"@

# Check syntax
try:
    import ast
    src = r'''
$content = @'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

PRICE = {'apr14-21': 0.57, 'apr17-24': 0.50, 'may2026': 0.50}
COV = 42.0 / 22.0
REAL_DAIL = 30.0 * COV
NOW = datetime.now(timezone.utc)

MARKETS = [
    ['apr14-21', 'Elon Apr14-21 >190', 190, '2026-04-14', '2026-04-21', 116],
    ['apr17-24', 'Elon Apr17-24 >200', 200, '2026-04-17', '2026-04-24', 7],
    ['may2026', 'Elon May2026 >800', 800, '2026-05-01', '2026-05-31', 0],
]

DATA = Path(r'$TWEETS_DIR')
TWEETS = DATA / 'tweets_latest.json'
tweets = json.loads(TWEETS.read_text('utf-8')) if TWEETS.exists() else []
print(f'Tweets: {len(tweets)} loaded')
'''.strip()
    ast.parse(src)
    print('Syntax OK')
except SyntaxError as e:
    print(f'Syntax error: {e}')
"@

# Actually run
Write-Host "Running analysis..."
& $py "-c" @"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
COV = 42.0 / 22.0
REAL_DAIL = 30.0 * COV
NOW = datetime.now(timezone.utc)
DATA = Path(r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\data')
TWEETS = DATA / 'tweets_latest.json'
tweets = json.loads(TWEETS.read_text('utf-8')).get('tweets', []) if TWEETS.exists() else []
print('Tweets:', len(tweets))
MARKETS = [
    ['apr14-21', 'Elon Apr14-21 >190', 190, '2026-04-14', '2026-04-21', 116],
    ['apr17-24', 'Elon Apr17-24 >200', 200, '2026-04-17', '2026-04-24', 7],
    ['may2026', 'Elon May2026 >800', 800, '2026-05-01', '2026-05-31', 0],
]
def parse_ts(s):
    if not s: return None
    s = s.replace('Z', '+00:00')
    try: return datetime.fromisoformat(s)
    except: return None
def cnt(twt, ws, we):
    ws_d = datetime.fromisoformat(ws + 'T00:00:00+00:00')
    we_d = datetime.fromisoformat(we + 'T23:59:59+00:00')
    n = 0
    for t in twt:
        dt = parse_ts(t.get('ts') or '')
        if dt and ws_d <= dt <= we_d: n += 1
    return n
def kelly(e, p):
    if e <= 0 or e >= 1: return 0
    b = 1.0/e - 1.0
    if b <= 0: return 0
    return max(0, (b*p - (1-p)) / b)
def sim(cur, tgt, days):
    import random
    if days <= 0: return 1.0 if cur >= tgt else 0.0
    sc = [('bear', REAL_DAIL*0.7, 0.2), ('base', REAL_DAIL, 0.5), ('bull', REAL_DAIL*1.5, 0.3)]
    all_vw, tw = [], 0
    prs = {}
    for nm, rt, wt in sc:
        vs = [cur + random.poisson(rt*days) for _ in range(30000)]
        pr = sum(1 for v in vs if v >= tgt) / 30000
        prs[nm] = round(pr, 4)
        all_vw.extend((v, wt) for v in vs)
        tw += wt * 30000
    pw = sum(w for v, w in all_vw if v >= tgt) / tw
    return round(pw, 4), prs
DATA.mkdir(exist_ok=True)
OUT = DATA.parent / 'output'
OUT.mkdir(exist_ok=True)
ALL_RES = []
for mid, q, tgt, ws, we, xsnap in MARKETS:
    conf = cnt(tweets, ws, we)
    we_d = datetime.fromisoformat(we + 'T23:59:59+00:00')
    days_r = max((we_d - NOW).total_seconds() / 86400.0, 0)
    rem = max(tgt - conf, 0)
    req = rem / days_r if days_r > 0 else 999
    p_yes, scen = sim(conf, tgt, days_r)
    edge = p_yes - 0.50
    kf = kelly(0.50, p_yes)
    print(f'=== {q} ===')
    print(f'  Conf: {conf} | xtracker: {xsnap} | Rem: {rem} in {days_r:.1f}d | req: {req:.1f}/d | real: {REAL_DAIL:.1f}/d')
    for nm, pr in scen.items(): print(f'  MC {nm}: {pr*100:.0f}%')
    print(f'  -> P(yes)={p_yes*100:.0f}% Edge={edge*100:+.1f}% Kelly={kf*100:.1f}%')
    res = {'id': mid, 'conf': conf, 'rem': rem, 'days_r': round(days_r, 1), 'req': round(req, 1), 'p_yes': round(p_yes, 4), 'edge': round(edge, 4), 'kelly': round(kf, 4), 'scen': scen}
    (OUT / f'{mid}.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    ALL_RES.append({'id': mid, 'q': q, 'tgt': tgt, **res})
(OUT / 'latest.json').write_text(json.dumps(ALL_RES, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Summary: {OUT / "latest.json"}')
"@

Write-Host "Done"