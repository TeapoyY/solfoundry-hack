#!/usr/bin/env python3
"""
One-shot tweet collector for Polymarket Elon markets.
Collects tweets via the browser tool (OpenClaw CDP evaluate).
Stores to SQLite DB, runs analysis, saves results.

Usage:
  python collect.py                    # single collection
  python run_continuous.py             # continuous (for background)
"""
import asyncio
import json
import random
import sys
import time as time_module
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import TweetDB
from src.analyzer import analyze, print_results, COVERAGE

TARGET_ID = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

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
    "r.push({p:pid,t:ts,x:tx.substring(0,100),ln:ln,rn:rn});"
    "}"
    "return JSON.stringify(r);"
    "})()"
)

SCROLL_JS = "window.scrollTo(0,document.body.scrollHeight);"

# We import the browser tool via OpenClaw's gateway
# The collector expects to be driven by the main assistant which has browser access


def parse_relative(ts_text, ref):
    import re
    ts_text = ts_text.strip()
    m = re.search(r"(\d+)\s*(小时|天|分钟|秒)\s*前", ts_text)
    if m:
        v = int(m.group(1)); u = m.group(2)
        d = {"秒":1,"分钟":60,"小时":3600,"天":86400}
        return ref - timedelta(seconds=v*d.get(u,86400))
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


def store_tweets(db, tweets_data):
    """Store tweet list to DB. Returns count stored."""
    parsed = []
    ref = datetime.now(timezone.utc)
    for raw in tweets_data:
        p = parse_tweet(raw, ref)
        if p:
            parsed.append(p)
    n = db.bulk_upsert(parsed)
    return n, parsed


def save_to_json(tweets, out_path):
    """Save tweets to JSON file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"tweets": tweets, "count": len(tweets),
                     "saved_at": datetime.now(timezone.utc).isoformat()},
                    ensure_ascii=False, indent=2),
        encoding="utf-8")


def run_analysis(db):
    results = analyze(db)
    print_results(results)

    now_iso = datetime.now(timezone.utc).isoformat()
    out_dir = PROJECT_ROOT / "output"
    out_dir.mkdir(exist_ok=True)

    save_data = {
        "collected_at": now_iso,
        "total_in_db": db.total_tweets(),
        "coverage_ratio": COVERAGE,
        "results": results,
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = out_dir / f"snapshot_{ts}.json"
    fp.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = out_dir / "latest_snapshot.json"
    latest.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {fp}")

    return results


if __name__ == "__main__":
    # This module is imported by the main assistant which drives browser collection
    # It provides storage and analysis functions
    print("Collector module loaded. Use with OpenClaw browser tool.")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    db = TweetDB()
    print(f"DB tweets: {db.total_tweets()}")
