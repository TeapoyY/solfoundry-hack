#!/usr/bin/env python3
"""
Browser-based tweet collector using OpenClaw's Python->PowerShell->browser relay.
This script is called by the hourly cron job. It uses subprocess to invoke
PowerShell scripts that call the browser tool via the OpenClaw gateway.

Collection flow:
  1. Navigate to x.com/home
  2. 循环 n 次: evaluate JS → parse → scroll
  3. Save to tweets_latest.json
  4. Store to SQLite
  5. Run analysis
"""
import asyncio
import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "output"
PY = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"

TARGET_ID = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
CHROME_PS = r"C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"

EXTRACT_JS = (
    "(function(){var r=[];var a=document.querySelectorAll('article[role=article]');"
    "for(var i=0;i<a.length;i++){var el=a[i];var pid='';var ls=el.querySelectorAll('a[href]');"
    "for(var j=0;j<ls.length;j++){var m=ls[j].href.match(/\\\\/status\\\\/(\\\\d+)/);if(m){pid=m[1];break;}}"
    "var t=el.querySelector('time');var ts=t?(t.getAttribute('datetime')||''):'';"
    "var txt=el.querySelector('[data-testid=tweetText]');var tx=txt?(txt.innerText||''):'';"
    "var like=el.querySelector('[data-testid=like]');var ln=like?(like.innerText||'0').replace(/,/g,''):'0';"
    "var rt=el.querySelector('[data-testid=retweet]');var rn=rt?(rt.innerText||'0').replace(/,/g,''):'0';"
    "r.push({p:pid,t:ts,x:tx.substring(0,100),ln:ln,rn:rn});}"
    "return JSON.stringify(r);})()"
)

SCROLL_JS = "window.scrollTo(0,document.body.scrollHeight);"


def run_ps(script: str, timeout=60) -> str:
    """Run PowerShell script, return stdout."""
    r = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, timeout=timeout,
        encoding="utf-8", errors="replace"
    )
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def browser_act(js: str, timeout_ms=25000) -> dict:
    """Call browser act with evaluate JS."""
    script = f'''
$ErrorActionPreference = 'Stop'
$result = & "{CHROME_PS}" browser act --json `
    --target host `
    --profile chrome `
    --targetId {TARGET_ID} `
    --request '{{"kind": "evaluate", "fn": "{js}", "timeoutMs": {timeout_ms}}}'
Write-Output $result
'''
    stdout, stderr, rc = run_ps(script, timeout=40)
    if rc != 0 or not stdout.strip():
        return {}
    try:
        # PowerShell outputs to stderr sometimes
        text = stdout.strip() if stdout.strip() else stderr.strip()
        return json.loads(text)
    except Exception:
        return {}


def browser_navigate(url: str) -> dict:
    script = f'''
$ErrorActionPreference = 'Stop'
$result = & "{CHROME_PS}" browser navigate --json `
    --target host `
    --profile chrome `
    --targetId {TARGET_ID} `
    --url "{url}"
Write-Output $result
'''
    stdout, stderr, rc = run_ps(script, timeout=30)
    if rc != 0:
        return {}
    try:
        return json.loads(stdout.strip() or stderr.strip())
    except Exception:
        return {}


def parse_tweet(raw, ref):
    pid = raw.get("p", "")
    if not pid:
        return None
    ts_str = raw.get("t", "")
    dt = None
    if ts_str:
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            pass
    if not dt:
        # Try relative time
        pass
    if not dt:
        return None
    wd = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    s = raw.get("ln", "0").strip().replace(",", "")
    mult = 1
    if "K" in s.upper():
        mult, s = 1000, s.upper().replace("K", "")
    elif "M" in s.upper():
        mult, s = 1000000, s.upper().replace("M", "")
    try:
        likes = int(float(s) * mult)
    except Exception:
        likes = 0
    s = raw.get("rn", "0").strip().replace(",", "")
    mult = 1
    if "K" in s.upper():
        mult, s = 1000, s.upper().replace("K", "")
    elif "M" in s.upper():
        mult, s = 1000000, s.upper().replace("M", "")
    try:
        rts = int(float(s) * mult)
    except Exception:
        rts = 0
    return {
        "post_id": pid,
        "timestamp": dt.isoformat().replace("+00:00", "Z"),
        "text": raw.get("x", ""),
        "hour": dt.hour,
        "weekday": wd[dt.weekday()],
        "likes": likes,
        "retweets": rts,
        "replies": 0,
        "views": 0,
        "is_pinned": False,
        "has_media": False,
    }


def num(s):
    if not s:
        return 0
    s = s.strip().replace(",", "")
    mult = 1
    if "K" in s.upper():
        mult, s = 1000, s.upper().replace("K", "")
    elif "M" in s.upper():
        mult, s = 1000000, s.upper().replace("M", "")
    try:
        return int(float(s) * mult)
    except Exception:
        return 0


def collect(n_scrolls=8):
    """Main collection: navigate + scroll + extract."""
    print("Navigating to x.com/home...")
    browser_navigate("https://x.com/home")
    time.sleep(3)

    all_tweets = []
    all_pids = set()
    seen = set()

    for i in range(n_scrolls):
        time.sleep(2)
        result = browser_act(EXTRACT_JS, timeout_ms=25000)
        raw_str = result.get("result", "")
        if not raw_str:
            print(f"  Scroll {i+1}: no result")
            time.sleep(1)
            continue
        try:
            raw_tweets = json.loads(raw_str)
        except Exception:
            print(f"  Scroll {i+1}: JSON parse error")
            continue

        new_count = 0
        for raw in raw_tweets:
            pid = raw.get("p", "")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            all_pids.add(pid)
            p = parse_tweet(raw, datetime.now(timezone.utc))
            if p:
                all_tweets.append(p)
                new_count += 1

        print(f"  Scroll {i+1}: +{new_count} new, total pids: {len(all_pids)}")

        if i < n_scrolls - 1:
            browser_act(SCROLL_JS, timeout_ms=5000)
            time.sleep(2)

    # Sort newest first
    all_tweets.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_tweets, list(all_pids)


def store_and_analyze(tweets):
    """Store tweets to SQLite and run analysis."""
    # Save JSON
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DATA_DIR / "tweets_latest.json"
    save = {
        "tweets": tweets,
        "count": len(tweets),
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }
    json_path.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {json_path} ({len(tweets)} tweets)")

    # Store to SQLite
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.database import TweetDB
    from collect import store_tweets
    db = TweetDB()
    n, parsed = store_tweets(db, tweets)
    total = db.total_tweets()
    print(f"SQLite: +{n} new, total: {total}")

    # Run analysis
    from src.analyzer import analyze
    results = analyze(db)

    # Save results
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = OUT_DIR / f"snapshot_{ts}.json"
    latest = OUT_DIR / "latest_snapshot.json"
    save_data = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "new_tweets": len(tweets),
        "total_in_db": total,
        "results": results,
    }
    for f in [fp, latest]:
        f.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {fp}")

    return results


def send_feishu_alert(results):
    """Send Feishu alert if significant edge found."""
    significant = [r for r in results if r["edge"] > 0.15]
    if not significant:
        print("No significant edge (>15%), skipping Feishu alert.")
        return

    lines = ["*Polymarket Elon — 实时信号*\n"]
    for r in significant:
        action = "BUY_YES" if r["p_yes"] > 0.5 else "BUY_NO"
        lines.append(f"*#{r['market_id']}* ({r['question'][:30]}...)")
        lines.append(f"  确认: {r['confirmed']} tweets | P(YES): {r['p_yes']*100:.0f}%")
        lines.append(f"  Edge: {r['edge_pct']} | Kelly: {r['kelly_quarter']*100:.1f}%")
        lines.append(f"  Action: {action}\n")

    msg = "\n".join(lines)
    # Send via message tool would go here
    # For now, just print
    print("FEISHU ALERT:", msg)


if __name__ == "__main__":
    n_scrolls = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"Collecting with {n_scrolls} scrolls...")
    tweets, pids = collect(n_scrolls=n_scrolls)
    print(f"Collected: {len(tweets)} tweets, {len(pids)} unique pids")
    if tweets:
        results = store_and_analyze(tweets)
        send_feishu_alert(results)
    else:
        print("No tweets collected!")
