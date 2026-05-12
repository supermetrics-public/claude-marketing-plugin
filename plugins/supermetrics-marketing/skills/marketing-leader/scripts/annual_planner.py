#!/usr/bin/env python3
"""
Annual planning analyzer.

Classifies channels by stability and growth, models budget scenarios for
next period. Used for annual marketing plan preparation.

Expected CSV columns:
    - channel (or platform)
    - month (YYYY-MM, or any date — script aggregates monthly)
    - spend
    - revenue (or conversion_value)
    - conversions

Usage:
    python annual_planner.py monthly.csv \
        --next-period-budget 1500000 \
        --output plan.csv

The script classifies each channel into one of:
    - stable_performer: flat ROAS, low variance, predictable
    - growing: improving ROAS or growing volume
    - declining: deteriorating ROAS or volume
    - volatile: high variance, hard to predict

Then models 3 scenarios:
    - hold: current mix, current total spend
    - growth: total spend +20%, weighted toward growing channels
    - efficiency: same total, weighted toward stable+growing, declining channels reduced
"""

import argparse
import sys
import csv
from collections import defaultdict
from datetime import datetime
from statistics import mean, stdev


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Monthly channel-level CSV")
    p.add_argument("--channel-col", default="channel")
    p.add_argument("--month-col", default="month", help="Month or date column")
    p.add_argument("--next-period-budget", type=float, default=None, help="Target spend for next period (default: same as current)")
    p.add_argument("--output", default="-", help="Output CSV (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def parse_month(s):
    """Accept YYYY-MM, YYYY-MM-DD, MM/DD/YYYY, etc. — return YYYY-MM."""
    s = str(s).strip()
    for fmt in ("%Y-%m", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m")
        except ValueError:
            continue
    return s  # fall back to whatever was passed


def classify_channel(months_data):
    """Classify a channel based on its monthly ROAS sequence."""
    months = sorted(months_data.keys())
    if len(months) < 3:
        return "insufficient_data"

    roas_series = []
    spend_series = []
    for m in months:
        d = months_data[m]
        if d["spend"] > 0:
            roas_series.append(d["revenue"] / d["spend"])
            spend_series.append(d["spend"])

    if len(roas_series) < 3:
        return "insufficient_data"

    roas_mean = mean(roas_series)
    roas_std = stdev(roas_series) if len(roas_series) > 1 else 0
    coefficient_of_variation = roas_std / roas_mean if roas_mean > 0 else 0

    # Trend: compare first third to last third
    third = len(roas_series) // 3
    if third == 0:
        return "insufficient_data"
    early = mean(roas_series[:third]) if third > 0 else roas_series[0]
    late = mean(roas_series[-third:]) if third > 0 else roas_series[-1]
    trend_pct = (late - early) / early * 100 if early > 0 else 0

    # Classification
    if coefficient_of_variation > 0.35:
        return "volatile"
    if trend_pct > 15:
        return "growing"
    if trend_pct < -15:
        return "declining"
    return "stable_performer"


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data.", file=sys.stderr)
        return 1

    # Aggregate per (channel, month)
    data = defaultdict(lambda: defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "conversions": 0.0}))
    for r in rows:
        ch = r.get(args.channel_col, "(unknown)")
        m = parse_month(r.get(args.month_col, ""))
        data[ch][m]["spend"] += to_float(r.get("spend") or r.get("cost"))
        data[ch][m]["revenue"] += to_float(r.get("revenue") or r.get("conversion_value"))
        data[ch][m]["conversions"] += to_float(r.get("conversions"))

    # Per channel: classification + totals + recent monthly avg
    summary = {}
    for ch, months in data.items():
        classification = classify_channel(months)
        total_spend = sum(d["spend"] for d in months.values())
        total_rev = sum(d["revenue"] for d in months.values())
        total_conv = sum(d["conversions"] for d in months.values())
        n_months = len(months)
        monthly_avg_spend = total_spend / n_months if n_months > 0 else 0
        roas = total_rev / total_spend if total_spend > 0 else 0
        roas_series = [(d["revenue"] / d["spend"]) for d in months.values() if d["spend"] > 0]
        roas_std = stdev(roas_series) if len(roas_series) > 1 else 0

        summary[ch] = {
            "classification": classification,
            "n_months": n_months,
            "total_spend": total_spend,
            "monthly_avg_spend": monthly_avg_spend,
            "total_revenue": total_rev,
            "total_conversions": total_conv,
            "roas": roas,
            "roas_volatility": roas_std,
        }

    # Build scenarios
    total_current_monthly_spend = sum(d["monthly_avg_spend"] for d in summary.values())
    if args.next_period_budget:
        next_total = args.next_period_budget
    else:
        next_total = total_current_monthly_spend * 12  # annualize

    next_monthly_total = next_total / 12

    # Scenario weights
    weights_hold = {ch: 1.0 for ch in summary}
    weights_growth = {}
    weights_efficiency = {}
    for ch, s in summary.items():
        c = s["classification"]
        weights_growth[ch] = {"growing": 1.4, "stable_performer": 1.1, "declining": 0.7, "volatile": 0.9}.get(c, 1.0)
        weights_efficiency[ch] = {"growing": 1.3, "stable_performer": 1.15, "declining": 0.5, "volatile": 0.85}.get(c, 1.0)

    def allocate(base_spends, weights, total):
        weighted = {ch: base_spends[ch] * weights[ch] for ch in base_spends}
        total_weight = sum(weighted.values())
        if total_weight <= 0:
            return base_spends
        return {ch: total * (w / total_weight) for ch, w in weighted.items()}

    base_monthly = {ch: s["monthly_avg_spend"] for ch, s in summary.items()}
    hold = allocate(base_monthly, weights_hold, next_monthly_total)
    growth = allocate(base_monthly, weights_growth, next_monthly_total * 1.2)
    efficiency = allocate(base_monthly, weights_efficiency, next_monthly_total)

    # Output
    out_rows = []
    for ch in sorted(summary.keys(), key=lambda c: -summary[c]["total_spend"]):
        s = summary[ch]
        out_rows.append({
            "channel": ch,
            "classification": s["classification"],
            "months_observed": s["n_months"],
            "current_monthly_avg_spend": round(s["monthly_avg_spend"], 2),
            "current_roas": round(s["roas"], 2),
            "roas_volatility": round(s["roas_volatility"], 3),
            "hold_monthly_spend": round(hold.get(ch, 0), 2),
            "growth_monthly_spend": round(growth.get(ch, 0), 2),
            "efficiency_monthly_spend": round(efficiency.get(ch, 0), 2),
        })

    fields = ["channel", "classification", "months_observed", "current_monthly_avg_spend",
              "current_roas", "roas_volatility",
              "hold_monthly_spend", "growth_monthly_spend", "efficiency_monthly_spend"]

    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    writer = csv.DictWriter(out_stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out_rows)

    out_stream.write(f"\n--- Scenarios (monthly) ---\n")
    out_stream.write(f"Hold:       ${sum(hold.values()):,.0f} same mix\n")
    out_stream.write(f"Growth:     ${sum(growth.values()):,.0f} (+20% total, weighted to growing channels)\n")
    out_stream.write(f"Efficiency: ${sum(efficiency.values()):,.0f} same total, declining channels reduced\n")

    if close_after:
        out_stream.close()
        print(f"Annual plan written to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
