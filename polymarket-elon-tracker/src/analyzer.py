"""
Market Analyzer — computes probabilities for Polymarket Elon tweet-count markets.
"""
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Coverage calibration ──────────────────────────────────────────
# xtracker Apr16-18 confirmed: 42 tweets
# Our Browser Relay Apr16-18: 22 tweets
# => COVERAGE_RATIO = 42/22 ≈ 1.91
COVERAGE = 42.0 / 22.0

# ── Market definitions ─────────────────────────────────────────────
MARKETS = [
    {
        "id": "apr14-21",
        "question": "Elon Musk tweets April 14–21, 2026? (Over 190?)",
        "target": 190,
        "ws": "2026-04-14T00:00:00Z",
        "we": "2026-04-21T23:59:59Z",
        "xtracker_snapshot": 116,   # confirmed count at snapshot
        "snapshot_time": "2026-04-18T02:15:00+08:00",
    },
    {
        "id": "apr17-24",
        "question": "Elon Musk tweets April 17–24, 2026? (Over 200?)",
        "target": 200,
        "ws": "2026-04-17T00:00:00Z",
        "we": "2026-04-24T23:59:59Z",
        "xtracker_snapshot": 7,
        "snapshot_time": "2026-04-18T02:15:00+08:00",
    },
    {
        "id": "may2026",
        "question": "Elon Musk tweets May 2026? (Over 800?)",
        "target": 800,
        "ws": "2026-05-01T00:00:00Z",
        "we": "2026-05-31T23:59:59Z",
        "xtracker_snapshot": 0,
        "snapshot_time": "2026-04-18T02:15:00+08:00",
    },
]


def parse_ts(s: str):
    if not s:
        return None
    s = s.replace("Z", "+00:00").replace(" ", "T")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def cnt_window(tweets: list, ws: str, we: str) -> int:
    """Count tweets within UTC window [ws, we]."""
    ws_dt = parse_ts(ws)
    we_dt = parse_ts(we)
    if not ws_dt or not we_dt:
        return 0
    n = 0
    for t in tweets:
        ts = _get_ts(t)
        dt = parse_ts(ts)
        if dt and ws_dt <= dt <= we_dt:
            n += 1
    return n


def kelly(entry: float, prob: float) -> float:
    """
    Kelly criterion fraction for a binary outcome.
    entry: decimal price (e.g. 0.50 for even odds)
    prob: true probability of success (0-1)
    """
    if entry <= 0 or entry >= 1 or prob <= 0:
        return 0.0
    b = 1.0 / entry - 1.0
    q = 1.0 - prob
    if b <= 0:
        return 0.0
    f = (b * prob - q) / b
    return max(0.0, f)


def mc3(cur: int, tgt: int, days: float, daily: float, n: int = 30000):
    """
    3-scenario Monte Carlo.
    Scenarios: bear (0.7x real_daily, 20%), base (1x, 50%), bull (1.5x, 30%)
    Poisson(lam) approximated by Normal(lam, sqrt(lam)) for speed.
    Returns: (P(reach target), mean tweets, scenario probabilities dict)
    """
    if days <= 0:
        return (1.0 if cur >= tgt else 0.0, float(cur), {})

    scenarios = [
        ("bear", daily * 0.7, 0.20),
        ("base", daily, 0.50),
        ("bull", daily * 1.5, 0.30),
    ]

    all_vw = []
    total_w = 0
    prs = {}

    rng = random.Random(x=42)  # reproducible seed

    for name, rate, wt in scenarios:
        lam = rate * days
        # Normal approx to Poisson: N(lam, sqrt(lam))
        std = max(math.sqrt(lam), 0.5)
        vs = [max(0, int(round(cur + rng.gauss(lam, std)))) for _ in range(n)]
        pr = sum(1 for v in vs if v >= tgt) / n
        prs[name] = round(pr, 4)
        all_vw.extend((v, wt) for v in vs)
        total_w += wt * n

    pw = sum(w for v, w in all_vw if v >= tgt) / total_w
    mw = sum(v * w for v, w in all_vw) / total_w
    return round(pw, 4), round(mw, 1), prs


def _get_ts(t) -> str:
    """Extract timestamp from a tweet row (tuple or dict)."""
    if isinstance(t, dict):
        return t.get("timestamp", "")
    if isinstance(t, (list, tuple)) and len(t) > 1:
        return str(t[1])
    return ""


def velocity_stats(tweets: list, now_utc: datetime) -> dict:
    """
    Compute velocity stats from tweet list.
    tweets: list of (post_id, timestamp, ...) sorted newest-first.
    """
    hourly_bins = {h: 0 for h in range(24)}
    daily_counts = {}

    for t in tweets:
        ts = _get_ts(t)
        dt = parse_ts(ts)
        if not dt:
            continue
        hourly_bins[dt.hour] += 1
        day_key = dt.strftime("%Y-%m-%d")
        daily_counts[day_key] = daily_counts.get(day_key, 0) + 1

    # Velocity over various windows
    cutoff_base = now_utc.replace(minute=0, second=0, microsecond=0)
    velocities = {}
    for h in [1, 3, 6, 12, 24, 48, 72]:
        cutoff = cutoff_base - datetime.timedelta(hours=h)
        count = sum(
            1 for t in tweets
            if parse_ts(_get_ts(t)) is not None and parse_ts(_get_ts(t)) >= cutoff
        )
        velocities[h] = {"count": count, "rate_per_day": round(count / h * 24, 1) if h > 0 else 0}

    return {"hourly": hourly_bins, "daily": daily_counts, "velocities": velocities}


def analyze(db) -> list:
    """
    Main analysis: read all tweets from db, compute market probabilities.

    Returns list of market result dicts.
    """
    tweets = db.get_all_tweets()
    now_utc = datetime.now(timezone.utc)
    total = len(tweets)
    real_daily = round(30.0 * COVERAGE, 1)  # ~57.3/day

    results = []
    for m in MARKETS:
        mid = m["id"]
        tgt = m["target"]
        ws, we = m["ws"], m["we"]

        conf = cnt_window(tweets, ws, we)
        conf_est = int(conf * COVERAGE)

        we_dt = parse_ts(we)
        days_rem = max((we_dt - now_utc).total_seconds() / 86400.0, 0) if we_dt else 0
        rem = max(tgt - conf, 0)
        req_rate = round(rem / days_rem, 1) if days_rem > 0 else 999

        p_yes, mean_v, scen_p = mc3(conf, tgt, days_rem, real_daily)
        edge = p_yes - 0.50
        kf_full = kelly(0.50, p_yes)

        # Velocity ratio (higher = more bullish)
        vel_ratio = round(real_daily / req_rate, 2) if req_rate > 0 and req_rate < 999 else 99.0

        result = {
            "market_id": mid,
            "question": m["question"],
            "target": tgt,
            "window_start": ws[:10],
            "window_end": we[:10],
            "confirmed": conf,
            "confirmed_est": conf_est,
            "remaining": rem,
            "days_remaining": round(days_rem, 2),
            "required_rate": req_rate,
            "real_daily_rate": real_daily,
            "velocity_ratio": vel_ratio,
            "p_yes": p_yes,
            "edge": round(edge, 4),
            "edge_pct": f"{edge*100:+.1f}%",
            "kelly_full": round(kf_full, 4),
            "kelly_half": round(kf_full * 0.5, 4),
            "kelly_quarter": round(kf_full * 0.25, 4),
            "mc_scenarios": scen_p,
            "mean_tweets": mean_v,
            "xtracker_snapshot": m["xtracker_snapshot"],
            "coverage_ratio": round(COVERAGE, 3),
            "total_tweets_in_db": total,
            "analysis_time": now_utc.isoformat(),
        }
        results.append(result)

    return results


def print_results(results: list):
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*70}")
    print(f"  xTracker Clone — Real-time Analysis  ({now})")
    print(f"  DB tweets: {results[0]['total_tweets_in_db']} | Cov: {COVERAGE:.3f}x | "
          f"Real daily: ~{results[0]['real_daily_rate']}/day")
    print(f"{'='*70}\n")

    for r in results:
        print(f"[{r['market_id']}] {r['question']}")
        print(f"  Window: {r['window_start']} ~ {r['window_end']}")
        print(f"  Counted: {r['confirmed']} tweets  (est real: {r['confirmed_est']})")
        print(f"  Remaining: {r['remaining']} in {r['days_remaining']:.1f}d | "
              f"req {r['required_rate']}/day | real ~{r['real_daily_rate']}/day")
        print(f"  Velocity ratio: {r['velocity_ratio']}x  (1.0=break-even, >1=bullish)")
        print(f"  MC scenarios:")
        for nm, pr in r["mc_scenarios"].items():
            print(f"    {nm:6s}: {pr*100:5.0f}%")
        print(f"  --> P(YES)={r['p_yes']*100:5.0f}%  Edge={r['edge_pct']}  "
              f"Kelly={r['kelly_quarter']*100:.1f}%")
        print()
