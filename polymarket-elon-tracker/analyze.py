#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import json, random, math

PROJECT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT / "data"
OUT_DIR = PROJECT / "output"
OUT_DIR.mkdir(exist_ok=True)

# Market definitions (matches xtracker windows)
MARKETS = [
    {"id": "apr14-21", "q": "Elon Apr14-21 >190", "tgt": 190, "ws": "2026-04-14", "we": "2026-04-21", "xtrack": 116},
    {"id": "apr17-24", "q": "Elon Apr17-24 >200", "tgt": 200, "ws": "2026-04-17", "we": "2026-04-24", "xtrack": 7},
    {"id": "may2026", "q": "Elon May2026 >800", "tgt": 800, "ws": "2026-05-01", "we": "2026-05-31", "xtrack": 0},
]

# Coverage: xtracker Apr16-18=42, our Browser Relay Apr16-18=22
# Also verified with 269-tweet run: coverage=1.91x
COV = 1.91
REAL_DAILY = 30.0 * COV  # ~57/day real

def parse_ts(s):
    if not s:
        return None
    s = s.replace("Z", "+00:00").replace(" ", "T")
    try:
        return datetime.fromisoformat(s)
    except:
        return None

def cnt(tweets, ws_str, we_str):
    ws = datetime.fromisoformat(ws_str + "T00:00:00+00:00")
    we = datetime.fromisoformat(we_str + "T23:59:59+00:00")
    n = 0
    for t in tweets:
        ts = t.get("ts", "") or t.get("timestamp", "") or ""
        dt = parse_ts(ts)
        if dt and ws <= dt <= we:
            n += 1
    return n

def kelly(entry, prob):
    if entry <= 0 or entry >= 1:
        return 0.0
    odds = 1.0 / entry
    b = odds - 1.0
    q = 1.0 - prob
    if b <= 0:
        return 0.0
    f = (b * prob - q) / b
    return max(0.0, f)

def mc3(cur, tgt, days, daily):
    if days <= 0:
        return 1.0 if cur >= tgt else 0.0
    scens = [
        ("bear", daily * 0.7, 0.20),
        ("base", daily, 0.50),
        ("bull", daily * 1.5, 0.30),
    ]
    all_vw, total_w = [], 0
    prs = {}
    for name, rate, wt in scens:
        lam = rate * days
        vs = [cur + random.poisson(lam) for _ in range(30000)]
        pr = sum(1 for v in vs if v >= tgt) / 30000
        prs[name] = round(pr, 4)
        all_vw.extend((v, wt) for v in vs)
        total_w += wt * 30000
    pw = sum(w for v, w in all_vw if v >= tgt) / total_w
    mw = sum(v * w for v, w in all_vw) / total_w
    return round(pw, 4), round(mw, 1), prs

def analyze():
    tweets_path = DATA_DIR / "tweets_latest.json"
    if tweets_path.exists():
        tweets = json.loads(tweets_path.read_text("utf-8")).get("tweets", [])
    else:
        tweets = []
    print(f"Tweets: {len(tweets)} loaded")

    now_utc = datetime.now(timezone.utc)
    print(f"Coverage: {COV}x | Real daily: {REAL_DAILY:.1f}/day\n")

    results = []
    for m in MARKETS:
        ws_str, we_str = m["ws"], m["we"]
        tgt = m["tgt"]
        conf = cnt(tweets, ws_str, we_str)
        conf_est = int(conf * COV)

        # days remaining
        we_dt = datetime.fromisoformat(we_str + "T23:59:59+00:00")
        days_r = max((we_dt - now_utc).total_seconds() / 86400.0, 0.0)
        rem = max(tgt - conf, 0)
        req = rem / days_r if days_r > 0 else 999

        # MC
        p_yes, mean_v, scen_p = mc3(conf, tgt, days_r, REAL_DAILY)
        edge = p_yes - 0.50
        kf = kelly(0.50, p_yes)

        print(f"=== {m['q']} ===")
        print(f"  Confirmed: {conf} (est {conf_est}) | xtracker: {m['xtrack']}")
        print(f"  Remaining: {rem} in {days_r:.1f}d | req: {req:.1f}/day | real: {REAL_DAILY:.1f}/day")
        for n, pr in scen_p.items():
            print(f"  MC {n}: {pr*100:.0f}%")
        print(f"  -> P(yes)={p_yes*100:.0f}% Edge={edge*100:+.1f}% Kelly={kf*100:.1f}%")

        results.append({
            "id": m["id"],
            "confirmed": conf,
            "confirmed_est": conf_est,
            "target": tgt,
            "remaining": rem,
            "days_remaining": round(days_r, 2),
            "required_rate": round(req, 1),
            "real_daily": round(REAL_DAILY, 1),
            "p_yes": p_yes,
            "edge": round(edge, 4),
            "edge_pct": f"{edge*100:+.1f}%",
            "kelly_full": round(kf, 4),
            "kelly_half": round(kf * 0.5, 4),
            "kelly_quarter": round(kf * 0.25, 4),
            "mc_scenarios": scen_p,
            "xtracker_snapshot": m["xtrack"],
            "coverage": COV,
        })

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUT_DIR / f"analysis_{ts}.json"
    latest = OUT_DIR / "analysis_latest.json"
    for fp in [out, latest]:
        fp.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {out}")
    return results

if __name__ == "__main__":
    analyze()
