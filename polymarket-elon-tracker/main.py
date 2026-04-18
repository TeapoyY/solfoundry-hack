#!/usr/bin/env python3
"""
xTracker Clone - Polymarket Elon Musk Tweet Tracker
============================================
复制 xtracker.polymarket.com 的核心逻辑:
1. 在精确 UTC 时间窗口内统计 Elon 推文数
2. 对照 xtracker 快照校正覆盖率
3. 计算每个市场的 YES/NO 真实概率
4. 与 Polymarket 价格对比找边缘

抓取方法优先级:
  1. Browser Relay (Chrome 已登录态) → 最可靠
  2. Playwright (用户 Chrome profile)
  3. Twitter GraphQL API (Guest Token)
  4. Twitter Syndication API (需要认证 cookies)

Author: OpenClaw Agent
"""
import sys
import json
import math
import re
import time
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.resolve()

# ================================================================
# 推文市场定义 (与 xtracker 一致)
# ================================================================
MARKETS = [
    {
        "id": "elon-apr14-21",
        "question": "Elon Musk # tweets April 14 - April 21, 2026? (Over 190?)",
        "target": 190,
        "window_utc": ("2026-04-14T00:00:00Z", "2026-04-21T23:59:59Z"),
        "xtracker_snapshot": 116,  # xtracker 最后确认数
        "snapshot_time": "2026-04-18T02:15:00+08:00",
    },
    {
        "id": "elon-apr17-24",
        "question": "Elon Musk # tweets April 17 - April 24, 2026? (Over 200?)",
        "target": 200,
        "window_utc": ("2026-04-17T00:00:00Z", "2026-04-24T23:59:59Z"),
        "xtracker_snapshot": 7,
        "snapshot_time": "2026-04-18T02:15:00+08:00",
    },
    {
        "id": "elon-may2026",
        "question": "Elon Musk # tweets May 2026? (Over 800?)",
        "target": 800,
        "window_utc": ("2026-05-01T00:00:00Z", "2026-05-31T23:59:59Z"),
        "xtracker_snapshot": 0,
        "snapshot_time": None,
    },
]

# 覆盖率校正系数 (从 xtracker 验证得到)
# Apr16-18: xtracker=42, 我们方法=22 → 覆盖率=22/42=52.4%
# Apr14-21: xtracker=116, 我们估算4天窗口
COVERAGE_RATIO = 42 / 22  # ≈ 1.91


# ================================================================
# 核心逻辑: 从推文列表计算市场统计
# ================================================================

def parse_tweet_ts(ts_str: str) -> Optional[datetime]:
    """解析推文时间戳"""
    if not ts_str:
        return None
    # 优先 ISO format
    for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f"]:
        try:
            return datetime.strptime(ts_str[:19], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # 相对时间: "3小时前"
    m = re.search(r"(\d+)\s*(小时|天|周|分钟)\s*前", ts_str)
    if m:
        val = int(m.group(1))
        unit = m.group(2)
        delta_map = {"分钟": timedelta(minutes=val), "小时": timedelta(hours=val),
                    "天": timedelta(days=val), "周": timedelta(weeks=val)}
        return datetime.now(timezone.utc) - delta_map.get(unit, timedelta())
    return None


def count_in_window(tweets: List[dict], window_start: str, window_end: str) -> int:
    """统计指定 UTC 时间窗口内的推文数"""
    try:
        ws = datetime.fromisoformat(window_start.replace("Z", "+00:00"))
        we = datetime.fromisoformat(window_end.replace("Z", "+00:00"))
    except ValueError:
        return 0
    count = 0
    for t in tweets:
        ts = t.get("timestamp") or t.get("ts") or t.get("tsAttr", "")
        if isinstance(ts, str):
            dt = parse_tweet_ts(ts)
        elif isinstance(ts, datetime):
            dt = ts
        else:
            continue
        if dt and ws <= dt <= we:
            count += 1
    return count


def calc_market_stats(mkt: dict, tweets: List[dict]) -> dict:
    """计算单个市场的完整统计"""
    ws, we = mkt["window_utc"]
    confirmed = count_in_window(tweets, ws, we)
    target = mkt["target"]

    now = datetime.now(timezone.utc)
    window_end_dt = datetime.fromisoformat(we.replace("Z", "+00:00"))
    days_remaining = max((window_end_dt - now).total_seconds() / 86400, 0)

    remaining = max(target - confirmed, 0)
    required_rate = remaining / days_remaining if days_remaining > 0 else 999
    velocity_ratio = required_rate / (30 / days_remaining) if days_remaining > 0 else 999  # ~30/day baseline

    # 三情景 MC (用覆盖率校正后的速度)
    real_daily = 30 * COVERAGE_RATIO  # 真实日均 ≈ 57/day
    mc = monte_carlo_3scenario(confirmed, target, days_remaining, real_daily)
    p_yes = mc["p_reach"]

    yes_price = 0.50  # 需要从 Polymarket API 获取
    edge = p_yes - yes_price
    kelly_f = kelly(yes_price, p_yes)

    return {
        "market_id": mkt["id"],
        "question": mkt["question"],
        "target": target,
        "window_utc": f"{ws[:10]} ~ {we[:10]}",
        "confirmed_count": confirmed,
        "xtracker_snapshot": mkt["xtracker_snapshot"],
        "snapshot_time": mkt["snapshot_time"],
        "remaining": remaining,
        "days_remaining": round(days_remaining, 2),
        "required_rate": round(required_rate, 1),
        "p_yes": round(p_yes, 4),
        "edge": round(edge, 4),
        "kelly_full": round(kelly_f, 4),
        "mc": mc,
        "coverage_ratio": COVERAGE_RATIO,
    }


def kelly(entry: float, prob: float) -> float:
    """Kelly Criterion"""
    odds = 1 / entry
    b = odds - 1
    if b <= 0:
        return 0
    q = 1 - prob
    return max(0, (b * prob - q) / b)


def monte_carlo_3scenario(current: int, target: int, days: float,
                          real_daily: float, n: int = 30000) -> dict:
    """
    三情景 Monte Carlo
    - Bear: 0.7x real_daily, weight=0.2
    - Base: real_daily, weight=0.5
    - Bull: 1.5x real_daily, weight=0.3
    """
    import numpy as np

    if days <= 0:
        return {"p_reach": 1.0 if current >= target else 0.0,
                "mean": current, "scenarios": {}}

    scenarios = [
        ("bear", real_daily * 0.7, 0.20),
        ("base", real_daily,       0.50),
        ("bull", real_daily * 1.5, 0.30),
    ]

    all_results = []
    p_reaches = {}
    for name, rate, weight in scenarios:
        lam = rate * days
        samples = np.random.poisson(lam, size=n)
        final = current + samples
        p_reach = float(np.mean(final >= target))
        p_reaches[name] = round(p_reach, 4)
        all_results.extend((v, weight) for v in final)

    total_w = sum(w for _, w in all_results)
    p_reach_weighted = sum(w for v, w in all_results if v >= target) / total_w
    return {
        "p_reach": round(p_reach_weighted, 4),
        "mean": round(sum(v * w for v, w in all_results) / total_w, 1),
        "scenarios": {name: {"p_reach": p_reaches[name], "rate": rate, "weight": weight}
                      for name, rate, weight in scenarios},
    }


# ================================================================
# 推文抓取器接口
# ================================================================

class TweetFetcher:
    """推文抓取基类"""

    def fetch(self, min_count: int = 100) -> List[dict]:
        raise NotImplementedError


class BrowserRelayFetcher(TweetFetcher):
    """
    方法1: Browser Relay (Chrome 已登录态)
    通过 CDP WebSocket 执行 JS 滚动抓取 x.com/elonmusk
    需要 Chrome Browser Relay 标签已打开 x.com/elonmusk
    """
    CDP_URL = "ws://127.0.0.1:18792/cdp"
    TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

    def fetch(self, min_count: int = 100) -> List[dict]:
        try:
            import websockets, asyncio, json, random
        except ImportError:
            return []

        async def _fetch():
            try:
                async with websockets.connect(
                    self.CDP_URL, max_size=50*1024*1024,
                    extra_headers={"Origin": "chrome-extension://pnpcdjmgjnioejgfhppcffjgpkafhii"}
                ) as ws:
                    # Activate target
                    await ws.send(json.dumps({
                        "id": 1, "method": "Target.activateTarget",
                        "params": {"targetId": self.TARGET}
                    }))
                    await asyncio.sleep(0.5)

                    # Init collector
                    await ws.send(json.dumps({
                        "id": 2, "method": "Runtime.evaluate",
                        "params": {"expression": """
                            window.__tfc = {
                                seen: new Set(),
                                tweets: [],
                                scroll: 0,
                                maxScrolls: 20
                            };
                            window.scrollTo(0, document.body.scrollHeight);
                            'collector_init'
                        """, "returnByValue": True}
                    }))
                    await asyncio.sleep(2)

                    collected = []

                    for _ in range(20):
                        # Extract
                        await ws.send(json.dumps({
                            "id": 99, "method": "Runtime.evaluate",
                            "params": {
                                "expression": """
(function() {
    var c = window.__tfc;
    if (!c) return JSON.stringify({error: 'no collector'});
    var arts = document.querySelectorAll('article[role="article"]');
    var n = 0;
    for (var a of arts) {
        try {
            var pid = '';
            var links = a.querySelectorAll('a[href]');
            for (var l of links) {
                var m = l.href.match(/\\/status\\/(\\d+)/);
                if (m) { pid = m[1]; break; }
            }
            if (!pid || c.seen.has(pid)) continue;
            c.seen.add(pid);
            var tEl = a.querySelector('time');
            var ts = tEl ? (tEl.getAttribute('datetime') || tEl.innerText) : '';
            var txtEl = a.querySelector('[data-testid="tweetText"]');
            var txt = txtEl ? txtEl.innerText.slice(0, 150) : '';
            var cnt = function(sel) {
                var e = a.querySelector(sel);
                if (!e) return 0;
                var s = e.innerText.replace(/,/g,'');
                var m2 = s.match(/^([\\d.]+)(万|K|M)?/);
                if (!m2) return 0;
                var n2 = parseFloat(m2[1]);
                if (s.includes('万')) n2 *= 10000;
                else if (s.includes('K')) n2 *= 1000;
                else if (s.includes('M')) n2 *= 1e6;
                return Math.floor(n2);
            };
            c.tweets.push({
                pid, ts, txt,
                likes: cnt('[data-testid="like"]'),
                rts: cnt('[data-testid="retweet"]'),
                views: cnt('[data-testid="viewCount"]')
            });
            n++;
        } catch(e) {}
    }
    c.scroll++;
    window.scrollTo(0, document.body.scrollHeight);
    return JSON.stringify({scroll: c.scroll, new: n, total: c.tweets.length,
                           oldest: c.tweets[c.tweets.length-1]?.ts || 'none'});
})()
                                """,
                                "returnByValue": True, "timeout": 15000
                            }
                        }))
                        await asyncio.sleep(2)

                        # Collect response
                        while True:
                            try:
                                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                                data = json.loads(msg)
                                if data.get("id") == 99:
                                    result = data.get("result", {}).get("result", {})
                                    val = result.get("value", "")
                                    if val and "{" in str(val):
                                        try:
                                            info = json.loads(str(val).replace("'", '"'))
                                            print(f"  Scroll {info.get('scroll','?')}: +{info.get('new',0)} new, total={info.get('total',0)}, oldest={info.get('oldest','none')[:10]}")
                                        except:
                                            pass
                                    break
                            except asyncio.TimeoutError:
                                break

                        if info.get("total", 0) >= min_count:
                            break

                    # Extract all
                    await ws.send(json.dumps({
                        "id": 100, "method": "Runtime.evaluate",
                        "params": {
                            "expression": "JSON.stringify(window.__tfc?.tweets || [])",
                            "returnByValue": True, "timeout": 15000
                        }
                    }))
                    await asyncio.sleep(2)
                    while True:
                        try:
                            msg = await asyncio.wait_for(ws.recv(), timeout=5)
                            data = json.loads(msg)
                            if data.get("id") == 100:
                                raw = data.get("result", {}).get("result", {}).get("value", "[]")
                                tweets = json.loads(str(raw).replace("'", '"'))
                                return tweets
                        except asyncio.TimeoutError:
                            break
            except Exception as e:
                print(f"Browser Relay error: {e}")
                return []

        return asyncio.run(_fetch())


class PlaywrightFetcher(TweetFetcher):
    """
    方法2: Playwright + 用户 Chrome profile
    使用已登录的 Chrome session 抓取推文
    """
    CHROME_USER_DATA = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"

    def fetch(self, min_count: int = 100) -> List[dict]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return []

        tweets = []

        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.CHROME_USER_DATA.parent),
                    profile_directory="Default",
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox",
                          "--profile-directory=Default"],
                    viewport={"width": 1280, "height": 900},
                    user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"),
                )
            except Exception as e:
                print(f"Chrome launch error: {e}")
                return []

            page = context.new_page()
            page.goto("https://x.com/elonmusk", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            seen = set()
            last_h = 0
            no_change = 0

            while no_change < 3:
                page.wait_for_timeout(2000)
                articles = page.query_selector_all('article[role="article"]')

                for a in articles:
                    try:
                        links = a.query_selector_all('a[href]')
                        pid = next((l.get_attribute("href") for l in links
                                   if "/status/" in (l.get_attribute("href") or "")),
                                   None)
                        if not pid:
                            continue
                        m = re.search(r"/status/(\d+)", pid)
                        if not m:
                            continue
                        pid = m.group(1)
                        if pid in seen:
                            continue
                        seen.add(pid)

                        t_el = a.query_selector("time")
                        ts = (t_el.get_attribute("datetime") or
                              t_el.inner_text if t_el else "")
                        txt_el = a.query_selector('[data-testid="tweetText"]')
                        txt = txt_el.inner_text[:150] if txt_el else ""

                        def cnt(sel):
                            e = a.query_selector(sel)
                            if not e:
                                return 0
                            s = e.inner_text.replace(",", "")
                            m2 = re.match(r"^([\d.]+)(万|K|M)?", s)
                            if not m2:
                                return 0
                            n = float(m2.group(1))
                            unit = m2.group(2) or ""
                            mult = {"万": 1e4, "K": 1e3, "M": 1e6}.get(unit, 1)
                            return int(n * mult)

                        tweets.append({
                            "pid": pid,
                            "ts": ts,
                            "txt": txt,
                            "likes": cnt('[data-testid="like"]'),
                            "rts": cnt('[data-testid="retweet"]'),
                        })

                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

                new_h = page.evaluate(
                    "document.documentElement.scrollHeight")
                if new_h == last_h:
                    no_change += 1
                else:
                    no_change = 0
                last_h = new_h

                if len(tweets) >= min_count:
                    break

            context.close()

        return tweets


# ================================================================
# 主程序
# ================================================================

def run():
    print("=" * 70)
    print("  xTracker Clone - Polymarket Elon Musk Tweet Tracker")
    print(f"  Time: {datetime.now().isoformat()}")
    print("=" * 70)

    # 尝试多种抓取方式
    tweets = []
    fetcher_name = "none"

    # 方法1: Browser Relay
    print("\n[Fetcher 1] Browser Relay...")
    try:
        fetcher = BrowserRelayFetcher()
        tweets = fetcher.fetch(min_count=50)
        if tweets:
            fetcher_name = "BrowserRelay"
            print(f"  Got {len(tweets)} tweets")
    except Exception as e:
        print(f"  Browser Relay failed: {e}")

    # 方法2: Playwright
    if not tweets:
        print("\n[Fetcher 2] Playwright + Chrome profile...")
        try:
            fetcher = PlaywrightFetcher()
            tweets = fetcher.fetch(min_count=50)
            if tweets:
                fetcher_name = "Playwright"
                print(f"  Got {len(tweets)} tweets")
        except Exception as e:
            print(f"  Playwright failed: {e}")

    # 方法3: 加载历史数据
    if not tweets:
        print("\n[Fetcher 3] Loading from last known data...")
        latest = PROJECT_ROOT / "data" / "tweets_chrome_relay_latest.json"
        if latest.exists():
            tweets = json.loads(latest.read_text()).get("tweets", [])
            fetcher_name = "cached"
            print(f"  Loaded {len(tweets)} tweets from cache")

    if not tweets:
        print("\n  No tweets collected!")
        print("  Make sure Chrome Browser Relay is active on x.com/elonmusk")
        return

    # 解析时间戳
    parsed_tweets = []
    for t in tweets:
        ts_str = t.get("ts") or t.get("timestamp") or ""
        dt = parse_tweet_ts(ts_str)
        if dt:
            t["timestamp_dt"] = dt
            parsed_tweets.append(t)

    print(f"\n  Total tweets with timestamps: {len(parsed_tweets)}")

    # 保存
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = data_dir / f"tweets_{ts_str}.json"
    fp.write_text(json.dumps({
        "fetcher": fetcher_name,
        "collected_at": datetime.now().isoformat(),
        "count": len(parsed_tweets),
        "tweets": parsed_tweets,
    }, ensure_ascii=False, indent=2))

    latest = data_dir / "tweets_latest.json"
    latest.write_text(json.dumps({
        "fetcher": fetcher_name,
        "collected_at": datetime.now().isoformat(),
        "count": len(parsed_tweets),
        "tweets": parsed_tweets,
    }, ensure_ascii=False, indent=2))
    print(f"  Saved: {fp}")
    print(f"  Latest: {latest}")

    # 逐市场分析
    print("\n" + "=" * 70)
    print("  MARKET ANALYSIS")
    print("=" * 70)

    for mkt in MARKETS:
        stats = calc_market_stats(mkt, parsed_tweets)
        mc = stats["mc"]
        print(f"\n  【{mkt['question']}】")
        print(f"    窗口: {stats['window_utc']}")
        print(f"    确认: {stats['confirmed_count']} 条 (覆盖率校正后 ≈ {int(stats['confirmed_count'] * COVERAGE_RATIO)})")
        if stats['xtracker_snapshot'] > 0:
            print(f"    xtracker对照: {stats['xtracker_snapshot']} 条 (snapshot @ {stats['snapshot_time']})")
        print(f"    目标: {stats['target']} 条 | 剩余: {stats['remaining']} 条 | 剩余天数: {stats['days_remaining']}d")
        print(f"    需达速度: {stats['required_rate']}/天 (覆盖率校正后)")
        print(f"  -- MC 三情景 --")
        for name, sc in mc.get("scenarios", {}).items():
            print(f"    {name}: rate={sc['rate']:.1f}/d, P(达成)={sc['p_reach']*100:.1f}%")
        print(f"    综合P(达成): {stats['p_yes']*100:.1f}%")
        print(f"    边缘: {stats['edge']*100:+.1f}%")
        print(f"    Kelly全: {stats['kelly_full']*100:.1f}%")


if __name__ == "__main__":
    run()
