"""
Collector module that uses the OpenClaw `browser` tool to scrape tweets.
This is called by run_continuous.py via subprocess + browser tool.
The browser tool provides CDP evaluate via `browser(action="act", request={"kind": "evaluate", ...})`.
"""
import json
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

TARGET_ID = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
PROFILE = "chrome"

# Minimal tweet extractor JS (single line, no problematic chars)
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


def parse_relative(ts_text: str, ref: datetime) -> Optional[datetime]:
    import re
    ts_text = ts_text.strip()
    m = re.search(r"(\d+)\s*(小时|天|分钟|周|秒)\s*前", ts_text)
    if m:
        v = int(m.group(1))
        u = m.group(2)
        d = {"秒": 1, "分钟": 60, "小时": 3600, "天": 86400, "周": 604800}
        return ref - timedelta(seconds=v * d.get(u, 86400))
    m = re.search(r"(\d+)(h|d|m|s|w)\b", ts_text, re.I)
    if m:
        v = int(m.group(1))
        u = m.group(2).lower()
        d = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        return ref - timedelta(seconds=v * d.get(u, 86400))
    return None


def parse_tweet(raw: dict, ref: datetime) -> Optional[dict]:
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
        dt = parse_relative(raw.get("ttext", ""), ref)
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

    return {
        "post_id": pid,
        "timestamp": dt.isoformat().replace("+00:00", "Z"),
        "text": raw.get("x", ""),
        "hour": dt.hour,
        "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
        "likes": num(raw.get("ln", "0")),
        "retweets": num(raw.get("rn", "0")),
        "replies": 0,
        "views": 0,
        "is_pinned": False,
        "has_media": False,
    }


def evaluate(browser_tool_func, js: str, timeout_ms: int = 25000) -> dict:
    """
    Call browser tool act with evaluate.
    browser_tool_func: the browser action callable
    """
    return browser_tool_func(
        action="act",
        target="host",
        profile=PROFILE,
        targetId=TARGET_ID,
        request={"kind": "evaluate", "fn": js, "timeoutMs": timeout_ms},
    )


def scroll(browser_tool_func, delay: float = 2.0):
    browser_tool_func(
        action="act",
        target="host",
        profile=PROFILE,
        targetId=TARGET_ID,
        request={"kind": "evaluate", "fn": SCROLL_JS, "timeoutMs": 5000},
    )
    time.sleep(delay)


def collect_n_scrolls(browser_func, n: int = 5, min_new: int = 5,
                      since_pid: Optional[str] = None) -> tuple:
    """
    Collect tweets over n scroll cycles using the browser tool.
    Returns (new_tweets, all_pids, page_url)
    """
    ref = datetime.now(timezone.utc)
    all_pids = []
    all_parsed = []

    for i in range(n):
        time.sleep(2)
        result = evaluate(browser_func, EXTRACT_JS)
        raw_str = result.get("result", "")
        if not raw_str:
            time.sleep(1)
            continue
        try:
            raw_tweets = json.loads(raw_str)
        except Exception:
            continue

        for rt in raw_tweets:
            pid = rt.get("p", "")
            if pid:
                all_pids.append(pid)

        parsed = []
        for rt in raw_tweets:
            p = parse_tweet(rt, ref)
            if p:
                parsed.append(p)

        all_parsed.extend(parsed)
        print(f"  Scroll {i+1}: +{len(parsed)} parsed, total pids: {len(all_pids)}")

        if i < n - 1:
            scroll(browser_func, delay=2.5)

    # Deduplicate
    seen = set()
    unique = []
    for t in sorted(all_parsed, key=lambda x: x["timestamp"], reverse=True):
        if t["post_id"] not in seen:
            seen.add(t["post_id"])
            unique.append(t)

    # Filter to only new since since_pid
    new_tweets = unique
    if since_pid:
        cutoff = False
        filtered = []
        for t in unique:
            if t["post_id"] == since_pid:
                cutoff = True
                break
            if not cutoff:
                filtered.append(t)
        new_tweets = filtered

    url_result = evaluate(browser_func, "document.location.href")
    url = ""
    if isinstance(url_result, dict):
        url = url_result.get("url", "")

    return new_tweets, all_pids, url
