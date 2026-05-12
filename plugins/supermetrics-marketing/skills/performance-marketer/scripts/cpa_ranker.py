#!/usr/bin/env python3
"""
Ad-level performance ranker.

Ranks ads by an efficiency metric (default: CPA) with optional grouping
by ad format, placement, audience, or campaign. Used in creative testing
workflows to identify winners and compare formats (e.g. video vs static).

Expected CSV columns:
    - ad_name (or ad_id)
    - spend, clicks, impressions, conversions (minimum)
    - Optionally: ad_format, placement, audience, campaign_name

Usage:
    # Top 3 by CPA
    python cpa_ranker.py input.csv --top 3 --metric cpa --output winners.csv

    # Group by ad format (video vs static comparison)
    python cpa_ranker.py input.csv --metric cpa --group-by ad_format

    # Rank by ROAS instead
    python cpa_ranker.py input.csv --metric roas --top 5

Supported metrics: cpa, roas, ctr, cpc, conversion_rate

Minimum-spend filtering: by default, ads with less than $50 spend are
excluded to avoid ranking statistical noise. Override with --min-spend.
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--ad-col", default="ad_name", help="Ad identifier column (default: ad_name)")
    p.add_argument("--metric", default="cpa", choices=["cpa", "roas", "ctr", "cpc", "conversion_rate"],
                   help="Metric to rank by (default: cpa)")
    p.add_argument("--top", type=int, default=10, help="Number of top performers to return (default: 10)")
    p.add_argument("--group-by", default=None, help="Optional grouping column (e.g. ad_format)")
    p.add_argument("--min-spend", type=float, default=50.0, help="Exclude ads with spend below this (default: 50)")
    p.add_argument("--output", default="-", help="Output CSV path (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def compute_metric(metric, agg):
    spend = agg["spend"]
    clicks = agg["clicks"]
    impr = agg["impressions"]
    conv = agg["conversions"]
    revenue = agg.get("revenue", 0)

    if metric == "cpa":
        return (spend / conv) if conv > 0 else float("inf")
    if metric == "roas":
        return (revenue / spend) if spend > 0 else 0
    if metric == "ctr":
        return (clicks / impr * 100) if impr > 0 else 0
    if metric == "cpc":
        return (spend / clicks) if clicks > 0 else float("inf")
    if metric == "conversion_rate":
        return (conv / clicks * 100) if clicks > 0 else 0
    return 0


def aggregate(rows, group_col):
    """Aggregate rows by group_col, returning a dict of {group: aggregated_metrics}."""
    groups = defaultdict(lambda: {"spend": 0.0, "clicks": 0.0, "impressions": 0.0, "conversions": 0.0, "revenue": 0.0})
    for r in rows:
        g = r.get(group_col, "(unknown)")
        groups[g]["spend"] += to_float(r.get("spend") or r.get("cost"))
        groups[g]["clicks"] += to_float(r.get("clicks"))
        groups[g]["impressions"] += to_float(r.get("impressions"))
        groups[g]["conversions"] += to_float(r.get("conversions"))
        groups[g]["revenue"] += to_float(r.get("revenue") or r.get("conversion_value"))
    return groups


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    # Always aggregate at ad level first
    by_ad = aggregate(rows, args.ad_col)

    # Apply min-spend filter
    by_ad = {ad: agg for ad, agg in by_ad.items() if agg["spend"] >= args.min_spend}

    if not by_ad:
        print(f"No ads meet --min-spend {args.min_spend}. Try lowering it.", file=sys.stderr)
        return 1

    # If grouping, also aggregate at group level
    group_summary = None
    if args.group_by:
        group_summary = aggregate(rows, args.group_by)

    # Rank ads
    # For "lower is better" metrics (cpa, cpc), sort ascending; otherwise descending
    lower_better = args.metric in ("cpa", "cpc")
    ranked = [(ad, agg, compute_metric(args.metric, agg)) for ad, agg in by_ad.items()]
    ranked.sort(key=lambda x: x[2] if lower_better else -x[2])
    top = ranked[: args.top]

    # Build top-N output
    out_rows = []
    for rank, (ad, agg, val) in enumerate(top, 1):
        out_rows.append({
            "rank": rank,
            "ad": ad,
            args.metric: round(val, 4) if val != float("inf") else "n/a",
            "spend": round(agg["spend"], 2),
            "clicks": int(agg["clicks"]),
            "impressions": int(agg["impressions"]),
            "conversions": int(agg["conversions"]),
        })

    # Write top-N
    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    fields = ["rank", "ad", args.metric, "spend", "clicks", "impressions", "conversions"]
    writer = csv.DictWriter(out_stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out_rows)

    # If grouped, append the group comparison
    if group_summary:
        out_stream.write("\n")
        out_stream.write(f"--- {args.metric.upper()} by {args.group_by} ---\n")
        group_rows = []
        for g, agg in group_summary.items():
            if agg["spend"] < args.min_spend:
                continue
            group_rows.append({
                args.group_by: g,
                args.metric: round(compute_metric(args.metric, agg), 4),
                "spend": round(agg["spend"], 2),
                "conversions": int(agg["conversions"]),
            })
        group_rows.sort(key=lambda r: r[args.metric] if lower_better else -r[args.metric])
        group_fields = [args.group_by, args.metric, "spend", "conversions"]
        gw = csv.DictWriter(out_stream, fieldnames=group_fields)
        gw.writeheader()
        gw.writerows(group_rows)

    if close_after:
        out_stream.close()
        print(f"Wrote rankings to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
