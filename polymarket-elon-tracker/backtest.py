#!/usr/bin/env python3
"""
Backtest: Historical tweet-count strategy vs Polymarket Elon markets.
Uses real tweet velocity data to simulate strategy decisions day-by-day.

Historical data source: 269-tweet dataset (Apr 4-18) + Browser Relay DB
Coverage: 1.909x (xtracker calibration)
"""
import json
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
OUT_DIR = PROJECT_ROOT / "output"
COV = 42.0 / 22.0  # 1.909
# COVERAGE means: true_tweets = home_feed_tweets * COV
# xtracker Apr16-18=42 true, our feed Apr16-18=22 → COV=1.909

# ── Historical daily tweet counts (raw home feed, from 269-tweet dataset) ──
HISTORICAL_RAW = {
    "2026-04-12": 28,  # Historical spike (DOGE/policy?)
    "2026-04-13": 21,  # South Africa controversy
    "2026-04-14": 14,  # Normal
    "2026-04-15": 13,  # Normal
    "2026-04-16": 11,  # Normal
    "2026-04-17": 45,  # xAI product launch day!
    "2026-04-18": 10,  # Partial day (morning snapshot)
}

# Coverage-corrected real daily counts
HISTORICAL_REAL = {d: int(c * COV) for d, c in HISTORICAL_RAW.items()}

# ── Market definitions ──
MARKETS = {
    "apr14-21": {
        "target": 190, "ws": "2026-04-14", "we": "2026-04-21",
        "xtracker_snap": 116, "snap_date": "2026-04-18",
        "market_price": 0.57,  # approximate from analysis
    },
    "apr17-24": {
        "target": 200, "ws": "2026-04-17", "we": "2026-04-24",
        "xtracker_snap": 7, "snap_date": "2026-04-18",
        "market_price": 0.50,
    },
    "may2026": {
        "target": 800, "ws": "2026-05-01", "we": "2026-05-31",
        "xtracker_snap": 0, "snap_date": "2026-04-18",
        "market_price": 0.50,
    },
}

print("Historical daily tweet counts (real, coverage-corrected):")
print(f"  {'Date':<14} {'Raw':>5} {'Real':>5} {'Signal':<8} Note")
print("  " + "-" * 55)
for d, raw in sorted(HISTORICAL_RAW.items()):
    real = HISTORICAL_REAL[d]
    note = ""
    if d == "2026-04-12": note = "spike (DOGE)"
    elif d == "2026-04-13": note = "S.Africa"
    elif d == "2026-04-17": note = "xAI launch!"
    bar = "█" * min(real // 5, 18)
    print(f"  {d:<14} {raw:>5} {real:>5} {bar} {note}")
print()


def parse_dt(s):
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def cum_tweets_in_window(target_date, ws_str, we_str):
    """Cumulative tweets in window up to target_date (inclusive)."""
    ws = parse_dt(ws_str + "T00:00:00+00:00")
    we = parse_dt(we_str + "T23:59:59+00:00")
    td = parse_dt(target_date + "T23:59:59+00:00")
    total = 0
    for d, raw in HISTORICAL_RAW.items():
        dd = parse_dt(d + "T12:00:00+00:00")
        if ws <= dd <= we and ws <= dd <= td:
            total += HISTORICAL_REAL[d]
    return total


def mc3(cur, tgt, days, daily, n=30000):
    if days <= 0:
        return 1.0 if cur >= tgt else 0.0
    sc = [("bear", daily * 0.7, 0.20), ("base", daily, 0.50), ("bull", daily * 1.5, 0.30)]
    all_vw, tw = [], 0
    rng = random.Random(x=42)
    for nm, rate, wt in sc:
        lam = max(rate * days, 0.5)
        std = max(math.sqrt(lam), 0.5)
        vs = [max(0, int(round(cur + rng.gauss(lam, std)))) for _ in range(n)]
        all_vw.extend((v, wt) for v in vs)
        tw += wt * n
    pw = sum(w for v, w in all_vw if v >= tgt) / tw
    return round(pw, 4)


def kelly(entry, prob):
    if entry <= 0 or entry >= 1:
        return 0.0
    b = 1.0 / entry - 1.0
    q = 1.0 - prob
    if b <= 0:
        return 0.0
    return max(0.0, (b * prob - q) / b)


def velocity_signal(cur, tgt, days_left, daily_rate):
    """
    Compute velocity-based signal.
    Returns: (req_rate, vel_ratio, signal)
    """
    if days_left <= 0:
        return 0, 0, "RESOLVED"
    rem = max(tgt - cur, 0)
    req_rate = rem / days_left if days_left > 0 else 999
    vel_ratio = daily_rate / req_rate if req_rate > 0 else 99
    if vel_ratio >= 1.5:
        signal = "STRONG_BUY"
    elif vel_ratio >= 1.1:
        signal = "BUY"
    elif vel_ratio >= 0.9:
        signal = "NO_EDGE"
    elif vel_ratio >= 0.7:
        signal = "LEAN_NO"
    else:
        signal = "STRONG_NO"
    return req_rate, vel_ratio, signal


def run_backtest():
    print("=" * 70)
    print("  STRATEGY BACKTEST — Day-by-day signal simulation")
    print("=" * 70)
    print()

    all_signals = defaultdict(list)
    dates = sorted(HISTORICAL_REAL.keys())

    for i, date in enumerate(dates):
        now_dt = parse_dt(date + "T12:00:00+00:00")
        today_rate = HISTORICAL_REAL[date]  # today's real tweet rate

        for mid, m in MARKETS.items():
            tgt = m["target"]
            ws, we = m["ws"], m["we"]
            ws_dt = parse_dt(ws + "T00:00:00+00:00")
            we_dt = parse_dt(we + "T23:59:59+00:00")

            days_left = max((we_dt - now_dt).total_seconds() / 86400.0, 0)
            days_in_window = max((now_dt - ws_dt).total_seconds() / 86400.0, 0)

            # Cumulative tweets in window (real, coverage-corrected)
            cum = 0
            for d2, raw2 in HISTORICAL_RAW.items():
                d2_dt = parse_dt(d2 + "T12:00:00+00:00")
                if ws_dt <= d2_dt <= now_dt:
                    cum += int(raw2 * COV)

            # MC probability
            p_yes = mc3(cum, tgt, days_left, today_rate)
            edge = p_yes - 0.50

            # Velocity signal
            req_rate, vel_ratio, vel_signal = velocity_signal(cum, tgt, days_left, today_rate)

            # Kelly
            mkt_price = m["market_price"]
            implied_prob = 1 - mkt_price  # YES probability from market
            edge_vs_mkt = p_yes - implied_prob
            kf = kelly(mkt_price, p_yes)

            if edge_vs_mkt > 0.15:
                action = "BUY_YES"
            elif edge_vs_mkt < -0.15:
                action = "BUY_NO"
            else:
                action = "NO_EDGE"

            sig = {
                "date": date,
                "cum_est": cum,
                "target": tgt,
                "days_left": round(days_left, 1),
                "today_rate": today_rate,
                "p_yes": round(p_yes, 3),
                "edge": round(edge, 3),
                "edge_vs_mkt": round(edge_vs_mkt, 3),
                "edge_vs_mkt_pct": f"{edge_vs_mkt*100:+.1f}%",
                "req_rate": round(req_rate, 1),
                "vel_ratio": round(vel_ratio, 2),
                "vel_signal": vel_signal,
                "action": action,
                "kelly_quarter": round(kf * 0.25, 4),
                "market_price": mkt_price,
            }
            all_signals[mid].append(sig)

    # Print signals
    for mid, sigs in sorted(all_signals.items()):
        m = MARKETS[mid]
        print(f"\n{'='*60}")
        print(f"  [{mid}] Target: {m['target']} | Market: {m['market_price']:.0%}")
        print(f"{'='*60}")
        print(f"  {'Date':<14} {'Cum(est)':>8} {'DaysL':>5} {'Rate':>5} {'ReqRate':>6} "
              f"{'VelR':>5} {'P(YES)':>6} {'Edge%':>7} {'Action':<12}")
        print(f"  {'-'*75}")

        for s in sigs:
            bar = ""
            if s["action"] == "BUY_YES":
                bar = "  >>>"
            elif s["action"] == "BUY_NO":
                bar = "  <<<"
            print(f"  {s['date']:<14} {s['cum_est']:>8} {s['days_left']:>5.1f} "
                  f"{s['today_rate']:>5} {s['req_rate']:>6.1f} {s['vel_ratio']:>5.2f} "
                  f"{s['p_yes']*100:>5.0f}% {s['edge_vs_mkt_pct']:>7} {s['action']:<12}{bar}")

    return all_signals


def analyze_results(signals):
    print("\n" + "=" * 70)
    print("  PERFORMANCE ANALYSIS")
    print("=" * 70)

    # For each market, compute: total signals, accuracy
    # Since markets aren't resolved yet, compute expected value
    total_expected_ev = 0
    bankroll = 1000.0

    for mid, sigs in sorted(signals.items()):
        m = MARKETS[mid]
        buys = [s for s in sigs if s["action"] == "BUY_YES"]
        sells = [s for s in sigs if s["action"] == "BUY_NO"]

        print(f"\n  [{mid}] {m['target']} tweets")
        print(f"    Market price: {m['market_price']:.0%} YES")
        print(f"    BUY_YES signals: {len(buys)}")
        print(f"    BUY_NO signals: {len(sells)}")

        if buys:
            avg_edge = sum(s["edge_vs_mkt"] for s in buys) / len(buys)
            avg_p = sum(s["p_yes"] for s in buys) / len(buys)
            avg_kq = sum(s["kelly_quarter"] for s in buys) / len(buys)
            print(f"    Avg P(YES): {avg_p*100:.0f}% | Avg Edge: {avg_edge*100:+.1f}% | Avg Kellyq: {avg_kq*100:.1f}%")

            # Expected EV per $1000 traded
            # Win: profit = entry * (1/entry - 1) = 1 - entry; Loss: -entry
            entry = m["market_price"]
            wins = avg_p
            loss = 1 - wins
            net = wins * (1 - entry) - loss * entry
            print(f"    Expected return per $1 traded: ${net:.3f}")

        # Update bankroll simulation
        for s in buys:
            pos = bankroll * s["kelly_quarter"]
            win_prob = s["p_yes"]
            entry = m["market_price"]
            # Expected value: win*profit - loss*cost
            ev = win_prob * pos * (1/entry - 1) - (1 - win_prob) * pos
            bankroll += ev * 0.1  # conservative scaling

    print(f"\n  Simulated bankroll (conservative): ${bankroll:.2f} (from $1000)")
    return bankroll


def cross_validate():
    """Cross-validate coverage ratio with xtracker."""
    print("\n" + "=" * 70)
    print("  XTRACKER COVERAGE VALIDATION")
    print("=" * 70)

    # xtracker snapshot Apr18 02:15 HKT:
    # Apr14-21: 116 confirmed
    # Apr16-18: 42 confirmed (3 days)
    # Our home feed Apr16-18: raw counts = 11+45+10 = 66, est = 66*1.909 = 126
    # But our home feed only captured Apr17-18: 45+10 = 55, est = 105

    xtracker = {
        "apr14-21": {"confirmed": 116, "days": 8},
        "apr16-18": {"confirmed": 42, "days": 3},
    }

    our_apr17_18_raw = HISTORICAL_RAW.get("2026-04-17", 0) + HISTORICAL_RAW.get("2026-04-18", 0)
    our_apr16_18_raw = HISTORICAL_RAW.get("2026-04-16", 0) + our_apr17_18_raw

    print(f"\n  Apr16-18 window (3 days):")
    print(f"    xtracker: {xtracker['apr16-18']['confirmed']} tweets")
    print(f"    Our home feed (raw): {our_apr16_18_raw} tweets")
    cov1 = xtracker["apr16-18"]["confirmed"] / our_apr16_18_raw
    print(f"    Coverage: {cov1:.3f}x")
    print(f"    Our assumed: {COV:.3f}x  (delta: {cov1 - COV:+.3f})")

    print(f"\n  Apr14-21 window:")
    print(f"    xtracker: {xtracker['apr14-21']['confirmed']} tweets in 8 days")
    our_8day_raw = sum(HISTORICAL_RAW.get(d, 0) for d in HISTORICAL_RAW)
    print(f"    Our home feed (8 days, raw): {our_8day_raw} tweets")
    cov2 = xtracker["apr14-21"]["confirmed"] / our_8day_raw
    print(f"    Coverage: {cov2:.3f}x")
    print(f"    Our assumed: {COV:.3f}x  (delta: {cov2 - COV:+.3f})")

    # Reconciliation
    avg_cov = (cov1 + cov2) / 2
    print(f"\n  Average coverage: {avg_cov:.3f}x")
    print(f"  Previous assumed: {COV:.3f}x")
    print(f"  -> Update daily rate: {30*COV:.0f}/day -> {30*avg_cov:.0f}/day")
    print(f"  -> Apr14-21 real estimate: {xtracker['apr14-21']['confirmed']} (vs {int(our_8day_raw * COV)} assumed)")
    print(f"  -> Apr14-21 xtracker/our_est ratio: {xtracker['apr14-21']['confirmed'] / (our_8day_raw * COV):.2f}x")

    return avg_cov


if __name__ == "__main__":
    signals = run_backtest()
    ev = analyze_results(signals)
    avg_cov = cross_validate()

    OUT_DIR.mkdir(exist_ok=True)
    save = {
        "signals": dict(signals),
        "historical_raw": HISTORICAL_RAW,
        "historical_real": HISTORICAL_REAL,
        "coverage": COV,
        "avg_coverage_from_validation": avg_cov,
        "simulated_bankroll": round(ev, 2),
        "run_time": datetime.now(timezone.utc).isoformat(),
    }
    fp = OUT_DIR / "backtest_results.json"
    fp.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = OUT_DIR / "backtest_latest.json"
    latest.write_text(json.dumps(save, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {fp}")
