#!/usr/bin/env python3
"""
Polymarket Elon - 综合实时分析
输出格式: 每个选项的价格 vs 真实概率 → 边缘 → 决策
"""
import json, math, sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================
# 数据来源1: xtracker.polymarket.com (每小时快照)
# =============================================================
XTRACKER_SNAPSHOT = {
    "collected_at": "2026-04-18T02:15:00+08:00",  # 最后更新
    "markets": {
        "apr14-21": {
            "confirmed": 116,  # xtracker直接确认
            "window_start": "2026-04-14T00:00:00Z",
            "window_end": "2026-04-21T23:59:59Z",
        },
        "apr16-18": {
            "confirmed": 42,   # 历史对照
            "window_start": "2026-04-16T00:00:00Z",
            "window_end": "2026-04-18T23:59:59Z",
        },
        "apr17-24": {
            "confirmed": 7,
            "window_start": "2026-04-17T00:00:00Z",
            "window_end": "2026-04-24T23:59:59Z",
        },
    }
}

# =============================================================
# 数据来源2: Browser Relay 真实推文 (269条/21天)
# =============================================================
# 日均(UTC) — 从Browser Relay采集校正
DAILY_TWEETS = {
    "2026-04-18": 1,  "2026-04-17": 20, "2026-04-16": 11,
    "2026-04-15": 13, "2026-04-14": 11, "2026-04-13": 22,
    "2026-04-12": 32, "2026-04-11": 7,  "2026-04-10": 18,
    "2026-04-09": 14,  "2026-04-08": 7,  "2026-04-07": 19,
    "2026-04-06": 12,  "2026-04-05": 20, "2026-04-04": 10,
    "2026-04-03": 11,  "2026-04-02": 8,  "2026-04-01": 16,
    "2026-04-00": 9,   "2026-03-30": 8,  "2026-03-29": 4,
    "2026-03-28": 7,
}

# xtracker vs Browser Relay 覆盖率验证:
# Apr16-18: xtracker=42, 我们=22 → 覆盖率=22/42=52%
# Apr14-21: xtracker=116 (估算4天)
# 我们的 Apr14-17: 11+13+11+20=55条
# 覆盖率校正: 真实 ≈ 我们 × (42/22) = ×1.91
COVERAGE_RATIO = 42 / 22  # ≈ 1.91

# 真实日均速度 (覆盖率校正后)
our_recent = sum(DAILY_TWEETS.get(f"2026-04-{str(d).zfill(2)}", 0) for d in range(11, 18))
real_recent = our_recent * COVERAGE_RATIO
real_daily_avg = real_recent / 7  # 真实日均

# =============================================================
# 市场定义 (从 Polymarket 实时数据)
# =============================================================
MARKETS = [
    {
        "id": "elon-apr14-21",
        "question": "Elon Musk tweets April 14-21, 2026? (Over 190?)",
        "target": 190,
        "window": ("2026-04-14", "2026-04-21"),
        "yes_price": 0.57,
        "no_price": 0.43,
        "volume": 500000,
        "funded_y": 285000, "funded_n": 215000,
        "xtracker_confirmed": 116,  # xtracker直接数据
        "xtracker_window": ("2026-04-14", "2026-04-21"),
    },
    {
        "id": "elon-apr17-24",
        "question": "Elon Musk tweets April 17-24, 2026? (Over 200?)",
        "target": 200,
        "window": ("2026-04-17", "2026-04-24"),
        "yes_price": 0.50,
        "no_price": 0.50,
        "volume": 100000,
        "funded_y": 50000, "funded_n": 50000,
        "xtracker_confirmed": 7,  # 仅Apr17数据
        "xtracker_window": ("2026-04-17", "2026-04-24"),
    },
    {
        "id": "elon-may2026",
        "question": "Elon Musk tweets May 2026? (Over 800?)",
        "target": 800,
        "window": ("2026-05-01", "2026-05-31"),
        "yes_price": 0.50,
        "no_price": 0.50,
        "volume": 50000,
        "funded_y": 25000, "funded_n": 25000,
        "xtracker_confirmed": 0,
        "xtracker_window": None,
    },
]


def calc_days_left(end_date_str):
    now = datetime.utcnow()
    try:
        end = datetime.strptime(end_date_str, "%Y-%m-%d")
        delta = end - now
        return max(delta.total_seconds() / 86400, 0)
    except:
        return 0


def normal_cdf(x, mu=0, sigma=1):
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def kelly(entry_price, implied_prob):
    """Kelly Criterion"""
    odds = 1 / entry_price
    b = odds - 1
    p = implied_prob
    q = 1 - p
    if b <= 0:
        return 0, 0, 0
    full = max(0, (b * p - q) / b)
    return full, full * 0.5, full * 0.25


def monte_carlo_3scenario(current, target, days, coverage=COVERAGE_RATIO):
    """
    三情景Monte Carlo
    Bear: 真实速度 × 0.7
    Base: 真实速度 (覆盖校正后)
    Bull: Elon历史峰值速度 (估计80/天真实)
    """
    import numpy as np

    if days <= 0:
        return {"mean": current, "p_reach": 1.0 if current >= target else 0.0}

    real_base_rate = real_daily_avg  # 覆盖校正后的真实日均

    scenarios = {
        "bear": {"rate": real_base_rate * 0.7, "weight": 0.20},
        "base": {"rate": real_base_rate,        "weight": 0.50},
        "bull": {"rate": 80.0 / coverage,          "weight": 0.30},  # 80/天真实速度
    }

    all_results = []
    scenario_p_reach = {}

    for name, s in scenarios.items():
        lam = s["rate"] * days
        samples = np.random.poisson(lam, size=30000)
        final = current + samples
        p_reach = np.mean(final >= target)
        scenario_p_reach[name] = p_reach
        weighted = [(v, s["weight"]) for v in final]
        all_results.extend(weighted)

    # 加权综合 P(reach)
    total_w = sum(w for _, w in all_results)
    p_reach_weighted = sum(w for v, w in all_results if v >= target) / total_w

    all_results.sort(key=lambda x: x[0])
    median_idx = int(len(all_results) * 0.5)
    weighted_median = all_results[median_idx][0]

    mean_val = sum(v * w for v, w in all_results) / total_w

    return {
        "p_reach": round(p_reach_weighted, 4),
        "mean": round(mean_val, 1),
        "median": int(weighted_median),
        "scenarios": {k: {"p_reach": round(v, 4), "rate": round(scenarios[k]["rate"], 1)}
                     for k, v in scenario_p_reach.items()},
        "real_base_rate_used": round(real_base_rate, 1),
    }


def analyze_market(mkt):
    """完整分析一个市场"""
    target = mkt["target"]
    yes_price = mkt["yes_price"]
    no_price = mkt["no_price"]
    funded_y = mkt["funded_y"]
    funded_n = mkt["funded_n"]
    confirmed = mkt["xtracker_confirmed"]

    end_date = mkt["window"][1]
    days_left = calc_days_left(end_date)

    now = datetime.utcnow()

    if mkt["id"] == "elon-apr14-21":
        # Apr14-21: 从Apr14 00:00到Apr18现在
        window_start = datetime.strptime("2026-04-14", "%Y-%m-%d")
        elapsed_days = (now - window_start).total_seconds() / 86400
        elapsed_days = min(elapsed_days, 4.5)  # 钳制到Apr18晚上

        remaining = max(target - confirmed, 0)
        required_rate = remaining / days_left if days_left > 0 else 999
        velocity_ratio = real_daily_avg / required_rate if required_rate > 0 else 999

        mc = monte_carlo_3scenario(confirmed, target, days_left)
        p_yes = mc["p_reach"]
        p_no = 1 - p_yes

        edge_yes = p_yes - yes_price
        edge_no = p_no - no_price

        kelly_f, kelly_h, kelly_q = kelly(yes_price, p_yes)

        # 置信度来源分解
        confidence_velocity = min(velocity_ratio / 3.0, 1.0) if velocity_ratio < 3 else 1.0
        confidence_mc = p_yes
        confidence_bayesian = min((confirmed / target) * (1 / days_left * 7) if days_left > 0 else 1.0, 1.0)
        ensemble = 0.35 * confidence_velocity + 0.35 * confidence_mc + 0.30 * confidence_bayesian
        ensemble = min(ensemble, 0.98)

    elif mkt["id"] == "elon-apr17-24":
        # Apr17-24: 仅7条确认(apr17部分数据)
        # Apr17已过, 但仅确认7条 → Apr18 00:00到Apr24
        window_start = datetime.strptime("2026-04-17", "%Y-%m-%d")
        elapsed = (now - window_start).total_seconds() / 86400
        elapsed = min(elapsed, 1.5)  # Apr17整天 + Apr18半天

        remaining = max(target - confirmed, 0)
        required_rate = remaining / days_left if days_left > 0 else 999
        velocity_ratio = real_daily_avg / required_rate if required_rate > 0 else 999

        mc = monte_carlo_3scenario(confirmed, target, days_left)
        p_yes = mc["p_reach"]
        p_no = 1 - p_yes

        edge_yes = p_yes - yes_price
        edge_no = p_no - no_price

        kelly_f, kelly_h, kelly_q = kelly(yes_price, p_yes)

        ensemble = 0.30 * min(velocity_ratio / 3.0, 1.0) + 0.40 * p_yes + 0.30 * min(p_yes * 0.5, 1.0)
        ensemble = min(ensemble, 0.95)

    else:  # may2026
        remaining = target
        required_rate = remaining / days_left if days_left > 0 else 999
        velocity_ratio = real_daily_avg / required_rate if required_rate > 0 else 999

        mc = monte_carlo_3scenario(0, target, days_left)
        p_yes = mc["p_reach"]
        p_no = 1 - p_yes

        edge_yes = p_yes - yes_price
        edge_no = p_no - no_price

        kelly_f, kelly_h, kelly_q = kelly(yes_price, p_yes)

        ensemble = 0.30 * min(velocity_ratio / 2.0, 1.0) + 0.40 * p_yes + 0.30 * p_yes
        ensemble = min(ensemble, 0.95)

    # 决策
    if edge_yes > 0.10:
        decision = "✅ BUY_YES"
    elif edge_no > 0.10:
        decision = "✅ BUY_NO"
    elif edge_yes > 0.03:
        decision = "⚠️ WEAK_YES"
    elif edge_no > 0.03:
        decision = "⚠️ WEAK_NO"
    else:
        decision = "❌ NO_EDGE"

    return {
        # 基础数据
        "market_id": mkt["id"],
        "question": mkt["question"],
        "target": target,
        "window": f"{mkt['window'][0]} ~ {mkt['window'][1]}",
        "days_left": round(days_left, 2),
        "xtracker_confirmed": confirmed,
        "volume": mkt["volume"],
        # YES边
        "yes_price": yes_price,
        "yes_implied_prob": yes_price,
        "yes_actual_prob": round(p_yes, 4),
        "yes_edge": round(edge_yes, 4),
        "yes_edge_pct": f"{edge_yes*100:+.1f}%",
        # NO边
        "no_price": no_price,
        "no_implied_prob": no_price,
        "no_actual_prob": round(p_no, 4),
        "no_edge": round(edge_no, 4),
        "no_edge_pct": f"{edge_no*100:+.1f}%",
        # 速度分析
        "velocity_ratio": round(velocity_ratio, 2),
        "required_rate": round(required_rate, 1),
        "real_daily_rate": round(real_daily_avg, 1),
        # Monte Carlo
        "mc_p_reach": mc["p_reach"],
        "mc_mean_final": mc["mean"],
        "mc_scenarios": mc.get("scenarios", {}),
        # Kelly
        "kelly_full": round(kelly_f, 4),
        "kelly_half": round(kelly_h, 4),
        "kelly_quarter": round(kelly_q, 4),
        "kelly_quarter_pct": f"{kelly_q*100:.1f}%",
        # 综合
        "ensemble_confidence": round(ensemble, 4),
        "decision": decision,
    }


def format_report(results):
    """生成格式化的对比报告"""
    lines = []
    sep = "═" * 72

    lines.append(sep)
    lines.append("  POLYMARKET ELON — 实时分析 (价格 vs 概率对比)")
    lines.append(f"  生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"  数据: xtracker实时 + BrowserRelay(269条/21天) × {COVERAGE_RATIO:.2f}校正")
    lines.append(f"  真实日均: {real_daily_avg:.1f}条/天 (覆盖率校正后)")
    lines.append(sep)

    for r in results:
        lines.append(f"\n{'─' * 72}")
        lines.append(f"📊 {r['question']}")
        lines.append(f"   窗口: {r['window']} | 剩余: {r['days_left']}天 | xtracker确认: {r['xtracker_confirmed']}条 | 目标: {r['target']}条")
        lines.append("")

        # 价格 vs 概率 对比
        lines.append(f"   {'选项':<8} {'价格(概率隐含)':>16} {'真实概率':>12} {'边缘':>10} {'Kelly¼':>10}")
        lines.append(f"   {'─'*8} {'─'*16} {'─'*12} {'─'*10} {'─'*10}")
        lines.append(f"   {'YES':<8} {r['yes_price']:>16.0%} {r['yes_actual_prob']:>12.1%} {r['yes_edge_pct']:>10} {r['kelly_quarter_pct']:>10}")
        lines.append(f"   {'NO':<8} {r['no_price']:>16.0%} {r['no_actual_prob']:>12.1%} {r['no_edge_pct']:>10} {'—':>10}")

        lines.append("")
        # 速度分析
        lines.append(f"   【速度分析】 真实日均:{r['real_daily_rate']}/天 | 需达:{r['required_rate']:.1f}/天 | 速度比:{r['velocity_ratio']:.2f}x")

        # Monte Carlo 三情景
        mc = r.get("mc_scenarios", {})
        if mc:
            bear = mc.get("bear", {})
            base = mc.get("base", {})
            bull = mc.get("bull", {})
            lines.append(f"   【Monte Carlo】 Bear:{bear.get('p_reach',0)*100:.0f}%(假设{round(bear.get('rate',0),1)}/天) | Base:{base.get('p_reach',0)*100:.0f}%({round(base.get('rate',0),1)}/天) | Bull:{bull.get('p_reach',0)*100:.0f}%({round(bull.get('rate',0),1)}/天)")
            lines.append(f"              加权P(达成): {r['mc_p_reach']*100:.1f}% | 预测均值: {r['mc_mean_final']:.0f}条")

        lines.append("")
        lines.append(f"   ✅ 决策: {r['decision']}")
        lines.append(f"   综合置信度: {r['ensemble_confidence']*100:.1f}%")

    lines.append(f"\n{sep}")
    lines.append("  说明: 真实概率 = 三情景MC加权 | 边缘 = 真实概率 - 价格隐含概率")
    lines.append("  Kelly¼ = ¼Kelly仓位(建议) | 速度比 = 真实日均/需达日均")
    lines.append(sep)
    return "\n".join(lines)


if __name__ == "__main__":
    results = [analyze_market(m) for m in MARKETS]
    report = format_report(results)
    print(report)

    # 保存
    out_dir = PROJECT_ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    fp = out_dir / "realtime_analysis_latest.json"
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {fp}")
