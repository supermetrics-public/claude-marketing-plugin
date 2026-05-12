#!/usr/bin/env python3
"""
Ad fatigue detector.

Identifies ads showing classic fatigue signals: high frequency combined with
declining CTR over a recent window. The output is a ranked refresh list,
prioritized by spend impact so the user fixes the biggest bleeders first.

Expected CSV columns (auto-detected with flexibility):
    - ad_name (or ad_id, or both)
    - date (daily breakdown — we'll split into "recent" and "prior" windows)
    - impressions, clicks, spend, frequency (at minimum)

Usage:
    python ad_fatigue_detector.py input.csv \
        --freq-threshold 3.5 \
        --ctr-decline-pct 20 \
        --recent-days 7 \
        --prior-days 7 \
        --output fatigued_ads.csv

What "fatigue" means here:
    - Frequency in the recent window > freq-threshold (default 3.5), AND
    - CTR in the recent window has dropped by at least ctr-decline-pct%
      compared to the prior window.

Output is sorted by recent-window spend (descending) so the highest-spend
fatigued ads surface first.
"""

import argparse
import sys
import csv
from collections import defaultdict
from datetime import datetime, timedelta


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Input CSV file with daily ad-level data")
    p.add_argument("--ad-col", default="ad_name", help="Column identifying the ad (default: ad_name)")
    p.add_argument("--date-col", default="date", help="Column with the date (default: date)")
    p.add_argument("--freq-threshold", type=float, default=3.5, help="Frequency threshold (default: 3.5)")
    p.add_argument("--ctr-decline-pct", type=float, default=20.0, help="Minimum CTR decline percent to flag (default: 20)")
    p.add_argument("--recent-days", type=int, default=7, help="Days in the recent window (default: 7)")
    p.add_argument("--prior-days", type=int, default=7, help="Days in the prior window (default: 7)")
    p.add_argument("--output", default="-", help="Output CSV path (default: stdout)")
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

    # Determine date range and split
    dates = sorted({parse_date(r[args.date_col]) for r in rows})
    if not dates:
        print("No valid dates found.", file=sys.stderr)
        return 1

    most_recent = dates[-1]
    recent_start = most_recent - timedelta(days=args.recent_days - 1)
    prior_end = recent_start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=args.prior_days - 1)

    print(f"Recent window: {recent_start} to {most_recent}", file=sys.stderr)
    print(f"Prior window:  {prior_start} to {prior_end}", file=sys.stderr)

    # Aggregate per ad per window
    ads = defaultdict(lambda: {
        "recent": {"impr": 0.0, "clicks": 0.0, "spend": 0.0, "freq_sum": 0.0, "freq_n": 0},
        "prior":  {"impr": 0.0, "clicks": 0.0, "spend": 0.0, "freq_sum": 0.0, "freq_n": 0},
    })

    for r in rows:
        try:
            d = parse_date(r[args.date_col])
        except (ValueError, KeyError):
            continue
        ad = r.get(args.ad_col, "(unknown)")
        impr = to_float(r.get("impressions"))
        clicks = to_float(r.get("clicks"))
        spend = to_float(r.get("spend") or r.get("cost"))
        freq = to_float(r.get("frequency"))

        if recent_start <= d <= most_recent:
            bucket = ads[ad]["recent"]
        elif prior_start <= d <= prior_end:
            bucket = ads[ad]["prior"]
        else:
            continue

        bucket["impr"] += impr
        bucket["clicks"] += clicks
        bucket["spend"] += spend
        if freq > 0:
            bucket["freq_sum"] += freq
            bucket["freq_n"] += 1

    # Compute fatigue flags
    flagged = []
    for ad, windows in ads.items():
        recent = windows["recent"]
        prior = windows["prior"]

        recent_ctr = (recent["clicks"] / recent["impr"] * 100) if recent["impr"] > 0 else 0
        prior_ctr  = (prior["clicks"] / prior["impr"] * 100) if prior["impr"] > 0 else 0
        recent_freq = (recent["freq_sum"] / recent["freq_n"]) if recent["freq_n"] > 0 else 0

        if prior_ctr == 0:
            ctr_decline = 0
        else:
            ctr_decline = (prior_ctr - recent_ctr) / prior_ctr * 100

        is_fatigued = (
            recent_freq > args.freq_threshold and
            ctr_decline >= args.ctr_decline_pct
        )

        if is_fatigued:
            flagged.append({
                "ad_name": ad,
                "recent_frequency": round(recent_freq, 2),
                "recent_ctr_pct": round(recent_ctr, 3),
                "prior_ctr_pct": round(prior_ctr, 3),
                "ctr_decline_pct": round(ctr_decline, 1),
                "recent_spend": round(recent["spend"], 2),
                "recent_impressions": int(recent["impr"]),
                "severity": "high" if ctr_decline >= 35 else "medium",
            })

    if not flagged:
        print("No fatigued ads detected with current thresholds.", file=sys.stderr)
        print(f"Try lowering --freq-threshold (current: {args.freq_threshold}) or --ctr-decline-pct (current: {args.ctr_decline_pct}).", file=sys.stderr)
        return 0

    # Rank by recent spend descending — fix the biggest bleeders first
    flagged.sort(key=lambda x: -x["recent_spend"])

    fields = ["ad_name", "severity", "recent_frequency", "recent_ctr_pct", "prior_ctr_pct",
              "ctr_decline_pct", "recent_spend", "recent_impressions"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(flagged)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(flagged)
        print(f"Wrote {len(flagged)} fatigued ads to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
