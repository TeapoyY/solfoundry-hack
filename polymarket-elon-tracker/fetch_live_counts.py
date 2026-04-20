"""Fetch live xtrack counts from Polymarket via HTTP (no browser relay needed).

xtrack.polymarket.com is BLOCKED, but the Polymarket event pages embed
the xtrack Post Counter in the page HTML. We extract it via regex.
"""
import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MARKETS = [
    {"id": "apr14-21", "slug": "elon-musk-of-tweets-april-14-april-21",
     "url": "https://polymarket.com/event/elon-musk-of-tweets-april-14-april-21"},
    {"id": "apr17-24", "slug": "elon-musk-of-tweets-april-17-april-24",
     "url": "https://polymarket.com/event/elon-musk-of-tweets-april-17-april-24"},
    {"id": "may2026", "slug": "elon-musk-of-tweets-may-2026",
     "url": "https://polymarket.com/event/elon-musk-of-tweets-may-2026"},
]

PROXY = urllib.request.ProxyHandler({"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"})
opener = urllib.request.build_opener(PROXY)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_html(url, timeout=20) -> str:
    """Fetch HTML page via HTTP."""
    req = urllib.request.Request(url, headers=HEADERS)
    with opener.open(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_tweet_count(html: str) -> int:
    """Extract TWEET COUNT value from Polymarket page HTML.
    
    The HTML contains: ...TWEET COUNT...</div><span class="...">139</span>...
    We need the first 2-4 digit number that appears AFTER the TWEET COUNT label.
    """
    # Pattern: TWEET COUNT followed by any content, then a 2-4 digit number
    # Example: TWEET COUNT</span></div><span ...>139</span>
    pattern = r'TWEET\s+COUNT[^<]{0,200}?([0-9]{2,4})'
    matches = re.findall(pattern, html)
    if matches:
        return int(matches[0])
    
    # Fallback: find "TWEET COUNT" and get first number in next 200 chars
    idx = html.find("TWEET COUNT")
    if idx >= 0:
        chunk = html[idx:idx+300]
        numbers = re.findall(r'\b([0-9]{2,4})\b', chunk)
        if numbers:
            return int(numbers[0])
    return None


def main():
    print(f"Fetching live xtrack counts from Polymarket via HTTP...")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print()

    counts = {}
    for m in MARKETS:
        print(f"[{m['id']}] {m['url']}")
        try:
            html = fetch_html(m["url"])
            print(f"  HTML length: {len(html)}")
            tweet_count = extract_tweet_count(html)
            print(f"  xtrack confirmed: {tweet_count}")
        except Exception as e:
            print(f"  ERROR: {e}")
            tweet_count = None

        counts[m["id"]] = {
            "xtrack_confirmed": tweet_count,
            "source": "polymarket_html",
            "fetched_at": time.time(),
        }

    # Save to JSON
    out_path = Path(__file__).parent / "data" / "live_xtrack.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved to: {out_path}")

    for cid, data in counts.items():
        tc = data.get("xtrack_confirmed", "ERROR")
        print(f"  {cid}: xtrack confirmed = {tc}")

    return counts


if __name__ == "__main__":
    main()