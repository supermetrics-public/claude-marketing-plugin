#!/usr/bin/env python3
"""
Blended ROAS and day-of-week analyzer.

Computes blended ROAS across platforms with daily and day-of-week
breakdowns. Identifies the top and bottom days of the week and outputs
a budget-weighting recommendation.

Expected CSV columns:
    - platform (or channel)
    - date (daily)
    - spend
    - revenue (or conversion_value or purchase_value)
    - purchases (or conversions) — optional

Usage:
    python blended_roas.py input.csv --output report.txt

The output includes:
    - Headline: blended ROAS for the period, with the double-count caveat
    - Daily trend (week-by-week if data spans multiple weeks)
    - Day-of-week ranking with conversion rate and ROAS per DoW
    - Budget weighting recommendation (top 2 DoWs +X%, bottom 2 DoWs -Y%)
"""

import argparse
import sys
import csv
from collections import defaultdict
from datetime import datetime


DOW_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Daily platform-level CSV")
    p.add_argument("--platform-col", default="platform", help="Platform column (default: platform)")
    p.add_argument("--date-col", default="date", help="Date column (default: date)")
    p.add_argument("--output", default="-", help="Output path (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {s}")


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    platform_col = args.platform_col
    if platform_col not in rows[0]:
        for c in ("platform", "channel", "data_source", "source"):
            if c in rows[0]:
                platform_col = c
                break

    # Parse rows
    parsed = []
    platforms = set()
    for r in rows:
        try:
            d = parse_date(r[args.date_col])
        except (ValueError, KeyError):
            continue
        platform = r.get(platform_col, "(unknown)")
        platforms.add(platform)
        parsed.append({
            "platform": platform,
            "date": d,
            "spend": to_float(r.get("spend") or r.get("cost")),
            "revenue": to_float(r.get("revenue") or r.get("conversion_value") or r.get("purchase_value")),
            "purchases": to_float(r.get("purchases") or r.get("conversions")),
            "clicks": to_float(r.get("clicks")),
        })

    if not parsed:
        print("No valid dated rows.", file=sys.stderr)
        return 1

    # Headline totals
    total_spend = sum(r["spend"] for r in parsed)
    total_revenue = sum(r["revenue"] for r in parsed)
    total_purchases = sum(r["purchases"] for r in parsed)
    blended_roas = total_revenue / total_spend if total_spend > 0 else 0
    blended_cpa = total_spend / total_purchases if total_purchases > 0 else 0

    # Per-platform
    by_platform = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "purchases": 0.0})
    for r in parsed:
        by_platform[r["platform"]]["spend"] += r["spend"]
        by_platform[r["platform"]]["revenue"] += r["revenue"]
        by_platform[r["platform"]]["purchases"] += r["purchases"]

    # Daily totals (collapsed across platforms)
    by_date = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "purchases": 0.0, "clicks": 0.0})
    for r in parsed:
        by_date[r["date"]]["spend"] += r["spend"]
        by_date[r["date"]]["revenue"] += r["revenue"]
        by_date[r["date"]]["purchases"] += r["purchases"]
        by_date[r["date"]]["clicks"] += r["clicks"]

    # Day-of-week aggregation
    by_dow = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "purchases": 0.0, "clicks": 0.0, "days": 0})
    for d, totals in by_date.items():
        dow = d.weekday()  # 0 = Monday
        by_dow[dow]["spend"] += totals["spend"]
        by_dow[dow]["revenue"] += totals["revenue"]
        by_dow[dow]["purchases"] += totals["purchases"]
        by_dow[dow]["clicks"] += totals["clicks"]
        by_dow[dow]["days"] += 1

    # Format the output
    lines = []
    period_start = min(r["date"] for r in parsed)
    period_end = max(r["date"] for r in parsed)
    n_days = (period_end - period_start).days + 1

    lines.append(f"--- Blended ROAS report ({period_start} to {period_end}, {n_days} days) ---\n")
    lines.append(f"Total spend:    ${total_spend:,.2f}")
    lines.append(f"Total revenue:  ${total_revenue:,.2f}")
    lines.append(f"Total purchases: {int(total_purchases):,}")
    lines.append(f"Blended ROAS:   {blended_roas:.2f}x")
    lines.append(f"Blended CPA:    ${blended_cpa:,.2f}\n")
    lines.append("Caveat: 'blended ROAS' sums platform-reported revenue divided by total spend. Both Facebook and Google may credit themselves for the same purchase, so this number is directionally useful but likely overstates true blended ROAS by 5-15%.\n")

    # Per-platform
    lines.append("--- By platform ---")
    for p in sorted(platforms):
        d = by_platform[p]
        roas = d["revenue"] / d["spend"] if d["spend"] > 0 else 0
        cpa = d["spend"] / d["purchases"] if d["purchases"] > 0 else 0
        lines.append(f"{p}: spend ${d['spend']:,.0f}, revenue ${d['revenue']:,.0f}, ROAS {roas:.2f}x, CPA ${cpa:.2f}")
    lines.append("")

    # DoW table
    lines.append("--- By day of week ---")
    lines.append(f"{'Day':<11} {'Spend':>10} {'Revenue':>11} {'ROAS':>7} {'CPA':>8} {'CVR':>7} {'N days':>7}")
    dow_summary = []
    for dow in range(7):
        d = by_dow[dow]
        if d["days"] == 0:
            continue
        roas = d["revenue"] / d["spend"] if d["spend"] > 0 else 0
        cpa = d["spend"] / d["purchases"] if d["purchases"] > 0 else 0
        cvr = (d["purchases"] / d["clicks"] * 100) if d["clicks"] > 0 else 0
        dow_summary.append((dow, roas, cvr, d))
        lines.append(f"{DOW_NAMES[dow]:<11} ${d['spend']:>9,.0f} ${d['revenue']:>10,.0f} {roas:>6.2f}x ${cpa:>6.2f} {cvr:>6.2f}% {d['days']:>7}")
    lines.append("")

    # Ranking and recommendation
    if dow_summary:
        ranked = sorted(dow_summary, key=lambda x: -x[1])  # by ROAS descending
        top = ranked[:2]
        bottom = ranked[-2:]
        lines.append("--- Day-of-week ranking ---")
        lines.append(f"Best ROAS days:   {', '.join(DOW_NAMES[d[0]] + f' ({d[1]:.2f}x)' for d in top)}")
        lines.append(f"Worst ROAS days:  {', '.join(DOW_NAMES[d[0]] + f' ({d[1]:.2f}x)' for d in bottom)}\n")
        lines.append("--- Budget weighting recommendation ---")
        lines.append(f"Increase budget on {DOW_NAMES[top[0][0]]} and {DOW_NAMES[top[1][0]]} by ~20%.")
        lines.append(f"Decrease budget on {DOW_NAMES[bottom[0][0]]} and {DOW_NAMES[bottom[1][0]]} by ~15%.")
        lines.append("Hold the middle three days flat. Re-evaluate after 4 weeks of the new schedule.\n")
        lines.append("Important: this pattern reflects non-promo weeks. During BFCM, holiday sales, or other promotional periods, normal day-of-week patterns are scrambled by intent spikes and competitor bidding. Pause this strategy during promos and use a flat or promo-specific weighting instead.")

    output_text = "\n".join(lines) + "\n"

    if args.output == "-":
        sys.stdout.write(output_text)
    else:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Wrote report to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
