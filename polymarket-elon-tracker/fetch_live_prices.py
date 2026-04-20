#!/usr/bin/env python3
"""
Fetch live Polymarket YES/NO prices via browser relay (CLI subprocess).
Uses the same approach as fetch_live_counts.py.
Navigates to each market page and extracts prices from the embedded React JSON.
"""
import json
import subprocess
import time
from pathlib import Path

NODE = r"C:\Program Files\nodejs\node.exe"
OC_MJS = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs"
PROFILE = "chrome"
DATA_DIR = Path(__file__).parent / "data"

MARKET_SLUGS = [
    ("apr14-21", "https://polymarket.com/event/elon-musk-of-tweets-april-14-april-21"),
    ("apr17-24", "https://polymarket.com/event/elon-musk-of-tweets-april-17-april-24"),
    ("may2026",  "https://polymarket.com/event/elon-musk-of-tweets-may-2026"),
]


def run_browser(args, timeout=60):
    cmd = [NODE, OC_MJS, "browser", "--browser-profile", PROFILE] + args
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, encoding="utf-8", errors="replace")
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"


def bnav(url):
    """Navigate to URL and wait for page to load."""
    run_browser(["navigate", "--url", url], timeout=20)
    time.sleep(4)


def beval(js, timeout_ms=25000):
    """Run JS in browser and return result (same as fetch_live_counts.py)."""
    result = run_browser(
        ["evaluate", "--fn", js, "--timeout", str(timeout_ms)],
        timeout=timeout_ms // 1000 + 20
    )
    if not result:
        return None
    try:
        data = json.loads(result.strip())
        return data.get("result", None)
    except:
        return None


def fetch_price_from_page(slug: str, url: str) -> dict:
    """
    Navigate to market page and extract YES/NO prices from embedded React JSON.
    """
    print(f"  Navigating to {url}...")
    bnav(url)

    # JS: extract binary Yes/No prices from Next.js React JSON
    # Look for "outcomes":["Yes","No"] in the Next.js state and get the outcomePrices
    js = r"""(function(){
    var scripts = document.querySelectorAll('script');
    var results = [];
    for(var i=0;i<scripts.length;i++){
        var t = scripts[i].textContent;
        if(t.length < 50000) continue;
        if(t.indexOf('"outcomes":["Yes","No"]') < 0 && t.indexOf('"outcomes":["No","Yes"]') < 0) continue;

        // Search for each binary Yes/No occurrence
        var searchFrom = 0;
        while(true){
            var idx = t.indexOf('"outcomes":["Yes","No"]', searchFrom);
            if(idx < 0) idx = t.indexOf('"outcomes":["No","Yes"]', searchFrom);
            if(idx < 0) break;

            // Get window around the outcomes array
            var wStart = Math.max(0, idx - 4000);
            var wEnd = Math.min(t.length, idx + 500);
            var window = t.substring(wStart, wEnd);

            // Extract outcomePrices: ["0.96","0.04"] style
            var priceMatch = window.match(/"outcomePrices"\s*:\s*\[([^\]]+)\]/);
            var outMatch = window.match(/"outcomes"\s*:\s*\[([^\]]+)\]/);

            if(priceMatch && priceMatch[1]){
                var priceStrs = priceMatch[1].split(',');
                var prices = [];
                for(var p=0;p<priceStrs.length;p++){
                    var v = parseFloat(priceStrs[p].trim().replace(/"/g,''));
                    if(!isNaN(v)) prices.push(v);
                }

                if(prices.length === 2 && prices[0] >= 0 && prices[0] <= 1 && prices[1] >= 0 && prices[1] <= 1){
                    // Determine Yes/No from outcomes order
                    var outs = outMatch && outMatch[1] ? outMatch[1].split(',').map(function(o){ return o.trim().replace(/"/g,''); }) : ['Yes','No'];
                    var yesIdx = outs.indexOf('Yes');
                    var noIdx = outs.indexOf('No');
                    if(yesIdx < 0) yesIdx = 0;
                    if(noIdx < 0) noIdx = 1;

                    var yesPrice = prices[yesIdx];
                    var noPrice = prices[noIdx];

                    // Get question text
                    var qMatch = window.match(/"question"\s*:\s*"([^"]+)"/);
                    var question = qMatch ? qMatch[1].substring(0, 100) : 'unknown';

                    results.push({yes: yesPrice, no: noPrice, question: question});
                }
            }
            searchFrom = idx + 1;
            if(results.length >= 3) break;
        }
        if(results.length > 0) break;
    }
    return results;
})()"""

    result = beval(js, timeout_ms=30000)
    if isinstance(result, list) and len(result) > 0:
        for item in result:
            if isinstance(item, dict) and item.get("yes") is not None:
                print(f"  Found: YES={item['yes']:.4f} NO={item.get('no', 1-item['yes']):.4f} | {item.get('question','')[:80]}")
                return {"yes": float(item["yes"]), "no": float(item.get("no", 1 - item["yes"]))}
    print(f"  No binary market found. result={str(result)[:200]}")
    return {"yes": None, "no": None}


def fetch_all_live_prices() -> dict:
    """Fetch prices for all markets via browser relay."""
    results = {}
    for market_id, url in MARKET_SLUGS:
        slug = url.split("/event/")[1]
        print(f"[{market_id}]")
        try:
            price_data = fetch_price_from_page(slug, url)
            results[market_id] = {
                "yes": price_data.get("yes"),
                "no": price_data.get("no"),
                "fetched_at": time.time(),
            }
            if price_data.get("yes") is not None:
                no = price_data.get("no", 1 - price_data["yes"])
                print(f"  => YES={price_data['yes']:.4f} NO={no:.4f}")
            else:
                print(f"  => no price found")
        except Exception as e:
            results[market_id] = {"yes": None, "no": None, "error": str(e)}
            print(f"  => error: {e}")
        time.sleep(2)
    return results


def save_live_prices(prices: dict):
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    path = DATA_DIR / "live_prices.json"
    path.write_text(json.dumps(prices, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved to {path}")


def main():
    print("Fetching live Polymarket prices via browser relay (CLI)...\n")
    prices = fetch_all_live_prices()
    save_live_prices(prices)
    for mkt, data in prices.items():
        yes = data.get("yes")
        no = data.get("no")
        if yes is not None:
            print(f"  {mkt}: YES={yes:.4f} NO={no:.4f if no else '?'}")
        else:
            print(f"  {mkt}: no live price")


if __name__ == "__main__":
    main()
