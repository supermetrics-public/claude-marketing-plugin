#!/usr/bin/env python3
"""
Week-over-week comparison helper.

Takes a CSV with two time periods of marketing data and computes deltas
(absolute and percentage) for any numeric metric. Flags rows where the
change exceeds a configurable threshold.

Expected CSV columns (flexible — the script auto-detects):
    - A grouping column (e.g. campaign_name, ad_name, channel)
    - A period column with two values (e.g. "this_week" / "last_week", or
      explicit date ranges)
    - One or more numeric metric columns (spend, clicks, ctr, cpc, cpa, etc.)

Usage:
    python wow_comparison.py input.csv \
        --group-col campaign_name \
        --period-col period \
        --metrics spend clicks ctr cpc cpa \
        --threshold 10 \
        --output comparison.csv

The threshold is a percentage. Rows where ANY metric moved more than
threshold% get a "flagged" marker so the user can scan to what changed.
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--group-col", required=True, help="Column to group by (e.g. campaign_name)")
    p.add_argument("--period-col", required=True, help="Column identifying the two periods")
    p.add_argument("--current-label", default=None, help="Value in period-col for the current period (default: auto-detect last value)")
    p.add_argument("--previous-label", default=None, help="Value in period-col for the previous period (default: auto-detect first value)")
    p.add_argument("--metrics", nargs="+", required=True, help="Numeric metric columns to compare")
    p.add_argument("--threshold", type=float, default=10.0, help="Flag changes exceeding this percent (default: 10)")
    p.add_argument("--output", default="-", help="Output CSV path (default: stdout)")
    return p.parse_args()


def load_data(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def pct_change(current, previous):
    if previous == 0:
        return float("inf") if current != 0 else 0.0
    return (current - previous) / previous * 100


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        # Strip common formatting
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def main():
    args = parse_args()
    rows, fieldnames = load_data(args.input)

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    # Auto-detect period labels if not provided
    periods = list(dict.fromkeys(r[args.period_col] for r in rows))
    if len(periods) < 2:
        print(f"Expected 2 periods in column '{args.period_col}', found {len(periods)}: {periods}", file=sys.stderr)
        return 1

    previous_label = args.previous_label or periods[0]
    current_label = args.current_label or periods[-1]

    # Index by group
    grouped = defaultdict(dict)
    for r in rows:
        group = r[args.group_col]
        period = r[args.period_col]
        grouped[group][period] = r

    # Build output
    out_rows = []
    for group, periods_data in grouped.items():
        if current_label not in periods_data or previous_label not in periods_data:
            continue
        curr = periods_data[current_label]
        prev = periods_data[previous_label]

        out = {args.group_col: group}
        flagged = False
        for metric in args.metrics:
            c = to_float(curr.get(metric))
            p = to_float(prev.get(metric))
            delta = c - p
            pct = pct_change(c, p)
            out[f"{metric}_previous"] = round(p, 4)
            out[f"{metric}_current"] = round(c, 4)
            out[f"{metric}_delta"] = round(delta, 4)
            out[f"{metric}_pct"] = round(pct, 2) if pct != float("inf") else "new"
            if pct != float("inf") and abs(pct) >= args.threshold:
                flagged = True
        out["flagged"] = "yes" if flagged else ""
        out_rows.append(out)

    if not out_rows:
        print("No groups appear in both periods.", file=sys.stderr)
        return 1

    # Sort flagged first, then by largest absolute change in the first metric
    first_metric = args.metrics[0]
    out_rows.sort(key=lambda r: (r["flagged"] != "yes", -abs(to_float(r.get(f"{first_metric}_pct")) if r.get(f"{first_metric}_pct") != "new" else 999)))

    out_fields = list(out_rows[0].keys())
    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} rows to {args.output}", file=sys.stderr)
        flagged_count = sum(1 for r in out_rows if r["flagged"] == "yes")
        print(f"{flagged_count} rows flagged (change >{args.threshold}% in at least one metric)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
