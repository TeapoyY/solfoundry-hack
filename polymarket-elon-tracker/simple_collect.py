#!/usr/bin/env python3
"""
Simple tweet collector that:
1. Uses browser tool (via Python subprocess calling openclaw CLI)
2. Navigates and scrolls x.com/home
3. Extracts tweets and saves to JSON
4. Stores in SQLite and analyzes

Key insight: openclaw CLI --json outputs clean JSON that Python can parse.
"""
import json
import os
import re
import subprocess
import sys
import time
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "output"
OC_PS1 = r"C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
OC_MJS = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs"
NODE = r"C:\Program Files\nodejs\node.exe"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

# Node.js JS unicode escape for quotes
Q = '\\"'
QL = '"'


def run_node(args, timeout=40):
    """Run node openclaw.mjs with args, return stdout as text."""
    cmd = [NODE, OC_MJS] + args
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout,
                          encoding="utf-8", errors="replace")
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"


def beval(js, timeout_ms=25000):
    """Browser evaluate, return the 'result' field string."""
    # Escape JS for JSON string: escape backslashes and quotes
    js_escaped = js.replace("\\", "\\\\").replace('"', '\\"')
    result = run_node([
        "browser", "evaluate",
        "--fn", js,
        "--target-id", TARGET,
        "--browser-profile", "chrome",
        "--timeout", str(timeout_ms),
        "--json"
    ], timeout=timeout_ms // 1000 + 15)
    if not result:
        return None
    # Parse JSON from result
    text = result.strip()
    try:
        data = json.loads(text)
        return data.get("result", None)
    except Exception:
        # Try extracting JSON object
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            try:
                data = json.loads(m.group(0))
                return data.get("result", None)
            except Exception:
                pass
        return None


def bnav(url):
    run_node(["browser", "navigate",
              "--target-id", TARGET,
              "--browser-profile", "chrome",
              "--url", url,
              "--json"], timeout=30)


def bscroll():
    beval("window.scrollTo(0,document.body.scrollHeight)", timeout_ms=5000)


EXTRACT_JS = r"""(function(){
var r=[];
var a=document.querySelectorAll('article[role=article]');
for(var i=0;i<a.length;i++){
var el=a[i];var pid='';
var ls=el.querySelectorAll('a[href]');
for(var j=0;j<ls.length;j++){
var m=ls[j].href.match(/\/status\/(\d+)/);
if(m){pid=m[1];break;}
}
var t=el.querySelector('time');
var ts=t?(t.getAttribute('datetime')||''):'';
var txt=el.querySelector('[data-testid=tweetText]');
var tx=txt?(txt.innerText||''):'';
var like=el.querySelector('[data-testid=like]');
var ln=like?(like.innerText||'0').replace(/,/g,''):'0';
var rt=el.querySelector('[data-testid=retweet]');
var rn=rt?(rt.innerText||'0').replace(/,/g,''):'0';
r.push({p:pid,t:ts,x:tx.substring(0,100),ln:ln,rn:rn});
}
return JSON.stringify(r);})()"""


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


def collect(n_scrolls=8):
    print("Navigating to x.com/home...")
    bnav("https://x.com/home")
    time.sleep(3)

    all_tweets = []
    seen = set()
    ref = datetime.now(timezone.utc)

    for i in range(n_scrolls):
        time.sleep(2)
        result = beval(EXTRACT_JS, timeout_ms=25000)

        raw_tweets = []
        if result:
            try:
                raw_tweets = json.loads(result)
            except Exception:
                pass

        new = 0
        for raw in raw_tweets:
            if isinstance(raw, str):
                continue
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
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DATA_DIR / "tweets_latest.json"
    save = {"tweets": tweets, "count": len(tweets),
            "collected_at": datetime.now(timezone.utc).isoformat()}
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
    save_data = {"collected_at": datetime.now(timezone.utc).isoformat(),
                 "new_tweets": len(tweets), "total_in_db": total,
                 "coverage": COVERAGE, "results": results}
    for f in [fp, latest]:
        f.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {fp}")

    print("\n=== ANALYSIS ===")
    for r in results:
        print(f"  [{r['market_id']}] conf={r['confirmed']} P={r['p_yes']*100:.0f}% "
              f"Edge={r['edge_pct']} Kelly={r['kelly_quarter']*100:.1f}%")
    return results


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"Collecting {n} scrolls via Node.js + openclaw CLI...")
    tweets = collect(n_scrolls=n)
    print(f"Collected: {len(tweets)} tweets")
    if tweets:
        store_and_analyze(tweets)
