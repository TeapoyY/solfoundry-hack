# Polymarket Elon Real-time Collector Task

## Context
You are running the xTracker Clone tweet collector for Polymarket Elon Musk markets.
Your Chrome Browser Relay is connected and authenticated at tab `B8795CA0F4574E46F3E6F21B1D5F8F4E`.

## Your Task (run every hour)

### Step 1: Navigate to x.com/home
```json
{"action": "navigate", "target": "host", "profile": "chrome", "targetId": "B8795CA0F4574E46F3E6F21B1D5F8F4E", "url": "https://x.com/home"}
```
Wait 3 seconds.

### Step 2: Collect tweets (10 scrolls)
For each scroll (0-9):
1. Evaluate this JS to extract tweets:
```json
{"action": "act", "target": "host", "profile": "chrome", "targetId": "B8795CA0F4574E46F3E6F21B1D5F8F4E", "request": {"kind": "evaluate", "fn": "(function(){var r=[];var a=document.querySelectorAll('article[role=article]');for(var i=0;i<a.length;i++){var el=a[i];var pid='';var ls=el.querySelectorAll('a[href]');for(var j=0;j<ls.length;j++){var m=ls[j].href.match(/\\\\/status\\\\/(\\\\d+)/);if(m){pid=m[1];break;}}var t=el.querySelector('time');var ts=t?(t.getAttribute('datetime')||''):'';var txt=el.querySelector('[data-testid=tweetText]');var tx=txt?(txt.innerText||''):'';var like=el.querySelector('[data-testid=like]');var ln=like?(like.innerText||'0').replace(/,/g,''):'0';var rt=el.querySelector('[data-testid=retweet]');var rn=rt?(rt.innerText||'0').replace(/,/g,''):'0';r.push({p:pid,t:ts,x:tx.substring(0,100),ln:ln,rn:rn});}return JSON.stringify(r);})()", "timeoutMs": 25000}}
```
2. Parse the result JSON and store unique tweets
3. Scroll down:
```json
{"action": "act", "target": "host", "profile": "chrome", "targetId": "B8795CA0F4574E46F3E6F21B1D5F8F4E", "request": {"kind": "evaluate", "fn": "window.scrollTo(0,document.body.scrollHeight)", "timeoutMs": 5000}}
```
4. Wait 2.5 seconds

### Step 3: Store to SQLite
Run this Python:
```bash
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe -c "
import sys; sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker')
from src.database import TweetDB
from collect import store_tweets
import json
# tweets_json = <tweets from JS>
db = TweetDB()
n, parsed = store_tweets(db, tweets_json)
print(f'Stored +{n} tweets, total: {db.total_tweets()}')
"
```

### Step 4: Run Analysis
```bash
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe -c "
import sys; sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker')
from src.database import TweetDB
from src.analyzer import analyze, print_results
db = TweetDB()
results = analyze(db)
# Save to output/
"
```

### Step 5: Send Feishu Alert
If any market has edge > 0.15 (15%), send a Feishu message to TP (ou_f3e81aedea89d300caca6e83bb0edeca) with the analysis summary.

## Tweet storage format
```python
{
    "post_id": "2045271774925918337",
    "timestamp": "2026-04-17T22:42:45Z",
    "text": "Tweet text...",
    "hour": 22,
    "weekday": "Thu",
    "likes": 72000,
    "retweets": 6100,
    "replies": 0, "views": 0,
    "is_pinned": False, "has_media": False,
}
```

## Projects paths
- Tracker: `C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\`
- DB: `C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\data\tracker.db`
- Tweet data: `C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\data\tweets_latest.json`

## Key constants
- COVERAGE_RATIO = 42/22 = 1.909 (xtracker calibration)
- REAL_DAILY = 30 * 1.909 = ~57.3 tweets/day
- Target markets:
  - Apr14-21: 190 tweets, 116 confirmed at snapshot
  - Apr17-24: 200 tweets, 7 confirmed at snapshot  
  - May2026: 800 tweets, 0 confirmed at snapshot
