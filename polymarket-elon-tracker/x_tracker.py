#!/usr/bin/env python3
"""
xTracker Clone - Polymarket Elon Musk Tweet Counter
抓取方法: Browser Relay Chrome 已登录态
"""
import json, re, sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional

PROJECT_ROOT = Path(__file__).parent.resolve()

MARKETS = [
    {
        "id": "elon-apr14-21",
        "question": "Elon Musk tweets Apr 14-21, 2026? (Over 190?)",
        "target": 190,
        "window_utc": ("2026-04-14T00:00:00Z", "2026-04-21T23:59:59Z"),
        "xtracker_snapshot": 116,
        "snapshot_time": "2026-04-18T02:15+08:00",
    },
    {
        "id": "elon-apr17-24",
        "question": "Elon Musk tweets Apr 17-24, 2026? (Over 200?)",
        "target": 200,
        "window_utc": ("2026-04-17T00:00:00Z", "2026-04-24T23:59:59Z"),
        "xtracker_snapshot": 7,
        "snapshot_time": "2026-04-18T02:15+08:00",
    },
    {
        "id": "elon-may2026",
        "question": "Elon Musk tweets May 2026? (Over 800?)",
        "target": 800,
        "window_utc": ("2026-05-01T00:00:00Z", "2026-05-31T23:59:59Z"),
        "xtracker_snapshot": 0,
        "snapshot_time": None,
    },
]

COVERAGE_RATIO = 42 / 22  # xtracker Apr16-18 = 42, our Apr16-18 = 22


def parse_ts(ts_str: str) -> Optional[datetime]:
    if not ts_str or ts_str == "none":
        return None
    ts_clean = ts_str.replace("Z", "+00:00").replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(ts_clean[:19], fmt.replace("Z", "").replace("%Y-%m-%dT", "%Y-%m-%dT")
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # Try datetime.fromisoformat as fallback
    try:
        return datetime.fromisoformat(ts_clean)
    except ValueError:
        pass
    return None


def count_window(tweets: List, ws_str: str, we_str: str) -> int:
    try:
        ws = datetime.fromisoformat(ws_str.replace("Z", "+00:00"))
        we = datetime.fromisoformat(we_str.replace("Z", "+00:00"))
    except ValueError:
        return 0
    count = 0
    for t in tweets:
        ts_str = t.get("ts") or t.get("timestamp") or t.get("tsAttr", "")
        dt = parse_ts(ts_str)
        if dt and ws <= dt <= we:
            count += 1
    return count


def kelly(entry: float, prob: float) -> float:
    if entry <= 0 or entry >= 1:
        return 0.0
    odds = 1 / entry
    b = odds - 1
    p = prob
    q = 1 - p
    if b <= 0:
        return 0.0
    f = (b * p - q) / b
    return max(0.0, f)


def monte_carlo(current: int, target: int, days: float,
              real_daily: float = 30.0, n: int = 30000) -> dict:
    import math
    try:
        import numpy as np
    except ImportError:
        np = None

    if days <= 0:
        return {"p_reach": 1.0 if current >= target else 0.0,
                "mean": current, "scenarios": {}}

    scenarios = [
        ("bear", real_daily * 0.7, 0.20),
        ("base", real_daily,       0.50),
        ("bull", real_daily * 1.5, 0.30),
    ]

    all_results = []
    p_reaches = {}

    for name, rate, weight in scenarios:
        if np:
            lam = rate * days
            samples = np.random.poisson(lam, size=n)
            final = current + samples
        else:
            import random
            final = [current + sum(1 for _ in range(max(0, int(rate * days))) for _ in range(n)]

        p_reach = sum(1 for v in final if v >= target) / len(final)
        p_reaches[name] = round(p_reach, 4)
        all_results.extend((v, weight) for v in final)

    total_w = sum(w for _, w in all_results)
    p_reach_weighted = sum(w for v, w in all_results if v >= target) / total_w
    weighted_mean = sum(v * w for v, w in all_results) / total_w

    return {
        "p_reach": round(p_reach_weighted, 4),
        "mean": round(weighted_mean, 1),
        "scenarios": {n: {"p_reach": p_reaches[n], "rate": r, "weight": w}
                     for n, r, w in scenarios},
    }


def analyze_market(mkt: dict, tweets: List, real_daily: float = 30.0) -> dict:
    ws, we = mkt["window_utc"]
    confirmed = count_window(tweets, ws, we)

    try:
        we_dt = datetime.fromisoformat(we.replace("Z", "+00:00"))
    except ValueError:
        days_remaining = 0.0
    else:
        now = datetime.now(timezone.utc)
        days_remaining = max((we_dt - now).total_seconds() / 86400, 0)

    remaining = max(mkt["target"] - confirmed, 0)
    required_rate = remaining / days_remaining if days_remaining > 0 else 999

    mc = monte_carlo(confirmed, mkt["target"], days_remaining,
                     real_daily=real_daily * COVERAGE_RATIO)
    p_yes = mc["p_reach"]

    yes_price = 0.50
    edge = p_yes - yes_price
    kelly_f = kelly(yes_price, p_yes)

    return {
        "market_id": mkt["id"],
        "question": mkt["question"],
        "target": mkt["target"],
        "window": f"{ws[:10]} ~ {we[:10]}",
        "confirmed_count": confirmed,
        "confirmed_est": int(confirmed * COVERAGE_RATIO),
        "xtracker_snapshot": mkt["xtracker_snapshot"],
        "remaining": remaining,
        "days_remaining": round(days_remaining, 2),
        "required_rate": round(required_rate, 1),
        "p_yes": round(p_yes, 4),
        "edge": round(edge, 4),
        "edge_pct": f"{edge*100:+.1f}%",
        "kelly_full": round(kelly_f, 4),
        "kelly_half": round(kelly_f * 0.5, 4),
        "kelly_quarter": round(kelly_f * 0.25, 4),
        "mc": mc,
        "coverage_ratio": COVERAGE_RATIO,
        "real_daily_used": round(real_daily * COVERAGE_RATIO, 1),
    }


def format_report(results: List[dict]) -> str:
    sep = "=" * 72
    lines = [sep,
             f"  xTracker Clone - Polymarket Elon Analysis  {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
             sep]
    for r in results:
        lines.append(f"\n{'-'*72}")
        lines.append(f"  {r['question']}")
        lines.append(f"  窗口: {r['window']} | 目标: {r['target']} | 剩余: {r['remaining']}条/{r['days_remaining']}天")
        lines.append(f"  确认: {r['confirmed_count']}条 (覆盖率校正后≈{r['confirmed_est']}条)")
        if r['xtracker_snapshot'] > 0:
            lines.append(f"  xtracker对照: {r['xtracker_snapshot']}条")
        lines.append("")
        lines.append(f"  {'选项':<8} {'价格(隐含)':>14} {'真实概率':>12} {'边缘':>10} {'Kelly全':>10}")
        lines.append(f"  {'-'*8} {'-'*14} {'-'*12} {'-'*10} {'-'*10}")
        lines.append(f"  {'YES':<8} {0.50:>14.0%} {r['p_yes']:>12.1%} {r['edge_pct']:>10} {r['kelly_full']*100:>9.1f}%")
        lines.append(f"  {'NO':<8} {0.50:>14.0%} {1-r['p_yes']:>12.1%} {-r['edge']:>10.1%} {'—':>10}")
        lines.append("")
        mc = r.get("mc", {})
        sc = mc.get("scenarios", {})
        for name in ("bear", "base", "bull"):
            if name in sc:
                s = sc[name]
                lines.append(f"    {name:6s}: rate={s['rate']:.1f}/d, P(达成)={s['p_reach']*100:.0f}%")
        lines.append(f"  ✅ {r['market_id']}: P={r['p_yes']*100:.0f}%, Edge={r['edge_pct']}, Kelly={r['kelly_full']*100:.1f}%")
    lines.append(f"\n{sep}")
    lines.append(f"  覆盖率校正系数: {COVERAGE_RATIO:.2f}x (xtracker Apr16-18: 42 / 我们: 22)")
    lines.append(sep)
    return "\n".join(lines)


if __name__ == "__main__":
    # 尝试加载最新推文
    tweets = []
    latest = PROJECT_ROOT / "data" / "tweets_latest.json"
    if latest.exists():
        try:
            tweets = json.loads(latest.read_text("utf-8")).get("tweets", [])
            print(f"Loaded {len(tweets)} tweets from cache")
        except Exception as e:
            print(f"Cache load error: {e}")

    if not tweets:
        print("No tweets. Run Browser Relay collector first.")
        sys.exit(1)

    # 分析
    results = [analyze_market(m, tweets) for m in MARKETS]
    print(format_report(results))

    # 保存
    out_dir = PROJECT_ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = out_dir / f"analysis_{ts}.json"
    latest_out = out_dir / "analysis_latest.json"
    for fpath in [fp, latest_out]:
        fpath.write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    print(f"\nSaved: {fp}")
