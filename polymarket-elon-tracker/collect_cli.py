#!/usr/bin/env python3
"""
Real-time tweet collector using openclaw CLI browser evaluate.
Uses subprocess to call: openclaw browser evaluate --fn "..."
Uses subprocess to call: openclaw browser act --request "{...}"

No CDP WebSocket needed - CLI handles auth automatically.
"""
import json
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "output"
OC = r"C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
PY = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
PROFILE = "chrome"
N_SCROLLS = 8


def run(args, timeout=40):
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command",
           *[OC] + args]
    r = subprocess.run(cmd, capture_output=True, text=True,
                        timeout=timeout, encoding="utf-8", errors="replace")
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def beval(js, timeout_ms=25000):
    """Browser evaluate JS, return parsed JSON."""
    stdout, stderr, rc = run([
        "browser", "evaluate",
        "--fn", js,
        "--target-id", TARGET,
        "--browser-profile", PROFILE,
        "--timeout", str(timeout_ms),
        "--json"
    ], timeout=timeout_ms // 1000 + 10)
    if rc != 0:
        return None
    try:
        return json.loads(stdout)
    except Exception:
        try:
            return json.loads(stderr)
        except Exception:
            return None


def bnav(url):
    """Navigate browser to URL."""
    stdout, stderr, rc = run([
        "browser", "navigate",
        "--target-id", TARGET,
        "--browser-profile", PROFILE,
        "--url", url,
        "--json"
    ], timeout=30)
    if rc != 0:
        return None
    try:
        return json.loads(stdout)
    except Exception:
        return None


def bscroll():
    """Scroll to bottom."""
    return beval("window.scrollTo(0,document.body.scrollHeight)", timeout_ms=5000)


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
        return None

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

    wd = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return {
        "post_id": pid,
        "timestamp": dt.isoformat().replace("+00:00", "Z"),
        "text": raw.get("x", ""),
        "hour": dt.hour,
        "weekday": wd[dt.weekday()],
        "likes": num(raw.get("ln", "0")),
        "retweets": num(raw.get("rn", "0")),
        "replies": 0,
        "views": 0,
        "is_pinned": False,
        "has_media": False,
    }


EXTRACT = (
    "(function(){"
    "var r=[];"
    "var a=document.querySelectorAll('article[role=article]');"
    "for(var i=0;i<a.length;i++){"
    "var el=a[i];var pid='';"
    "var ls=el.querySelectorAll('a[href]');"
    "for(var j=0;j<ls.length;j++){"
    "var m=ls[j].href.match(/\\/status\\/(\\d+)/);"
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
    "r.push({p:pid,t:ts,x:tx.substring(0,100),ln:ln,rn:rn});"
    "}"
    "return JSON.stringify(r);"
    "})()"
)


def collect(n_scrolls=N_SCROLLS):
    """Navigate + scroll + extract tweets. Returns (tweets, pids)."""
    print("Navigating to x.com/home...")
    bnav("https://x.com/home")
    time.sleep(3)

    all_tweets = []
    seen = set()
    ref = datetime.now(timezone.utc)

    for i in range(n_scrolls):
        time.sleep(2)
        result = beval(EXTRACT, timeout_ms=25000)
        if not result:
            print(f"  Scroll {i+1}: no result")
            time.sleep(1)
            continue

        raw_str = result.get("result", "")
        if not raw_str:
            print(f"  Scroll {i+1}: empty result")
            continue

        try:
            raw_tweets = json.loads(raw_str)
        except Exception:
            print(f"  Scroll {i+1}: JSON parse error")
            continue

        new = 0
        for raw in raw_tweets:
            pid = raw.get("p", "")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            p = parse_tweet(raw, ref)
            if p:
                all_tweets.append(p)
                new += 1

        print(f"  Scroll {i+1}: +{new} new, total: {len(all_tweets)}")

        if i < n_scrolls - 1:
            bscroll()
            time.sleep(2)

    all_tweets.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_tweets


def store_and_analyze(tweets):
    """Store tweets to SQLite, run analysis, save results."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DATA_DIR / "tweets_latest.json"
    save = {
        "tweets": tweets,
        "count": len(tweets),
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }
    json_path.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")

    sys.path.insert(0, str(PROJECT_ROOT))
    from src.database import TweetDB
    from collect import store_tweets
    db = TweetDB()
    n, parsed = store_tweets(db, tweets)
    total = db.total_tweets()
    print(f"Stored: +{n}, total: {total}")

    from src.analyzer import analyze, COVERAGE
    results = analyze(db)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = OUT_DIR / f"snapshot_{ts}.json"
    latest = OUT_DIR / "latest_snapshot.json"
    save_data = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "new_tweets": len(tweets),
        "total_in_db": total,
        "coverage": COVERAGE,
        "results": results,
    }
    for f in [fp, latest]:
        f.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {fp}")

    return results


def print_results(results):
    print("\n" + "=" * 60)
    for r in results:
        print(f"  [{r['market_id']}] {r['question']}")
        print(f"    Confirmed: {r['confirmed']} (est: {r['confirmed_est']}) | "
              f"Remaining: {r['remaining']} in {r['days_remaining']:.1f}d")
        print(f"    req rate: {r['required_rate']}/day | real: {r['real_daily_rate']}/day | "
              f"vel_ratio: {r['velocity_ratio']}x")
        print(f"    P(YES)={r['p_yes']*100:.0f}%  Edge={r['edge_pct']}  "
              f"Kelly={r['kelly_quarter']*100:.1f}%")
        print()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_SCROLLS
    print(f"=== Collecting {n} scrolls ===")
    tweets = collect(n_scrolls=n)
    print(f"Collected {len(tweets)} tweets")
    if tweets:
        results = store_and_analyze(tweets)
        print_results(results)
