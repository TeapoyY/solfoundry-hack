# Polymarket Elon Tracker — Collection Fix Report
**Date:** 2026-04-19
**Task:** Fix tweet collector to match xtrack.polymarket.com methodology

---

## What Was Wrong

### 1. Root Cause: x.com/home vs x.com/elonmusk

The `simple_collect.py` was navigating to `x.com/home` (the algorithmic home feed) to collect tweets. This was a fundamental methodology error:

- **x.com/home**: Shows tweets from accounts you follow, ranked by an algorithmic feed. Many tweets are hidden/demoted based on engagement, recency, and other factors. This is why we only captured ~50% of actual tweets.
- **x.com/elonmusk**: Shows ALL tweets from Elon's profile chronologically, including retweets. This is the correct source for counting tweets by Elon.

### 2. Insufficient Scroll Depth

With only 8 scrolls on `x.com/home`, we were capturing only the most recent ~80 tweets. Since Elon posts ~30 tweets/day and we were collecting across a 7-day window, we needed far more scroll depth.

### 3. Stale xtrack Confirmed Count

The hardcoded `xtrack_confirmed` in `full_analyzer.py` was set to **184** (from Apr19 ~11:00 HKT), but the current Polymarket page shows **167** (as of 16:20 HKT). This discrepancy was causing analysis errors.

---

## What Was Fixed

### Fix 1: Changed collection source from `x.com/home` to `x.com/elonmusk`

**File:** `simple_collect.py`

**Before:**
```python
bnav("https://x.com/home")
```

**After:**
```python
url = target_url or "https://x.com/elonmusk"
bnav(url)
# Click Posts tab to ensure we're on the posts feed (not replies/subs/highlights/media)
r = beval(CLICK_POSTS_TAB_JS, ...)
# Scroll to top to start from newest
bscroll_to_top()
```

Added helper functions:
- `bscroll_to_top()` — scroll to top of page before starting collection
- `CLICK_POSTS_TAB_JS` — JavaScript to click the "Posts" tab on profile pages

### Fix 2: Increased default scroll count from 8 to 20

**File:** `simple_collect.py`

**Before:**
```python
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
```

**After:**
```python
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20  # Increased from 8
```

Rationale: At ~10 tweets per scroll, 20 scrolls = ~200 tweets, enough to cover a 7-day window at 30 tweets/day.

### Fix 3: Updated xtrack_confirmed to current Polymarket count

**File:** `src/full_analyzer.py`

**Before:**
```python
"xtrack_confirmed": 184,  # UPDATED 2026-04-19 15:36 HKT
```

**After:**
```python
"xtrack_confirmed": 167,  # UPDATED from Polymarket TWEET COUNT (2026-04-19 16:20 HKT)
```

Verified via browser relay: Polymarket market page for apr14-21 shows **TWEET COUNT = 167**.

---

## Test Results

### Profile Collection Test (5 scrolls):
```
Scroll 1: +9 new (total in window: 9)
Scroll 2: +11 new (total in window: 20)
Scroll 3: +11 new (total in window: 31)
Scroll 4: +11 new (total in window: 42)
Scroll 5: +10 new (total in window: 52)

Total tweets in Apr14-21 window: 52 (in 5 scrolls)
By day:
  2026-04-14: 3 tweets
  2026-04-15: 11 tweets
  2026-04-16: 16 tweets
  2026-04-17: 18 tweets
  2026-04-18: 4 tweets
```

The profile page captures tweets from all days in the window (Apr14-18), unlike the home feed which only had tweets from Apr17-18.

### Analysis Verification (quick_check.py --no-fetch):
```
[apr14-21] xtrack confirmed: 167 / target: 190
Expected final: ~249.4 tweets  P10=215  P90=282
Binary YES @ 88%  edge=+12.0%  Kelly1/4=25.0%
VERDICT: BUY_YES
```

---

## Current Market Data (from Polymarket, via browser relay)

| Market | Window | xtrack Confirmed | Target | Polymarket YES |
|--------|--------|-----------------|--------|---------------|
| apr14-21 | Apr14-21 | **167** | 190 | 88% |
| apr17-24 | Apr17-24 | **68** | 200 | 85% |
| may2026 | May 2026 | **0** (not started) | 800 | 85% |

---

## xtrack Counting Rules (from Polymarket T&Cs)

- ✅ Main feed posts (original tweets)
- ✅ Quote posts (tweet with comment)
- ✅ Reposts / retweets (show in Posts tab of profile)
- ⚠️ Standalone replies on main feed — these are captured but controversial
- ❌ Pure replies do NOT count (shown in separate Replies tab — we skip this)
- ❌ Community reposts do NOT count

---

## Next Steps

1. **Run the fixed collector**: `python simple_collect.py 20` to collect tweets with 20 scrolls from x.com/elonmusk
2. **Run analysis**: `python quick_check.py --no-fetch` to verify counts
3. **Compare with xtrack**: After collection, verify that our count approaches 167 for apr14-21

---

## Known Limitations

1. **Browser session state**: Navigating to x.com/elonmusk may sometimes load cached content. The fix includes scrolling to top before collection to mitigate this.
2. **Infinite scroll timing**: x.com may have slight delays in loading tweets. The 2.5-second wait between scrolls helps.
3. **Retweet timestamps**: When Elon retweets someone, the DOM shows the original tweet's timestamp, not when Elon retweeted. This could cause some retweets to be incorrectly filtered by date window.
4. **Collection speed**: 20 scrolls takes ~45 seconds. Consider running this as a background process for production use.
