#!/usr/bin/env python3
"""
Real-time tweet collector + analyzer for Polymarket Elon markets.
Uses OpenClaw browser tool for CDP evaluate (via act action).

Flow:
  1. This script runs as a BACKGROUND cron/process
  2. Writes COLLECT_MARKER when ready to collect
  3. Main assistant sees marker, calls browser tool to collect
  4. Writes results to SHARED_JSON
  5. This script reads results, stores to DB, runs analysis
  6. Repeat every INTERVAL_MINUTES
"""
import asyncio
import json
import os
import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import TweetDB
from src.analyzer import analyze, print_results, COVERAGE

# ── Paths ───────────────────────────────────────────────────────────────────
DATA_DIR   = PROJECT_ROOT / "data"
OUT_DIR    = PROJECT_ROOT / "output"
MARKER     = DATA_DIR / ".collect_needed"
SHARED     = DATA_DIR / ".browser_result.json"
DB_PATH    = DATA_DIR / "tracker.db"

# ── Config ──────────────────────────────────────────────────────────────────
INTERVAL_MIN   = 15   # minutes between collection cycles
COLLECT_SCROLLS = 8   # scrolls per collection
COLLECT_MIN_NEW = 5   # min new tweets before stopping

TARGET_ID  = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

# JS: extract tweets from x.com home feed
EXTRACT_JS = (
    "(function(){"
    "var r=[];"
    "var a=document.querySelectorAll('article[role=article]');"
    "for(var i=0;i<a.length;i++){"
    "var el=a[i];"
    "var pid='';"
    "var ls=el.querySelectorAll('a[href]');"
    "for(var j=0;j<ls.length;j++){"
    "var m=ls[j].href.match(/\\\\/status\\\\/(\\\\d+)/);"
    "if(m){pid=m[1];break;}"
    "}"
    "var t=el.querySelector('time');"
    "var ts=t?(t.getAttribute('datetime')||''):'';"
    "var txt=el.querySelector('[data-testid=tweetText]');"
    "var tx=txt?(txt.innerText||''):'';"
    "var like=el.querySelector('[data-testid=like]');"
    "var ln=like?(like.innerText||'0').replace(/,/g,''):'0';"
    "var rt=el.querySelector('[data-testid=retweet]');"
    "var rn=rt?(rt.innerText||'0').replace(/,/g,''):'0';"
    "r.push({p:pid,t:ts,x:tx.substring(0,80),ln:ln,rn:rn});"
    "}"
    "return JSON.stringify(r);"
    "})()"
)

SCROLL_JS = "window.scrollTo(0,document.body.scrollHeight);"


def parse_relative(ts_text, ref):
    import re
    ts_text = ts_text.strip()
    m = re.search(r"(\d+)\s*(小时|天|分钟|秒)\s*前", ts_text)
    if m:
        v = int(m.group(1)); u = m.group(2)
        d = {"秒":1,"分钟":60,"小时":3600,"天":86400}
        return ref - datetime.timedelta(seconds=v*d.get(u,86400))
    m = re.search(r"(\d+)(h|d|m|s|w)\b", ts_text, re.I)
    if m:
        v = int(m.group(1)); u = m.group(2).lower()
        d = {"s":1,"m":60,"h":3600,"d":86400,"w":604800}
        return ref - datetime.timedelta(seconds=v*d.get(u,86400))
    return None


def num(s):
    if not s: return 0
    s = s.strip().replace(",","")
    mult = 1
    if "K" in s.upper(): mult, s = 1000, s.upper().replace("K","")
    elif "M" in s.upper(): mult, s = 1000000, s.upper().replace("M","")
    try: return int(float(s)*mult)
    except: return 0


def parse_tweet(raw, ref):
    pid = raw.get("p","")
    if not pid: return None
    ts_str = raw.get("t","")
    dt = None
    if ts_str:
        try: dt = datetime.fromisoformat(ts_str.replace("Z","+00:00"))
        except: pass
    if not dt: dt = parse_relative(raw.get("ttext",""), ref)
    if not dt: return None
    wd = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    return {
        "post_id": pid,
        "timestamp": dt.isoformat().replace("+00:00","Z"),
        "text": raw.get("x",""),
        "hour": dt.hour,
        "weekday": wd[dt.weekday()],
        "likes": num(raw.get("ln","0")),
        "retweets": num(raw.get("rn","0")),
        "replies": 0, "views": 0,
        "is_pinned": False, "has_media": False,
    }


def run_analysis(db):
    """Run analysis and save results."""
    results = analyze(db)
    print_results(results)

    now_iso = datetime.now(timezone.utc).isoformat()
    OUT_DIR.mkdir(exist_ok=True)

    save_data = {
        "collected_at": now_iso,
        "total_in_db": db.total_tweets(),
        "coverage_ratio": COVERAGE,
        "results": results,
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (OUT_DIR / f"snapshot_{ts}.json").write_text(
        json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "latest_snapshot.json").write_text(
        json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return results


def wait_for_marker(timeout_sec=None):
    """Wait for COLLECT_MARKER to appear."""
    start = time.time()
    while True:
        if MARKER.exists():
            # Read marker: contains collection params
            try:
                params = json.loads(MARKER.read_text("utf-8"))
            except:
                params = {}
            MARKER.unlink()
            return params
        if timeout_sec and (time.time() - start) > timeout_sec:
            return None
        time.sleep(2)


def write_marker(scrolls=COLLECT_SCROLLS, min_new=COLLECT_MIN_NEW):
    """Write marker to signal main assistant to collect."""
    DATA_DIR.mkdir(exist_ok=True)
    marker = {
        "scrolls": scrolls,
        "min_new": min_new,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    MARKER.write_text(json.dumps(marker, ensure_ascii=False), encoding="utf-8")


def read_browser_result():
    """Read collected tweets from shared JSON."""
    if not SHARED.exists():
        return []
    try:
        data = json.loads(SHARED.read_text("utf-8"))
        SHARED.unlink()
        return data.get("tweets", [])
    except Exception:
        return []


def main():
    print("=" * 60)
    print("  xTracker Clone — Real-time Collector")
    print(f"  Interval: {INTERVAL_MIN} min | Scrolls: {COLLECT_SCROLLS}")
    print(f"  DB: {DB_PATH}")
    print("=" * 60)

    db = TweetDB()
    total = db.total_tweets()
    print(f"  Existing tweets in DB: {total}")

    if total == 0:
        print("  [FIRST RUN] Requesting initial full collection...")
        write_marker(scrolls=10, min_new=5)
        params = wait_for_marker(timeout_sec=300)
        if params:
            tweets = read_browser_result()
            if tweets:
                n = db.bulk_upsert(tweets)
                print(f"  Initial collection: +{n} tweets stored")
        else:
            print("  No collection result received (timeout)")

    cycle = 0
    while True:
        cycle += 1
        now_iso = datetime.now(timezone.utc).isoformat()[:19]
        print(f"\n[Cycle #{cycle}] {now_iso} — Requesting collection...")
        write_marker(scrolls=COLLECT_SCROLLS, min_new=COLLECT_MIN_NEW)

        # Wait for assistant to process (with timeout)
        params = wait_for_marker(timeout_sec=INTERVAL_MIN * 60)
        if not params:
            print("  Timeout waiting for collection, retrying...")
            continue

        tweets = read_browser_result()
        if tweets:
            n = db.bulk_upsert(tweets)
            print(f"  Stored: +{n} tweets")
        else:
            print("  No new tweets collected this cycle")

        total = db.total_tweets()
        print(f"  Total in DB: {total}")

        # Run analysis
        if total > 0:
            results = run_analysis(db)
            # Send Feishu alert if significant
            for r in results:
                if r["edge"] > 0.15:  # >15% edge
                    print(f"  [SIGNAL] {r['market_id']}: {r['edge_pct']} edge detected!")
        else:
            print("  Skipping analysis (no data)")

        print(f"  Sleeping {INTERVAL_MIN} min...")
        time.sleep(INTERVAL_MIN * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
