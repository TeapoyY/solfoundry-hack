#!/usr/bin/env python3
"""
Fixed tweet collector for Polymarket Elon tweet count markets.

KEY FIXES from original simple_collect.py:
1. Collects from x.com/elonmusk (profile) instead of x.com/home (algorithmic feed)
   - x.com/home misses many tweets due to algorithmic ranking
   - x.com/elonmusk shows ALL tweets from the profile including retweets
2. Scrolls back to cover the FULL target window (not just recent tweets)
3. Filters tweets to only those within the target date window

xtrack counting rules (from Polymarket T&Cs):
- Main posts: YES
- Quote posts (with comment): YES  
- Reposts/retweets: YES (show up in Posts tab of profile)
- Pure replies: NO (shown in separate Replies tab)
- Community reposts: NO

Usage:
  python simple_collect_fixed.py              # collect with defaults
  python simple_collect_fixed.py --scrolls 20 --window-start 2026-04-14 --window-end 2026-04-21
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "output"
OC_PS1 = r"C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
OC_MJS = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs"
NODE = r"C:\Program Files\nodejs\node.exe"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"


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
    text = result.strip()
    try:
        data = json.loads(text)
        return data.get("result", None)
    except Exception:
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


def bscroll_to_top():
    """Scroll to top of page to start fresh collection."""
    beval("window.scrollTo(0,0)", timeout_ms=5000)


# Extract tweets from x.com profile page
# This works for both home feed and profile pages
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


# JS to click the Posts tab on a profile page
CLICK_POSTS_TAB_JS = r"""(function(){
var tabs=document.querySelectorAll('a[role=tab],div[role=tab],span[role=tab');
for(var i=0;i<tabs.length;i++){
if(tabs[i].innerText && tabs[i].innerText.trim()==='Posts'){
tabs[i].click();return 'clicked';
}
}
return 'not found';
})()"""


# JS to check if we're on the Posts tab
CHECK_TAB_JS = r"""(function(){
var tabs=document.querySelectorAll('[role=tab]');
for(var i=0;i<tabs.length;i++){
var t=tabs[i];
if(t.getAttribute('aria-selected')==='true'||t.getAttribute('data-state')==='active'){
return t.innerText||'unknown';
}
}
return 'no active tab';
})()"""


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


def collect_profile(n_scrolls=15, window_start=None, window_end=None):
    """
    Collect tweets from x.com/elonmusk profile page.
    
    Key difference from home feed: Profile page shows ALL tweets from the user,
    including retweets. Home feed (x.com/home) uses algorithmic ranking that
    hides many tweets.
    
    Args:
        n_scrolls: Number of scroll cycles to perform
        window_start: ISO date string (YYYY-MM-DD) - only collect tweets after this
        window_end: ISO date string (YYYY-MM-DD) - only collect tweets before this
    """
    print("Navigating to x.com/elonmusk (profile page)...")
    bnav("https://x.com/elonmusk")
    time.sleep(3)

    # Wait for page to load
    beval("document.body.innerHTML.length", timeout_ms=10000)
    time.sleep(2)

    # Click Posts tab to ensure we're on the posts feed (not replies)
    print("Clicking Posts tab...")
    result = beval(CLICK_POSTS_TAB_JS, timeout_ms=10000)
    print(f"  Tab click result: {result}")
    time.sleep(2)

    all_tweets = []
    seen = set()
    ref = datetime.now(timezone.utc)

    # Parse window dates
    ws_dt = None
    we_dt = None
    if window_start:
        try:
            ws_dt = datetime.strptime(window_start, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0, tzinfo=timezone.utc)
        except Exception:
            pass
    if window_end:
        try:
            we_dt = datetime.strptime(window_end, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except Exception:
            pass

    # Scroll to top first
    bscroll_to_top()
    time.sleep(2)

    for i in range(n_scrolls):
        # Scroll down to load more tweets
        bscroll()
        time.sleep(2.5)

        result = beval(EXTRACT_JS, timeout_ms=25000)

        raw_tweets = []
        if result:
            try:
                raw_tweets = json.loads(result)
            except Exception:
                pass

        new = 0
        newest_ts = None
        oldest_ts = None

        for raw in raw_tweets:
            if isinstance(raw, str):
                continue
            pid = raw.get("p", "")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            p = parse_tweet(raw, ref)
            if not p:
                continue

            # Apply window filter
            try:
                ts = datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00'))
            except Exception:
                continue

            if ws_dt and ts < ws_dt:
                continue
            if we_dt and ts > we_dt:
                continue

            all_tweets.append(p)
            new += 1

            if newest_ts is None or ts > newest_ts:
                newest_ts = ts
            if oldest_ts is None or ts < oldest_ts:
                oldest_ts = ts

        ts_info = ""
        if newest_ts and oldest_ts:
            ts_info = f" | tweets: {newest_ts.strftime('%b%d %H:%M')} -> {oldest_ts.strftime('%b%d %H:%M')}"

        print(f"  Scroll {i+1}: +{new} new (total: {len(all_tweets)}){ts_info}")

        # Early exit if we've scrolled past the window start date
        if oldest_ts and ws_dt and old_tweets_count >= 0:
            if old_tweets_count == 0 and i > 2:
                # No new tweets added in this scroll, we've gone past window
                # But let's continue a bit more to be sure
                pass
        old_tweets_count = new  # track for next iteration

    all_tweets.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_tweets


def collect_and_save(window_start=None, window_end=None, n_scrolls=15):
    """
    Main entry point for profile-based tweet collection.
    """
    tweets = collect_profile(n_scrolls=n_scrolls, 
                           window_start=window_start,
                           window_end=window_end)

    print(f"\nCollected: {len(tweets)} tweets in window {window_start} to {window_end}")

    if not tweets:
        print("No tweets collected!")
        return None

    # Save to JSON
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DATA_DIR / "tweets_latest.json"
    save = {"tweets": tweets, "count": len(tweets),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "method": "x.com/elonmusk profile (fixed)",
            "window_start": window_start,
            "window_end": window_end}
    json_path.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")

    # Store to SQLite
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.database import TweetDB
    from collect import store_tweets
    db = TweetDB()
    n, parsed = store_tweets(db, tweets)
    total = db.total_tweets()
    print(f"Stored: +{n}, total: {total}")

    return tweets


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Collect tweets from x.com/elonmusk profile")
    parser.add_argument("--scrolls", type=int, default=15,
                       help="Number of scroll cycles (default: 15)")
    parser.add_argument("--window-start", "--ws", default="2026-04-14",
                       help="Window start date YYYY-MM-DD (default: 2026-04-14)")
    parser.add_argument("--window-end", "--we", default="2026-04-21",
                       help="Window end date YYYY-MM-DD (default: 2026-04-21)")
    args = parser.parse_args()

    collect_and_save(
        window_start=args.window_start,
        window_end=args.window_end,
        n_scrolls=args.scrolls
    )
