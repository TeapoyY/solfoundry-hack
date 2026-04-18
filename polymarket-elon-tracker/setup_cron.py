#!/usr/bin/env python3
"""Update the polymarket-elon-monitor cron job to use sub-agent."""
import subprocess

TASK_PROMPT = """You are the xTracker Clone collector for Polymarket Elon Musk tweet markets.

## Your Job
Every hour: collect tweets via Chrome Browser Relay, store to SQLite, analyze, alert.

## Chrome Browser Relay
- Tab: B8795CA0F4574E46F3E6F21B1D5F8F4E
- Profile: chrome
- Target: host

## Step 1: Navigate
browser(action="navigate", target="host", profile="chrome", targetId="B8795CA0F4574E46F3E6F21B1D5F8F4E", url="https://x.com/home")
Wait 3 seconds.

## Step 2: Collect Tweets (8 scrolls)
For scroll 1 to 8:
  a. Evaluate JS to extract tweets from current view:
browser(action="act", target="host", profile="chrome", targetId="B8795CA0F4574E46F3E6F21B1D5F8F4E", request={"kind": "evaluate", "fn": "(function(){var r=[];var a=document.querySelectorAll('article[role=article]');for(var i=0;i<a.length;i++){var el=a[i];var pid='';var ls=el.querySelectorAll('a[href]');for(var j=0;j<ls.length;j++){var m=ls[j].href.match(/\\\\/status\\\\/(\\\\d+)/);if(m){pid=m[1];break;}}var t=el.querySelector('time');var ts=t?(t.getAttribute('datetime')||''):'';var txt=el.querySelector('[data-testid=tweetText]');var tx=txt?(txt.innerText||''):'';var like=el.querySelector('[data-testid=like]');var ln=like?(like.innerText||'0').replace(/,/g,''):'0';var rt=el.querySelector('[data-testid=retweet]');var rn=rt?(rt.innerText||'0').replace(/,/g,''):'0';r.push({p:pid,t:ts,x:tx.substring(0,100),ln:ln,rn:rn});}return JSON.stringify(r);})()", "timeoutMs": 25000})

  b. Scroll down:
browser(action="act", target="host", profile="chrome", targetId="B8795CA0F4574E46F3E6F21B1D5F8F4E", request={"kind": "evaluate", "fn": "window.scrollTo(0,document.body.scrollHeight)", "timeoutMs": 5000})

  c. Wait 2.5 seconds: exec with Start-Sleep -Seconds 2.5

Collect ALL tweets from all 8 scrolls. Parse each JS result JSON, deduplicate by post_id.

## Step 3: Save to JSON file
Write all collected tweets to: C:\\Users\\Administrator\\.openclaw\\workspace\\polymarket-elon-tracker\\data\\tweets_latest.json
Format: {"tweets": [...list of tweet dicts...], "count": N, "collected_at": "ISO timestamp"}

Each tweet dict: {"post_id": "...", "timestamp": "ISO", "text": "...", "hour": N, "weekday": "Mon...", "likes": N, "retweets": N, "replies": 0, "views": 0, "is_pinned": false, "has_media": false}

## Step 4: Store to SQLite
exec: C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -c "import sys,json; sys.path.insert(0,r'C:\\Users\\Administrator\\.openclaw\\workspace\\polymarket-elon-tracker'); from src.database import TweetDB; from collect import store_tweets; db=TweetDB(); data=json.load(open(r'C:\\Users\\Administrator\\.openclaw\\workspace\\polymarket-elon-tracker\\data\\tweets_latest.json')); n=db.bulk_upsert(data.get('tweets',[])); print('Stored',n,'new, total',db.total_tweets())"

## Step 5: Analyze
exec: C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe C:\\Users\\Administrator\\.openclaw\\workspace\\polymarket-elon-tracker\\quick_check.py

## Step 6: Feishu Alert
If any market has edge greater than 0.15 (15%), send a Feishu message to user:ou_f3e81aedea89d300caca6e83bb0edeca with:
- Market analysis summary (confirmed count, P(YES), Edge, Kelly fraction)
- Recommendation: BUY_YES / BUY_NO / NO_EDGE
- Brief reasoning

## Market Data
| Market | Target | xtracker confirmed |
|--------|--------|-------------------|
| apr14-21 | 190 | 116 |
| apr17-24 | 200 | 7 |
| may2026 | 800 | 0 |

Coverage ratio: 1.909x (xtracker calibration: 42 tweets Apr16-18 / our 22)
Real daily rate: ~57 tweets/day

## After completing
Report: total tweets collected, DB total, analysis results for each market.
"""

# Write task to file
task_file = r"C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\cron_task.txt"
with open(task_file, "w", encoding="utf-8") as f:
    f.write(TASK_PROMPT)
print(f"Task written to: {task_file}")

# Try to update cron via openclaw CLI
result = subprocess.run(
    ["openclaw", "cron", "list"],
    capture_output=True, text=True
)
print("Cron list:", result.stdout[:500], result.stderr[:200])
