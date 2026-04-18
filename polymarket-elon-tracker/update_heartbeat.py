#!/usr/bin/env python3
"""Update HEARTBEAT.md with new Polymarket Tracker architecture."""
from pathlib import Path

heartbeat = Path(r"C:\Users\Administrator\.openclaw\workspace\HEARTBEAT.md")
content = heartbeat.read_text("utf-8")

new_section = """## Polymarket Elon Tracker (xTracker Clone) - Updated 2026-04-18
- **Repo**: `polymarket-elon-tracker/` (C:\\Users\\Administrator\\.openclaw\\workspace\\polymarket-elon-tracker\\)
- **Architecture**:
  - `simple_collect.py` — Tweet collection via Node.js + openclaw CLI browser evaluate
  - `src/database.py` — SQLite persistence (tweets, meta, snapshots)
  - `src/analyzer.py` — 3-scenario MC + Kelly criterion
  - `src/browser_client.py` — CDP collector (for reference)
- **Browser Relay**: Chrome tab B8795CA0F4574E46F3E6F21B1D5F8F4E (x.com/home)
- **Data**: ~69 tweets in DB (collected 2026-04-18)
- **Coverage ratio**: 1.909x (xtracker calibration)
- **Real daily rate**: ~57 tweets/day

### Hourly Collection (via HEARTBEAT)
1. Navigate: `browser(action="navigate", target="host", profile="chrome", targetId="B8795CA0F4574E46F3E6F21B1D5F8F4E", url="https://x.com/home")`
2. Extract JS: `(function(){var r=[];var a=document.querySelectorAll('article[role=article]');for(var i=0;i<a.length;i++){var el=a[i];var pid='';var ls=el.querySelectorAll('a[href]');for(var j=0;j<ls.length;j++){var m=ls[j].href.match(/\\/status\\/(\\d+)/);if(m){pid=m[1];break;}}var t=el.querySelector('time');var ts=t?(t.getAttribute('datetime')||''):'';var txt=el.querySelector('[data-testid=tweetText]');var tx=txt?(txt.innerText||''):'';var like=el.querySelector('[data-testid=like]');var ln=like?(like.innerText||'0').replace(/,/g,''):'0';var rt=el.querySelector('[data-testid=retweet]');var rn=rt?(rt.innerText||'0').replace(/,/g,''):'0';r.push({p:pid,t:ts,x:tx.substring(0,100),ln:ln,rn:rn});}return JSON.stringify(r);})()`
3. Scroll JS: `window.scrollTo(0,document.body.scrollHeight)`
4. Collect 8 scrolls with 2s delay between each
5. Store: `python simple_collect.py` (via Node.js CLI: `node C:\\...\\openclaw\\openclaw.mjs browser evaluate --fn ...`)
6. Analyze: `python quick_check.py` in tracker dir
7. Alert if edge > 15%: send Feishu to TP

### Markets
| Market | Target | xtracker | Price | Edge |
|--------|--------|----------|-------|------|
| apr14-21 | 190 | 116 | 57% | +46% |
| apr17-24 | 200 | 7 | 50% | +50% |
| may2026 | 800 | 0 | 50% | +50% |

### Collection Script (simple_collect.py)
- **Command**: `python simple_collect.py [n_scrolls]`
- **Node.js**: `C:\\Program Files\\nodejs\\node.exe`
- **Output**: `data/tweets_latest.json`, `output/latest_snapshot.json`
"""

# Find and replace the existing Polymarket section
import re
pattern = r"## Polymarket Elon Tracker.*?(?=\n## |\Z)"
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_section + "\n", content, flags=re.DOTALL)
else:
    # Prepend after the first heading
    content = new_section + "\n" + content

heartbeat.write_text(content, "utf-8", newline="\n")
print("Updated HEARTBEAT.md")
