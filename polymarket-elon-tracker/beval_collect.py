#!/usr/bin/env python3
"""
Tweet collector using openclaw CLI via PowerShell subprocess.
Works around PowerShell's JSON handling quirks.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "output"
OC = r"C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"


def run_beval(js, timeout_ms=25000):
    """
    Call openclaw browser evaluate, return {'ok': bool, 'result': str}
    """
    # Write PowerShell script to temp file
    ps_script = r'''
$ErrorActionPreference = 'Continue'
$OC = "{oc}"
$TARGET = "{target}"
$JS = @'
{js}
'@
$args = @('browser','evaluate','--fn',$JS,'--target-id',$TARGET,'--browser-profile','chrome','--timeout','{timeout}','--json')
$raw = & $OC @args 2>&1 | Out-String
# Extract first line that looks like JSON
$lines = $raw -split "`n"
foreach ($line in $lines) {{
    $trimmed = $line.Trim()
    if ($trimmed.StartsWith('{{') -or $trimmed.StartsWith('{{')) {{
        try {{
            $obj = $trimmed | ConvertFrom-Json
            # Return just the result field as string
            if ($obj.PSObject.Properties.Name -contains 'result') {{
                Write-Output $obj.result
            }} else {{
                Write-Output $trimmed
            }}
            break
        }} catch {{ }}
    }}
}}
'''.format(oc=OC, target=TARGET, js=js, timeout=timeout_ms)

    fd, fp = tempfile.mkstemp(suffix=".ps1")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(ps_script)

        timeout_sec = max(30, timeout_ms // 1000 + 10)
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-File", fp],
            capture_output=True, text=True, timeout=timeout_sec,
            encoding="utf-8", errors="replace"
        )
        return r.stdout.strip()
    finally:
        os.unlink(fp)


def beval(js, timeout_ms=25000):
    """Browser evaluate, return parsed JSON from result field."""
    text = run_beval(js, timeout_ms)
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        # Try to find JSON array/object in text
        import re
        m = re.search(r'\[.*\]', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return None


def bnav(url):
    """Navigate to URL."""
    ps_script = r'''
$OC = "{oc}"
$TARGET = "{target}"
$args = @('browser','navigate','--target-id',$TARGET,'--browser-profile','chrome','--url','{url}','--json')
& $OC @args 2>&1 | Out-String | Select-Object -First 1
'''.format(oc=OC, target=TARGET, url=url)
    fd, fp = tempfile.mkstemp(suffix=".ps1")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(ps_script)
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-File", fp],
            capture_output=True, text=True, timeout=30
        )
        return r.stdout.strip()
    finally:
        os.unlink(fp)


def bscroll():
    """Scroll to bottom."""
    run_beval("window.scrollTo(0,document.body.scrollHeight)", timeout_ms=5000)


# JS: Extract tweets from x.com home feed
EXTRACT_JS = """(function(){
var r=[];
var a=document.querySelectorAll('article[role=article]');
for(var i=0;i<a.length;i++){
var el=a[i];var pid='';
var ls=el.querySelectorAll('a[href]');
for(var j=0;j<ls.length;j++){
var m=ls[j].href.match(/\\/status\\/(\\d+)/);
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
return JSON.stringify(r);
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


def collect(n_scrolls=8):
    """Main collection loop."""
    print("Navigating to x.com/home...")
    bnav("https://x.com/home")
    time.sleep(3)

    all_tweets = []
    seen = set()
    ref = datetime.now(timezone.utc)

    for i in range(n_scrolls):
        time.sleep(2)
        result = beval(EXTRACT_JS, timeout_ms=25000)

        if result is None:
            print(f"  Scroll {i+1}: no result")
            time.sleep(1)
            continue

        # Result can be a list or a dict with 'result' key
        raw_tweets = result if isinstance(result, list) else result.get("result", [])
        if isinstance(raw_tweets, str):
            try:
                raw_tweets = json.loads(raw_tweets)
            except Exception:
                raw_tweets = []

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
    """Store to SQLite and run analysis."""
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
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"=== Collecting {n} scrolls ===")
    tweets = collect(n_scrolls=n)
    print(f"Collected {len(tweets)} tweets")
    if tweets:
        results = store_and_analyze(tweets)
        print_results(results)
    else:
        print("No tweets collected - check browser connection")
