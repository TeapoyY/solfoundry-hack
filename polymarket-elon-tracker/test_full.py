#!/usr/bin/env python3
"""Full profile collection test - 20 scrolls to see if we approach xtrack count."""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.resolve()
OC_MJS = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs"
NODE = r"C:\Program Files\nodejs\node.exe"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

def run_node(args, timeout=40):
    cmd = [NODE, OC_MJS] + args
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout,
                          encoding="utf-8", errors="replace")
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"

def beval(js, timeout_ms=25000):
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
        return None

def bnav(url):
    run_node(["browser", "navigate",
              "--target-id", TARGET,
              "--browser-profile", "chrome",
              "--url", url, "--json"], timeout=30)

def bscroll():
    beval("window.scrollTo(0,document.body.scrollHeight)", timeout_ms=5000)

def bscroll_to_top():
    beval("window.scrollTo(0,0)", timeout_ms=5000)

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
r.push({p:pid,t:ts,x:tx.substring(0,100)});
}
return JSON.stringify(r);})()"""

CLICK_POSTS_TAB_JS = r"""(function(){
var tabs=document.querySelectorAll('[role=tab],a[role=tab]');
for(var i=0;i<tabs.length;i++){
if(tabs[i].innerText && tabs[i].innerText.trim()==='Posts'){
tabs[i].click();return 'clicked';
}
}
return 'not found';
})()"""

def parse_tweet(raw):
    pid = raw.get("p", "")
    if not pid:
        return None
    ts_str = raw.get("t", "")
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return {"post_id": pid, "timestamp": dt.isoformat().replace("+00:00", "Z")}
    except Exception:
        return None

def main():
    print("=== Full profile collection (20 scrolls) ===")
    
    bnav("https://x.com/elonmusk")
    time.sleep(4)
    
    # First scroll to top to ensure we're at the beginning of the timeline
    bscroll_to_top()
    time.sleep(2)
    
    print("Clicking Posts tab...")
    r = beval(CLICK_POSTS_TAB_JS, timeout_ms=10000)
    print(f"  Result: {r}")
    time.sleep(3)
    
    # Scroll to top again after tab switch to start from newest
    bscroll_to_top()
    time.sleep(2)
    
    seen = set()
    tweets = []
    ws_dt = datetime(2026, 4, 14, 0, 0, 0, tzinfo=timezone.utc)
    we_dt = datetime(2026, 4, 21, 23, 59, 59, tzinfo=timezone.utc)
    
    for i in range(20):
        bscroll()
        time.sleep(2.5)
        result = beval(EXTRACT_JS, timeout_ms=25000)
        raw = []
        if result:
            try:
                raw = json.loads(result)
            except Exception:
                pass
        new = 0
        for raw_t in raw:
            if isinstance(raw_t, str):
                continue
            pid = raw_t.get("p", "")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            p = parse_tweet(raw_t)
            if not p:
                continue
            ts = datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00'))
            if ts < ws_dt or ts > we_dt:
                continue
            tweets.append(p)
            new += 1
        
        # Get the oldest tweet in this batch
        batch_ts = []
        for raw_t in raw:
            if isinstance(raw_t, str):
                continue
            ts_str = raw_t.get("t", "")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    batch_ts.append(ts)
                except Exception:
                    pass
        
        oldest = min(batch_ts) if batch_ts else None
        info = oldest.strftime("%b %d %H:%M") if oldest else "?"
        print(f"  Scroll {i+1:2d}: +{new:2d} new (total: {len(tweets):3d}) oldest={info}")
    
    print(f"\n=== RESULTS ===")
    print(f"Total tweets in Apr14-21 window: {len(tweets)}")
    print(f"xtrack confirmed (Polymarket TWEET COUNT): 167")
    print(f"Coverage: {len(tweets)/167*100:.1f}%")
    print(f"\nBy day:")
    days = Counter(t['timestamp'][:10] for t in tweets)
    for d in sorted(days):
        print(f"  {d}: {days[d]} tweets")

if __name__ == "__main__":
    main()
