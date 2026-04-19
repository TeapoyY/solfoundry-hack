#!/usr/bin/env python3
"""
Fetch live Polymarket YES/NO prices via browser relay.
Stores results to data/live_prices.json.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

NODE = r"C:\Program Files\nodejs\node.exe"
OC_MJS = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
DATA_DIR = Path(__file__).parent / "data"

MARKET_SLUGS = [
    ("apr14-21", "https://polymarket.com/event/elon-musk-of-tweets-april-14-april-21"),
    ("apr17-24", "https://polymarket.com/event/elon-musk-of-tweets-april-17-april-24"),
    ("may2026",  "https://polymarket.com/event/elon-musk-of-tweets-may-2026"),
]

def run_node(args, timeout=50):
    cmd = [NODE, OC_MJS] + args
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, encoding="utf-8", errors="replace")
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"

def beval(js, timeout_ms=25000):
    result = run_node([
        "browser", "evaluate",
        "--fn", js,
        "--target-id", TARGET,
        "--browser-profile", "chrome",
        "--timeout", str(timeout_ms),
        "--json"
    ], timeout=timeout_ms // 1000 + 15)
    if not result:
        return None
    try:
        data = json.loads(result.strip())
        return data.get("result", None)
    except:
        import re
        m = re.search(r'\{[\s\S]*\}', result)
        if m:
            try:
                return json.loads(m.group(0)).get("result", None)
            except:
                pass
        return None

def bnav(url):
    run_node([
        "browser", "navigate",
        "--target-id", TARGET,
        "--browser-profile", "chrome",
        "--url", url
    ], timeout=15)
    time.sleep(3)

def fetch_price_for_market(market_id: str, url: str) -> dict:
    """Navigate to market page and extract YES/NO prices."""
    bnav(url)
    time.sleep(2)

    # Try multiple selectors for Polymarket price display
    js = r"""() => {
        // Strategy 1: look for price elements with explicit YES/NO labels
        const yesEls = document.querySelectorAll('[class*="price"], [class*="outcome"], [class*="side"]');
        let yesPrice = null, noPrice = null;

        // Look for YES label + price
        for (const el of yesEls) {
            const text = el.textContent.trim();
            const parent = el.closest('[class]');
            const parentText = parent ? parent.textContent : '';
            if ((text.includes('YES') || text.includes('yes') || text.includes('Yes'))
                && !text.includes('NO') && !text.includes('no')) {
                const m = text.match(/0\.\d+/);
                if (m && !yesPrice) yesPrice = parseFloat(m[0]);
            }
            if ((text.includes('NO') || text.includes('no') || text.includes('No'))
                && !text.includes('YES') && !text.includes('YES')) {
                const m = text.match(/0\.\d+/);
                if (m && !noPrice) noPrice = parseFloat(m[0]);
            }
        }

        // Strategy 2: look for numeric spans near YES/NO text
        const allSpans = document.querySelectorAll('span');
        for (const span of allSpans) {
            const t = span.textContent.trim();
            const prev = span.previousElementSibling;
            const next = span.nextElementSibling;
            const prevT = prev ? prev.textContent.trim() : '';
            const nextT = next ? next.textContent.trim() : '';
            if ((prevT.includes('YES') || nextT.includes('YES')) && !t.includes('NO')) {
                const m = t.match(/0\.\d+/);
                if (m && !yesPrice) yesPrice = parseFloat(m[0]);
            }
            if ((prevT.includes('NO ') || prevT.includes('NO,') || nextT.includes('NO ')) && !t.includes('YES')) {
                const m = t.match(/0\.\d+/);
                if (m && !noPrice) noPrice = parseFloat(m[0]);
            }
        }

        // Strategy 3: look for any price displayed prominently (top number)
        const prices = [];
        document.querySelectorAll('[class*="bid"], [class*="ask"], [class*="last"]').forEach(el => {
            const t = el.textContent;
            const m = t.match(/0\.\d+/);
            if (m) prices.push(parseFloat(m[0]));
        });

        // Strategy 4: generic price scan near the market title
        const h1 = document.querySelector('h1');
        if (h1) {
            const parent = h1.closest('section, div');
            if (parent) {
                const spans = parent.querySelectorAll('span');
                spans.forEach(s => {
                    const t = s.textContent;
                    const m = t.match(/0\.\d+/);
                    if (m) {
                        const v = parseFloat(m[0]);
                        if (v > 0 && v <= 1) prices.push(v);
                    }
                });
            }
        }

        // Deduplicate and pick the two most likely
        const unique = [...new Set(prices)].sort();
        if (unique.length >= 2) {
            yesPrice = yesPrice || unique[unique.length - 1];
            noPrice = noPrice || (1 - yesPrice);
        } else if (unique.length === 1) {
            if (!yesPrice) yesPrice = unique[0];
        }

        return JSON.stringify({ yesPrice, noPrice, prices: unique.slice(0, 5) });
    }"""

    result = beval(js, timeout_ms=20000)
    if not result:
        return {"yes": None, "no": None, "raw": []}

    try:
        data = json.loads(result) if isinstance(result, str) else result
        yes = data.get("yesPrice")
        no = data.get("noPrice")
        raw = data.get("prices", [])

        # Sanity check
        if yes and (yes < 0.01 or yes > 0.99):
            yes = None
        if no and (no < 0.01 or no > 0.99):
            no = None
        # YES + NO should ≈ 1
        if yes and no and abs(yes + no - 1.0) > 0.1:
            no = 1 - yes

        return {"yes": yes, "no": no, "raw": raw}
    except:
        return {"yes": None, "no": None, "raw": []}


def fetch_all_live_prices() -> dict:
    """Fetch prices for all markets via browser relay."""
    results = {}
    for market_id, url in MARKET_SLUGS:
        print(f"  Fetching {market_id}...", end=" ", flush=True)
        try:
            price_data = fetch_price_for_market(market_id, url)
            results[market_id] = {
                "yes": price_data["yes"],
                "no": price_data["no"],
                "raw_prices": price_data["raw"],
                "fetched_at": time.time(),
            }
            if price_data["yes"]:
                print(f"YES={price_data['yes']:.2f} NO={price_data.get('no', '?'):.2f}")
            else:
                print(f"no data (raw={price_data['raw'][:3]})")
        except Exception as e:
            results[market_id] = {"yes": None, "no": None, "error": str(e)}
            print(f"error: {e}")
        time.sleep(1)
    return results


def save_live_prices(prices: dict):
    """Save to data/live_prices.json."""
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    path = DATA_DIR / "live_prices.json"
    path.write_text(json.dumps(prices, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved to {path}")


def main():
    print("Fetching live Polymarket prices via browser relay...")
    prices = fetch_all_live_prices()
    save_live_prices(prices)

    # Summary
    for mkt, data in prices.items():
        yes = data.get("yes")
        no = data.get("no")
        if yes:
            print(f"  {mkt}: YES={yes:.2f} NO={no:.2f if no else '?'}")
        else:
            print(f"  {mkt}: no live price")


if __name__ == "__main__":
    main()
