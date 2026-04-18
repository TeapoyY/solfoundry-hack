#!/usr/bin/env python3
"""
Import existing tweet data into the tracker SQLite DB.
Run once to bootstrap the database.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_DATA = PROJECT_ROOT.parent / "polymarket-elon-analyzer" / "data"
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import TweetDB


def import_from_file(db: TweetDB, fp: Path) -> int:
    """Import tweets from a JSON file into the tracker DB."""
    data = json.loads(fp.read_text("utf-8"))
    tweets = data.get("tweets", [])
    if not tweets:
        # legacy format: top-level list
        if isinstance(data, list):
            tweets = data
    print(f"  File {fp.name}: {len(tweets)} tweets")
    n = db.bulk_upsert(tweets)
    print(f"  Stored: +{n}")
    return n


def main():
    print("Importing historical tweet data into xTracker Clone DB...")
    print(f"  Source: {SRC_DATA}")

    db = TweetDB()
    existing = db.total_tweets()
    print(f"  Existing in DB: {existing}")

    total = 0

    # Priority 1: chrome relay data
    relay = SRC_DATA / "tweets_chrome_relay_latest.json"
    if relay.exists():
        print(f"\nImporting: {relay.name}")
        total += import_from_file(db, relay)
    else:
        print(f"  Not found: {relay}")

    # Priority 2: any other tweet json files
    for fp in sorted((SRC_DATA / "tweets").glob("*.json")):
        if "chrome_relay_latest" in fp.name:
            continue
        print(f"\nImporting: {fp.name}")
        total += import_from_file(db, fp)

    final = db.total_tweets()
    print(f"\nDone. Total in DB: {final} (added +{final - existing})")

    # Show window counts
    from src.analyzer import MARKETS
    for m in MARKETS:
        cnt = db.count_in_window(m["ws"], m["we"])
        print(f"  {m['id']}: {cnt} tweets in window")


if __name__ == "__main__":
    main()
