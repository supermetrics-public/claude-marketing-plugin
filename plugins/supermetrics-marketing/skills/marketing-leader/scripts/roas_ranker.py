#!/usr/bin/env python3
"""
Cross-channel ROAS / CPA ranker with budget-shift recommendation.

Ranks channels by ROAS (or CPA) over a window and produces a budget-shift
recommendation: take X% from the worst performer and move it to the best.

Expected CSV columns:
    - channel (or platform)
    - spend
    - revenue (or conversion_value) — required for ROAS
    - conversions — required for CPA

Usage:
    python roas_ranker.py input.csv --metric roas --shift-pct 20

    python roas_ranker.py input.csv --metric cpa --shift-pct 15 --output ranking.csv

What it outputs:
    - A ranking table (best to worst on the metric)
    - The spread between best and worst
    - A reallocation recommendation: dollars to shift, source channel, destination channel
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Channel-level CSV")
    p.add_argument("--channel-col", default="channel", help="Channel column (default: channel)")
    p.add_argument("--metric", default="roas", choices=["roas", "cpa"], help="Ranking metric (default: roas)")
    p.add_argument("--shift-pct", type=float, default=20.0, help="Reallocation percent (default: 20)")
    p.add_argument("--output", default="-", help="Output CSV path (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    # Aggregate per channel (handles daily-granularity inputs)
    channels = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "conversions": 0.0})
    for r in rows:
        ch = r.get(args.channel_col, "(unknown)")
        channels[ch]["spend"] += to_float(r.get("spend") or r.get("cost"))
        channels[ch]["revenue"] += to_float(r.get("revenue") or r.get("conversion_value"))
        channels[ch]["conversions"] += to_float(r.get("conversions"))

    # Compute metric
    def metric_value(ch_data):
        if args.metric == "roas":
            return (ch_data["revenue"] / ch_data["spend"]) if ch_data["spend"] > 0 else 0
        else:  # cpa
            return (ch_data["spend"] / ch_data["conversions"]) if ch_data["conversions"] > 0 else float("inf")

    ranked = []
    for ch, data in channels.items():
        if data["spend"] <= 0:
            continue
        m = metric_value(data)
        ranked.append({
            "channel": ch,
            "spend": round(data["spend"], 2),
            "revenue": round(data["revenue"], 2),
            "conversions": int(data["conversions"]),
            args.metric: round(m, 3) if m != float("inf") else "n/a",
        })

    if len(ranked) < 2:
        print("Need at least 2 channels for ranking and reallocation.", file=sys.stderr)
        return 1

    lower_better = args.metric == "cpa"
    # Sort best to worst
    ranked.sort(key=lambda r: r[args.metric] if (not lower_better and r[args.metric] != "n/a") else (r[args.metric] if lower_better and r[args.metric] != "n/a" else float("inf")), reverse=not lower_better)

    # Add rank
    for i, r in enumerate(ranked, 1):
        r["rank"] = i

    best = ranked[0]
    worst = ranked[-1]

    # Compute spread
    if best[args.metric] != "n/a" and worst[args.metric] != "n/a":
        if args.metric == "roas":
            spread_x = best[args.metric] / worst[args.metric] if worst[args.metric] > 0 else None
            spread_label = f"{spread_x:.2f}x better" if spread_x else "n/a"
        else:
            spread_x = worst[args.metric] / best[args.metric] if best[args.metric] > 0 else None
            spread_label = f"{spread_x:.2f}x more expensive" if spread_x else "n/a"
    else:
        spread_label = "n/a"

    # Recommendation
    shift_amount = worst["spend"] * (args.shift_pct / 100)

    # Output
    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    fields = ["rank", "channel", args.metric, "spend", "revenue", "conversions"]
    writer = csv.DictWriter(out_stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(ranked)

    # Append summary
    out_stream.write("\n--- Summary ---\n")
    out_stream.write(f"Best performer:  {best['channel']} ({args.metric.upper()} = {best[args.metric]})\n")
    out_stream.write(f"Worst performer: {worst['channel']} ({args.metric.upper()} = {worst[args.metric]})\n")
    out_stream.write(f"Spread: {spread_label}\n\n")
    out_stream.write(f"--- Recommendation ({args.shift_pct}% shift) ---\n")
    out_stream.write(f"Move ${shift_amount:,.2f} from {worst['channel']} to {best['channel']} next period.\n")
    out_stream.write(f"Caveat: assumes {best['channel']} has remaining capacity at current efficiency. ")
    out_stream.write(f"Marginal ROAS at higher spend may compress — recommend reviewing after 2 weeks.\n")

    if close_after:
        out_stream.close()
        print(f"Wrote ranking to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
