#!/usr/bin/env python3
"""Collect tweets via Chrome CDP WebSocket, save to JSON."""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.browser_client import connect_and_collect
from src.database import TweetDB
from collect import store_tweets
from src.analyzer import analyze

TARGET_ID = "B8795CA0F4574E46F3E6F21B1D5F8F4E"


async def main():
    print("Connecting to Chrome Browser Relay...")
    db = TweetDB()
    since_pid = db.last_collected_pid()
    print(f"Last collected PID: {since_pid}")

    # Navigate to x.com/home first
    from src.browser_client import CHROME_CDP, send_ws, recv_ws, cdp_navigate, get_current_url
    import websockets
    
    async with websockets.connect(CHROME_CDP, max_size=50*1024*1024) as ws:
        await send_ws(ws, 1, "Target.activateTarget", {"targetId": TARGET_ID})
        await asyncio.sleep(0.5)
        url = await get_current_url(ws)
        print(f"Current URL: {url}")
        
        if "x.com/home" not in url and "twitter.com/home" not in url:
            print("Navigating to x.com/home...")
            await cdp_navigate(ws, "https://x.com/home")
            await asyncio.sleep(3)

    # Now do 8-scroll collection
    print("Collecting tweets (8 scrolls)...")
    tweets, all_pids, url = await connect_and_collect(n_scrolls=8, min_new=5, since_pid=since_pid)
    print(f"Collected {len(tweets)} new tweets, {len(all_pids)} total pids")

    # Save to JSON
    out_path = PROJECT_ROOT / "data" / "tweets_latest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    save_data = {
        "tweets": tweets,
        "all_pids": all_pids,
        "count": len(tweets),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "url": url,
    }
    out_path.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved to: {out_path}")

    # Store to DB
    n, parsed = store_tweets(db, tweets)
    print(f"Stored: {n} new tweets, total in DB: {db.total_tweets()}")

    # Update last collected PID
    if tweets:
        newest_pid = tweets[0].get("post_id", "") if tweets else ""
        if newest_pid:
            db.set_last_collected_pid(newest_pid)

    # Run analysis
    print("\nRunning analysis...")
    results = analyze(db)
    
    from src.analyzer import print_results, COVERAGE
    print_results(results)
    
    # Save snapshot
    out_dir = PROJECT_ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()
    snap_data = {
        "collected_at": now_iso,
        "total_in_db": db.total_tweets(),
        "coverage_ratio": COVERAGE,
        "results": results,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (out_dir / f"snapshot_{ts}.json").write_text(
        json.dumps(snap_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "latest_snapshot.json").write_text(
        json.dumps(snap_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved snapshot")

    return results


if __name__ == "__main__":
    results = asyncio.run(main())
    print("\n=== RESULTS ===")
    for r in results:
        print(f"  {r['market_id']}: P={r['p_yes']*100:.0f}% Edge={r['edge_pct']} Kelly={r['kelly_quarter']*100:.1f}%")
    
    # Alert check
    alerts = [r for r in results if r.get('edge', 0) > 0.15]
    if alerts:
        print(f"\n[ALERT] {len(alerts)} markets with edge > 15%:")
        for a in alerts:
            print(f"  {a['market_id']}: edge={a['edge_pct']}")
    else:
        print("\nNo alerts (no markets with edge > 15%)")
