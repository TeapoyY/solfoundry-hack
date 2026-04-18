"""
Browser Relay CDP client for Chrome.
Uses the existing Chrome Browser Relay WebSocket to scrape tweet DOM elements.
"""
import asyncio
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import websockets

# Chrome Browser Relay CDP
CHROME_CDP = "ws://127.0.0.1:18792/cdp"
TARGET_ID = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
MAX_SIZE = 50 * 1024 * 1024

# JS: Extract tweet elements from X.com home feed / profile page
EXTRACT_JS = r"""
(function() {
    var seen = new Set();
    var results = [];
    var articles = document.querySelectorAll('article[role="article"]');
    for (var a of articles) {
        try {
            var pid = '';
            var links = a.querySelectorAll('a[href*="/status/"]');
            for (var l of links) {
                var m = l.href.match(/\/status\/(\d+)/);
                if (m) { pid = m[1]; break; }
            }
            if (!pid || seen.has(pid)) continue;
            seen.add(pid);

            var tEl = a.querySelector('time');
            var tsAttr = tEl ? (tEl.getAttribute('datetime') || '') : '';
            var tsText = tEl ? (tEl.innerText || '') : '';
            var txtEl = a.querySelector('[data-testid="tweetText"]');
            var txt = txtEl ? (txtEl.innerText || '') : '';

            var parseNum = function(sel) {
                var e = a.querySelector(sel);
                if (!e) return 0;
                var s = (e.innerText || '').replace(/,/g, '');
                var m = s.match(/^([\d.]+)([万千百亿千万]|[KMB])?/);
                if (!m) return 0;
                var n = parseFloat(m[1]);
                var u = m[2] || '';
                if (u === 'K' || u === '千' || u === '千') n *= 1000;
                else if (u === 'M' || u === '百万') n *= 1000000;
                else if (u === 'B' || u === '十亿') n *= 1000000000;
                else if (u === '万') n *= 10000;
                return Math.floor(n);
            };

            var likes  = parseNum('[data-testid="like"]');
            var rts    = parseNum('[data-testid="retweet"]');
            var rps    = parseNum('[data-testid="reply"]');
            var vEl    = a.querySelector('[data-testid="viewCount"]');
            var views  = vEl ? parseNum('[data-testid="viewCount"]') : 0;
            var pinned = !!(a.querySelector('[data-testid="pin"]'));
            var media  = !!(
                a.querySelector('[data-testid="tweetPhoto"]') ||
                a.querySelector('[data-testid="card"]') ||
                a.querySelector('[data-testid="videoPlayer"]')
            );

            results.push({
                pid: pid,
                tsAttr: tsAttr,
                tsText: tsText,
                txt: txt,
                likes: likes,
                rts: rts,
                rps: rps,
                views: views,
                pinned: pinned,
                media: media
            });
        } catch(e) {}
    }
    return JSON.stringify(results);
})()
"""


async def send_ws(ws, msg_id, method, params=None):
    await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    return msg_id


async def recv_ws(ws, expected_id, timeout=10):
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
            data = json.loads(msg)
            if data.get("id") == expected_id:
                return data
        except asyncio.TimeoutError:
            return None


async def cdp_evaluate(ws, expr, timeout=20):
    msg_id = 1
    await send_ws(ws, msg_id, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "timeout": timeout * 1000,
    })
    resp = await asyncio.wait_for(recv_ws(ws, msg_id, timeout=timeout + 3), timeout=timeout + 5)
    if resp:
        return resp.get("result", {}).get("result", {})
    return {}


async def cdp_navigate(ws, url):
    """Navigate to URL via CDP."""
    msg_id = 1
    await send_ws(ws, msg_id, "Page.navigate", {"url": url})
    await asyncio.sleep(3)


async def get_current_url(ws) -> str:
    """Get current page URL."""
    result = await cdp_evaluate(ws, "window.location.href", timeout=5)
    return result.get("value", "") or ""


async def scroll_down(ws, pixels: int = 9999):
    await cdp_evaluate(ws, f"window.scrollTo(0, {pixels})", timeout=5)
    await asyncio.sleep(2)


def parse_relative_time(ts_text: str, ref_time: datetime) -> Optional[datetime]:
    """
    Parse Chinese/English relative time strings like:
    '2小时前', '3天前', '1分钟前', '2周前', 'Apr 5', etc.
    """
    ts_text = ts_text.strip()
    # Chinese patterns
    m = re.search(r"(\d+)\s*(小时|天|分钟|周|秒|月|年)\s*前", ts_text)
    if m:
        val = int(m.group(1))
        unit = m.group(2)
        delta_map = {
            "秒": timedelta(seconds=val),
            "分钟": timedelta(minutes=val),
            "小时": timedelta(hours=val),
            "天": timedelta(days=val),
            "周": timedelta(weeks=val),
            "月": timedelta(days=val * 30),
            "年": timedelta(days=val * 365),
        }
        return ref_time - delta_map.get(unit, timedelta())

    # English patterns like "2h", "3d", "1m"
    m = re.search(r"(\d+)(h|d|m|s|w|y)", ts_text, re.I)
    if m:
        val = int(m.group(1))
        unit = m.group(2).lower()
        delta_map = {
            "s": timedelta(seconds=val),
            "m": timedelta(minutes=val),
            "h": timedelta(hours=val),
            "d": timedelta(days=val),
            "w": timedelta(weeks=val),
            "y": timedelta(days=val * 365),
        }
        return ref_time - delta_map.get(unit, timedelta())

    return None


def parse_tweet_element(tweets_js: list, ref_time: datetime) -> list:
    """
    Parse raw JS tweet objects into canonical dicts.
    Returns list of {post_id, timestamp, text, likes, ...}
    """
    parsed = []
    for t in tweets_js:
        pid = t.get("pid", "")
        if not pid:
            continue

        ts_str = t.get("tsAttr", "")
        dt = None

        if ts_str:
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except Exception:
                pass

        if not dt:
            ts_text = t.get("tsText", "")
            dt = parse_relative_time(ts_text, ref_time)

        if not dt:
            continue

        parsed.append({
            "post_id": pid,
            "timestamp": dt.isoformat().replace("+00:00", "Z"),
            "text": t.get("txt", ""),
            "hour": dt.hour,
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
            "likes": t.get("likes", 0),
            "retweets": t.get("rts", 0),
            "replies": t.get("rps", 0),
            "views": t.get("views", 0),
            "is_pinned": bool(t.get("pinned", False)),
            "has_media": bool(t.get("media", False)),
        })

    return parsed


async def collect_once(ws, n_scrolls: int = 3, min_new: int = 10,
                       since_pid: Optional[str] = None) -> tuple:
    """
    Do ONE collection pass: scroll a few times, extract tweets.

    Returns:
        (new_tweets, all_tweet_pids) — new parsed tweets and ALL seen pids
    """
    all_pids = set()
    all_parsed = []
    ref_time = datetime.now(timezone.utc)

    for scroll_num in range(n_scrolls):
        await asyncio.sleep(2)

        result = await cdp_evaluate(ws, EXTRACT_JS, timeout=25)
        raw = result.get("value", "[]")
        try:
            tweets_js = json.loads(raw)
        except Exception:
            tweets_js = []

        for t in tweets_js:
            pid = t.get("pid", "")
            if pid:
                all_pids.add(pid)

        parsed = parse_tweet_element(tweets_js, ref_time)
        all_parsed.extend(parsed)

        if len(parsed) < min_new:
            # No new tweets this scroll, wait a bit
            await asyncio.sleep(2)

        # Scroll
        await scroll_down(ws)

    # Deduplicate by post_id, sort newest first
    seen = set()
    unique = []
    for t in sorted(all_parsed, key=lambda x: x["timestamp"], reverse=True):
        if t["post_id"] not in seen:
            seen.add(t["post_id"])
            unique.append(t)

    # Filter to only new since since_pid
    if since_pid:
        new_since = False
        new_tweets = []
        for t in unique:
            if t["post_id"] == since_pid:
                new_since = True
                break
            if new_since:
                new_tweets.append(t)
    else:
        new_tweets = unique

    return new_tweets, list(all_pids)


async def connect_and_collect(n_scrolls: int = 3, min_new: int = 10,
                               since_pid: Optional[str] = None) -> tuple:
    """
    Main entry point: connect to Chrome Browser Relay, collect tweets.

    Returns:
        (new_tweets, all_pids, url) — see collect_once()
    """
    async with websockets.connect(CHROME_CDP, max_size=MAX_SIZE) as ws:
        # Activate target tab
        await send_ws(ws, 1, "Target.activateTarget", {"targetId": TARGET_ID})
        await asyncio.sleep(0.5)

        # Check current URL
        url = await get_current_url(ws)

        # If not on X home/elon profile, navigate there
        if "x.com" not in url and "twitter.com" not in url:
            await cdp_navigate(ws, "https://x.com/home")
            await asyncio.sleep(3)
            url = await get_current_url(ws)

        new_tweets, all_pids = await collect_once(ws, n_scrolls=n_scrolls,
                                                   min_new=min_new,
                                                   since_pid=since_pid)

        return new_tweets, all_pids, url


if __name__ == "__main__":
    async def test():
        print("Connecting to Chrome Browser Relay...")
        tweets, pids, url = await connect_and_collect(n_scrolls=3, min_new=5)
        print(f"URL: {url}")
        print(f"New tweets: {len(tweets)}")
        print(f"All pids seen: {len(pids)}")
        if tweets:
            newest = tweets[0]["timestamp"]
            oldest = tweets[-1]["timestamp"]
            print(f"Range: {oldest} -> {newest}")

    asyncio.run(test())
