"""
Hourly Analysis Runner for Polymarket Elon Tracker
===================================================
Designed to run reliably from cron (no browser relay dependency).
Uses hardcoded Polymarket prices/buckets + our tweet data for pattern analysis.
Saves report to output/ and prints a ready-to-copy Feishu message.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

TRACKER_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker")
sys.path.insert(0, str(TRACKER_DIR / "src"))

from full_analyzer import analyze_market, MARKETS, load_live_xtrack, mc_final_count, DAILY_RATE, PEAK_HOURS

PY = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"


def get_current_utc_hour():
    return datetime.now(timezone.utc).hour


def hourly_pattern_analysis(tweets: list, now_utc: datetime) -> dict:
    """
    Analyze tweet patterns by hour of day.
    Returns per-hour rates and identifies peak/slow windows.
    """
    from collections import Counter
    from datetime import timedelta

    if not tweets:
        return {}

    hour_counts = Counter()
    for t in tweets:
        ts_str = t.get("timestamp", "")
        if ts_str:
            try:
                from datetime import datetime as dt
                ts = dt.fromisoformat(ts_str.replace("Z", "+00:00"))
                hour_counts[ts.hour] += 1
            except Exception:
                pass

    total = len(tweets)
    hourly_rates = {}
    for h in range(24):
        cnt = hour_counts.get(h, 0)
        hourly_rates[h] = {
            "count": cnt,
            "pct": round(cnt / total * 100, 1) if total > 0 else 0,
            "tweets_per_hour_if_constant": round(cnt / max(total, 1) * 30, 1),
        }

    # Peak hours (top 6)
    sorted_hours = sorted(hourly_rates.items(), key=lambda x: x[1]["count"], reverse=True)
    peak_hours = [h for h, _ in sorted_hours[:6]]
    quiet_hours = [h for h, _ in sorted_hours if hourly_rates[h]["pct"] < 3][:6]

    # Current hour status
    current_hour = now_utc.hour
    current_rate = hourly_rates.get(current_hour, {}).get("pct", 0)
    is_peak = current_hour in peak_hours[:3]

    return {
        "hourly_rates": hourly_rates,
        "peak_hours_utc": sorted(peak_hours),
        "quiet_hours_utc": sorted(quiet_hours),
        "current_hour_utc": current_hour,
        "current_hour_pct": current_rate,
        "is_peak_window": is_peak,
    }


def hourly_countdown(mkt: dict, now_utc: datetime) -> dict:
    """
    Compute countdown in HOURS not days, with hourly velocity analysis.
    """
    from full_analyzer import parse_ts, load_tweets

    ws = mkt["ws"]
    we = mkt["we"]
    target = mkt["target"]
    confirmed = mkt.get("xtrack_confirmed", 0) or 0

    we_dt = parse_ts(we)
    if not we_dt:
        return {}

    # Hours remaining (precise)
    hours_rem = max((we_dt - now_utc).total_seconds() / 3600.0, 0)

    # tweets needed per hour (not per day)
    tweets_per_hour_needed = round((target - confirmed) / hours_rem, 2) if hours_rem > 0 else 999

    # Daily rate converted to hourly
    tweets_per_hour_real = round(DAILY_RATE / 24, 2)  # ~1.25/hour

    # Peak-hour adjusted rate (if we're in a peak window)
    # Elon's peak hours are ~22:00-01:00 UTC (10pm-1am) and ~07:00-08:00 UTC
    # In peak hours, rate is ~3x the hourly average
    peak_hours = [22, 23, 0, 1, 7, 8]
    current_hour = now_utc.hour
    in_peak = current_hour in peak_hours
    peak_rate = round(tweets_per_hour_real * 2.5, 2) if in_peak else tweets_per_hour_real

    # Next peak window
    next_peak = None
    for h in range(current_hour + 1, current_hour + 12):
        if h % 24 in peak_hours:
            next_peak = h % 24
            break

    # Hourly probability using normal distribution
    import math
    expected_remaining = DAILY_RATE * (hours_rem / 24)
    std_rem = max(math.sqrt(expected_remaining), 1.0)

    # Use base rate MC
    days_rem_h = hours_rem / 24
    mc = mc_final_count(confirmed, days_rem_h)

    return {
        "hours_remaining": round(hours_rem, 1),
        "tweets_needed_per_hour": tweets_per_hour_needed,
        "tweets_per_hour_real_base": tweets_per_hour_real,
        "tweets_per_hour_peak_adjusted": peak_rate,
        "in_peak_window": in_peak,
        "current_hour_utc": current_hour,
        "next_peak_hour_utc": next_peak,
        "hourly_velocity_ratio": round(peak_rate / tweets_per_hour_needed, 2) if tweets_per_hour_needed < 999 else 99,
        "mc": mc,
    }


def format_feishu_message(results: list, hourly_info: dict, tweets: list) -> str:
    """Format the full analysis as a Feishu-ready message."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    current_hour = hourly_info.get("current_hour_utc", 0)
    peak = hourly_info.get("is_peak_window", False)

    # Peak hours label
    peak_hrs = hourly_info.get("peak_hours_utc", [])
    peak_label = f"{peak_hrs[0]:02d}-{peak_hrs[-1]:02d}" if peak_hrs else "?"

    msg = f"""🧠 POLYMARKET ELON TRACKER — HOURLY REPORT
📅 {now} | Current UTC hour: {current_hour:02d}:00 ({'PEAK WINDOW' if peak else 'quiet'} ~{peak_label} UTC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    for r in results:
        mid = r["market_id"]
        hrs = r.get("hours_remaining", {})
        hl = r.get("hourly", {})

        # Status line
        remaining = r.get("remaining_to_target", 0)
        target = r.get("target", 0)
        confirmed = r.get("xtrack_confirmed", 0)

        # Hourly countdown
        h_rem = r.get("hours_remaining", 0)
        per_hour_needed = r.get("tweets_needed_per_hour", 999)
        per_hour_real = r.get("tweets_per_hour_real_base", 0)
        in_peak = r.get("in_peak_window", False)
        peak_rate = r.get("tweets_per_hour_peak_adjusted", 0)

        # Best combo
        combos = r.get("combos", [])
        top_combo = combos[0] if combos else None

        # Verdict
        verdict = r.get("best_bet", "NO_EDGE")
        edge_yes = r.get("edge_yes_pct", "N/A")
        kelly_q = r.get("kelly_quarter_yes", 0)
        p_yes = r.get("p_yes", 0)
        pm_yes = r.get("yes_price", 0)

        # Emoji for verdict
        if verdict == "BUY_YES":
            emoji = "✅"
        elif verdict == "BUY_NO":
            emoji = "🚫"
        else:
            emoji = "⚠️"

        msg += f"""【{mid.upper()}】{emoji} {verdict}
• xtrack: {confirmed}/{target} | 剩余: {remaining}帖
• ⏱️ {h_rem:.1f}h left | 需要: {per_hour_needed:.1f}/h | 实际(基础): {per_hour_real:.2f}/h
• {'🌙 PEAK时: ' + str(peak_rate) + '/h | IN PEAK WINDOW' if in_peak else '☀️ 非高峰时段'}
• PM: {pm_yes:.0%} | 我们的P: {p_yes:.0%} | Edge: {edge_yes} | Kelly¼: {kelly_q*100:.0f}%

"""

        # Top combo
        if top_combo and top_combo.get("combo_edge", 0) > 0.05:
            c = top_combo
            msg += f"""  🎯 Top Combo: {c['combo_label']}
     概率{c['combo_prob_pct']} | 成本{c['combo_cost_pct']} | Edge {c['combo_edge_pct']} | Kelly¼ {c['kelly_quarter']*100:.0f}%

"""

        msg += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Hourly pattern
    peak_str = ",".join(f"{h:02d}:00" for h in peak_hrs[:4])
    quiet_hrs = hourly_info.get("quiet_hours_utc", [])
    quiet_str = ",".join(f"{h:02d}:00" for h in quiet_hrs[:3])

    msg += f"""📊 ELON发帖模式(UTC)
🌙 高峰: {peak_str} UTC
☀️ 低谷: {quiet_str} UTC (谨慎时段)
📌 当前{hourly_info['current_hour_utc']:02d}:00 UTC — {'🌙 高峰期' if peak else '☀️ 低谷期'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 规则提醒: 主贴+引用转发+转发=计入 | 纯回复不计入 | 社区转发不计入
🕐 xtrack权威: https://xtrack.polymarket.com
"""

    return msg


def main():
    now_utc = datetime.now(timezone.utc)
    tweets_path = TRACKER_DIR / "data" / "tweets_latest.json"
    tweets = []
    if tweets_path.exists():
        with open(tweets_path, encoding="utf-8") as f:
            data = json.load(f)
        tweets = data.get("tweets", [])

    # Hourly pattern from our collected tweets
    hourly_info = hourly_pattern_analysis(tweets, now_utc)

    # Analyze each market with hourly countdown
    results = []
    for m in MARKETS:
        r = analyze_market(m, now_utc)
        # Add hourly-specific fields
        hl = hourly_countdown(m, now_utc)
        r.update(hl)
        results.append(r)

    # Save snapshot
    out_dir = TRACKER_DIR / "output"
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    save = {
        "collected_at": now_utc.isoformat(),
        "hourly_pattern": hourly_info,
        "results": results,
        "total_tweets": len(tweets),
    }
    latest = out_dir / "latest_hourly_analysis.json"
    fp = out_dir / f"hourly_{ts}.json"
    fp.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")
    latest.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")

    # Format Feishu message
    msg = format_feishu_message(results, hourly_info, tweets)

    # Print ASCII-safe summary to console, save full message to file
    print(f"Analysis complete. {len(results)} markets analyzed.")
    print(f"Top signals:")
    for r in results:
        combos = r.get("combos", [])
        top = combos[0] if combos else None
        if top:
            print(f"  {r['market_id']}: {top['combo_label']} | P={top['combo_prob_pct']} | Edge={top['combo_edge_pct']} | Kelly={top['kelly_quarter']*100:.0f}%")

    # Save full Feishu message to file
    print(f"\n[Saved: {fp.name}]")
    try:
        print(msg)
    except UnicodeEncodeError:
        # Windows console can't print emojis — file save still worked
        pass

    # Save message to file for cron delivery
    msg_file = out_dir / "latest_feishu_msg.txt"
    msg_file.write_text(msg, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
