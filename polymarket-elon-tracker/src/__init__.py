"""
run_continuous.py — Real-time tweet collector + analyzer
Run indefinitely, collecting new tweets every INTERVAL_MINUTES.
"""
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import TweetDB
from src.analyzer import analyze, print_results, COVERAGE
from src.browser_client import connect_and_collect

# ── Config ──────────────────────────────────────────────────────────
INTERVAL_MINUTES = 15   # Collect every N minutes
N_SCROLLS = 3           # Scrolls per collection pass
MIN_NEW = 5             # Min new tweets to keep scrolling
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
OUT_DIR = PROJECT_ROOT / "output"


async def one_collection_cycle(db: TweetDB) -> dict:
    """
    Do one collect → store → analyze cycle.
    Returns the analysis results dict.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    last_pid = db.last_collected_pid()
    last_time = db.last_collect_time()

    print(f"\n[{now_iso[:19]}] Collecting tweets since pid={last_pid} ...")

    try:
        new_tweets, all_pids, url = await connect_and_collect(
            n_scrolls=N_SCROLLS,
            min_new=MIN_NEW,
            since_pid=last_pid
        )
    except Exception as e:
        print(f"  Browser collect error: {e}")
        return None

    if all_pids:
        latest_pid = all_pids[0]  # newest
    else:
        latest_pid = last_pid

    n_stored = db.bulk_upsert(new_tweets)
    db.set_last_collected_pid(latest_pid)
    db.set_last_collect_time(now_iso)

    total = db.total_tweets()
    print(f"  New: +{n_stored} tweets stored | Total in DB: {total}")
    if new_tweets:
        newest = new_tweets[0]["timestamp"][:19]
        oldest = new_tweets[-1]["timestamp"][:19]
        print(f"  New range: {oldest} -> {newest}")

    # Analyze
    results = analyze(db)

    # Save snapshots
    OUT_DIR.mkdir(exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = OUT_DIR / f"snapshot_{ts_str}.json"
    # Attach tweets to results for save
    save_data = {
        "collected_at": now_iso,
        "new_tweets": len(new_tweets),
        "total_in_db": total,
        "last_collected_pid": latest_pid,
        "coverage_ratio": COVERAGE,
        "results": results,
    }
    fp.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")

    latest_fp = OUT_DIR / "latest_snapshot.json"
    latest_fp.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print_results(results)

    return results


async def main():
    print("=" * 60)
    print("  xTracker Clone — Real-time Collector")
    print(f"  Interval: {INTERVAL_MINUTES} min | Scrolls: {N_SCROLLS}")
    print(f"  DB: {DB_PATH}")
    print("=" * 60)

    db = TweetDB()
    total = db.total_tweets()
    print(f"  Existing tweets in DB: {total}")
    if total == 0:
        print("  First run: doing a longer initial collection (10 scrolls)...")
        try:
            _, _, _ = await connect_and_collect(n_scrolls=10, min_new=5)
        except Exception as e:
            print(f"  Initial collection error: {e}")

    cycle = 0
    while True:
        cycle += 1
        print(f"\n{'='*60}\n  Cycle #{cycle} | {datetime.now().isoformat()[:19]}\n{'='*60}")
        results = await one_collection_cycle(db)
        if results is None:
            print("  Sleeping 5 min before retry...")
            await asyncio.sleep(300)
        else:
            await asyncio.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
