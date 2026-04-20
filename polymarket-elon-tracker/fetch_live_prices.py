#!/usr/bin/env python3
"""Fetch live Polymarket prices from event page HTML (no browser needed)."""
import json
import time
import urllib.request
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
MARKET_PAGES = [
    ("apr14-21", "https://polymarket.com/event/elon-musk-of-tweets-april-14-april-21", "190"),
    ("apr17-24", "https://polymarket.com/event/elon-musk-of-tweets-april-17-april-24", "200"),
    ("may2026",  "https://polymarket.com/event/elon-musk-of-tweets-may-2026", "800"),
]
PROXY = urllib.request.ProxyHandler({"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"})
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_live_prices() -> dict:
    results = {}
    for market_id, url, target in MARKET_PAGES:
        print(f"  Fetching {market_id}...")
        opener = urllib.request.build_opener(PROXY)
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with opener.open(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"  [{market_id}] HTTP error: {e}")
            results[market_id] = {"yes": None, "no": None, "source": "http_error", "fetched_at": time.time()}
            continue

        # Strategy: find the specific question text containing the target number
        # and get the price from the same chunk.
        # The question is like: "Will Elon Musk tweet at least 190 times..."
        # Look for "at least {target}" and then find nearby outcomePrices
        pattern = f'at least.{{0,20}}{target}.{{0,60}}'
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            # Get a chunk around this match that includes price data
            chunk_start = max(0, m.start() - 200)
            chunk_end = min(len(html), m.end() + 500)
            chunk = html[chunk_start:chunk_end]
            
            # Find the YES/NO price in this chunk
            price_m = re.search(r'outcomePrices["\s:]+(\[(?:[^"\s]+|"[^"]+")\s*,\s*(?:[^"\s]+|"[^"]+")\])', chunk)
            if not price_m:
                price_m = re.search(r'outcomePrices["\s:]+(\[[^\]]+\])', chunk)
            
            if price_m:
                prices_str = price_m.group(1)
                try:
                    prices = json.loads(prices_str.replace('"', '"').replace('"', '"'))
                    if len(prices) == 2:
                        # outcomes order: ["Yes", "No"] -> prices [yes_price, no_price]
                        yes_p = float(prices[0])
                        no_p = float(prices[1])
                        print(f"  [{market_id}] YES={yes_p:.4f} NO={no_p:.4f}")
                        results[market_id] = {"yes": yes_p, "no": no_p, "source": "html_question", "fetched_at": time.time()}
                        continue
                except:
                    pass
            else:
                print(f"  [{market_id}] Found 'at least {target}' but no price nearby")
        else:
            print(f"  [{market_id}] Question 'at least {target}' not found in HTML")

        # Fallback: find the FIRST binary Yes/No market in the page that has non-[0,1] prices
        print(f"  [{market_id}] Trying fallback (first non-resolved binary market)...")
        for m2 in re.finditer(r'"outcomes"\s*:\s*\["Yes","No"\]', html):
            chunk = html[max(0, m2.start()-50):m2.start()+300]
            price_m2 = re.search(r'outcomePrices["\s:]+(\[[^\]]+\])', chunk)
            if price_m2:
                prices_str = price_m2.group(1)
                try:
                    prices = json.loads(prices_str)
                    if len(prices) == 2 and not (prices[0] in ['0','1'] and prices[1] in ['0','1']):
                        yes_p = float(prices[0])
                        no_p = float(prices[1])
                        print(f"  [{market_id}] YES={yes_p:.4f} NO={no_p:.4f} (fallback)")
                        results[market_id] = {"yes": yes_p, "no": no_p, "source": "html_fallback", "fetched_at": time.time()}
                        break
                except:
                    pass
        else:
            print(f"  [{market_id}] No suitable binary market found")
            results[market_id] = {"yes": None, "no": None, "source": "html_not_found", "fetched_at": time.time()}

    return results


def save_live_prices(prices: dict):
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    p = DATA_DIR / "live_prices.json"
    p.write_text(json.dumps(prices, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved to {p}")


if __name__ == "__main__":
    print("Fetching live prices from Polymarket HTML...\n")
    p = fetch_live_prices()
    save_live_prices(p)
    for mid, d in p.items():
        if d.get("yes") is not None:
            print(f"  {mid}: YES={d['yes']:.4f} NO={d['no']:.4f}")
        else:
            print(f"  {mid}: no price")
