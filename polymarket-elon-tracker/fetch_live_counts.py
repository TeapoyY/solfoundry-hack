"""
Fetch live xtrack confirmed counts from Polymarket market pages.
Uses browser relay to get the TWEET COUNT figure shown on each market page.

xtrack.polymarket.com is BLOCKED from this machine, but the Polymarket
market pages show the xtrack Post Counter directly.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
NODE = r"C:\Program Files\nodejs\node.exe"
OC_MJS = r"C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs"

MARKETS = [
    {"id": "apr14-21", "slug": "elon-musk-of-tweets-april-14-april-21",
     "url": "https://polymarket.com/event/elon-musk-of-tweets-april-14-april-21"},
    {"id": "apr17-24", "slug": "elon-musk-of-tweets-april-17-april-24",
     "url": "https://polymarket.com/event/elon-musk-of-tweets-april-17-april-24"},
    {"id": "may2026", "slug": "elon-musk-of-tweets-may-2026",
     "url": "https://polymarket.com/event/elon-musk-of-tweets-may-2026"},
]


def run_node(args, timeout=60):
    import subprocess
    cmd = [NODE, OC_MJS] + args
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout,
                          encoding="utf-8", errors="replace")
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"


def navigate(url):
    return run_node([
        "browser", "navigate",
        "--target-id", TARGET,
        "--browser-profile", "chrome",
        "--url", url,
        "--json"
    ], timeout=35)


def evaluate(js, timeout_ms=25000):
    result = run_node([
        "browser", "evaluate",
        "--fn", js,
        "--target-id", TARGET,
        "--browser-profile", "chrome",
        "--timeout", str(timeout_ms),
        "--json"
    ], timeout=timeout_ms // 1000 + 20)
    if not result:
        return None
    text = result.strip()
    try:
        data = json.loads(text)
        return data.get("result", None)
    except Exception:
        return None


def fetch_tweet_count(url) -> dict:
    """Navigate to market page and extract TWEET COUNT value."""
    print(f"  Navigating to {url}...")
    nav = navigate(url)
    import time; time.sleep(4)  # Extra time for Polymarket to render

    # JS: find element with exact text "TWEET COUNT", then get nearby 2-4 digit number
    js = r"""(function(){
    var result = {error: 'not found'};
    var all = document.querySelectorAll('*');
    for(var i=0;i<all.length;i++){
        var el = all[i];
        if(el.childElementCount === 0){
            var t = el.textContent.trim();
            if(t === 'TWEET COUNT'){
                var parent = el.parentElement;
                if(parent){
                    var ctx = parent.innerText;
                    var nums = ctx.match(/\d+/g);
                    if(nums && nums.length > 0){
                        var valid = nums.filter(function(n){ return n.length >= 2 && n.length <= 4; });
                        if(valid.length > 0){
                            result = {label: t, value: parseInt(valid[0]), context: ctx.substring(0,150)};
                            break;
                        }
                    }
                }
            }
        }
    }
    // Fallback: scan entire body
    if(result.error){
        var body = document.body.innerText;
        var idx = body.indexOf('TWEET COUNT');
        if(idx >= 0){
            var chunk = body.substring(idx, idx+200);
            var nums = chunk.match(/\d{2,4}/g);
            if(nums && nums.length > 0){
                result = {label: 'TWEET COUNT', value: parseInt(nums[0]), context: chunk.substring(0,150)};
            }
        }
    }
    return result;
})()"""

    result = evaluate(js, timeout_ms=25000)
    if result and not result.get("error"):
        print(f"  Found: TWEET COUNT = {result.get('value')} (ctx: {str(result.get('context',''))[:80]})")
        return result
    elif result:
        print(f"  Failed: {result.get('error', 'no result')}")
    else:
        print(f"  No result from JS")
    return {"error": "extraction failed"}


def fetch_pm_prices(url) -> dict:
    """Extract YES and NO prices from Polymarket market."""
    js = """(function(){
var results = {yes: null, no: null};
// Find percentage values
var allEls = document.querySelectorAll('*');
for(var i=0;i<allEls.length;i++){
  var el = allEls[i];
  if(el.childElementCount === 0){
    var t = el.innerText.trim();
    // Match percentage like "88%" or "0.88"
    var pct = t.match(/^(\\d+(?:\\.\\d+)?)%?$/);
    if(pct && parseFloat(pct[1]) > 0 && parseFloat(pct[1]) <= 100){
      var parent = el.parentElement;
      if(parent){
        var pt = parent.innerText || '';
        if(pt.toLowerCase().includes('yes') || pt.toLowerCase().includes('y'))
          results.yes = parseFloat(pct[1]) / (t.includes('%') ? 100 : 1);
        if(pt.toLowerCase().includes('no ') || pt.toLowerCase().includes('no\\b'))
          results.no = parseFloat(pct[1]) / (t.includes('%') ? 100 : 1);
      }
    }
  }
}
return results;
})()"""
    try:
        result = evaluate(js, timeout_ms=15000)
        return result or {}
    except:
        return {}


def main():
    print(f"Fetching live xtrack counts from Polymarket...")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print()

    counts = {}
    for m in MARKETS:
        print(f"[{m['id']}] {m['url']}")
        count_data = fetch_tweet_count(m["url"])
        tweet_count = count_data.get("value", None)
        print(f"  xtrack confirmed: {tweet_count}")
        if count_data.get("context"):
            print(f"  context: {count_data['context'][:100]}")

        counts[m["id"]] = {
            "xtrack_confirmed": tweet_count,
            "fetch_time": datetime.now(timezone.utc).isoformat(),
            "raw_data": count_data,
        }

    # Save to JSON for analyzer to pick up
    out_path = Path(__file__).parent / "data" / "live_xtrack.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved to: {out_path}")
    print()

    for cid, data in counts.items():
        tc = data.get("xtrack_confirmed", "ERROR")
        print(f"  {cid}: xtrack confirmed = {tc}")

    return counts


if __name__ == "__main__":
    main()
