#!/usr/bin/env python3
"""
Cross-attribution conversion comparator.

Joins conversion counts from ad platforms with GA4-measured conversions
and surfaces the divergence per channel. Shows how rank changes between
the two attribution views.

Expected inputs: two CSVs.

Ad-platform CSV columns:
    - channel (or platform)
    - conversions (platform-reported)
    - spend (optional, for ROAS-divergence view)

GA4 CSV columns:
    - channel (must match ad-platform channel name)
    - conversions (GA4-measured)

Usage:
    python attribution_comparator.py \
        --ad-platform ads.csv \
        --ga4 ga4.csv \
        --output comparison.csv

The script:
    - Aligns channels across the two files
    - Computes divergence as (platform - ga4) / ga4 × 100
    - Flags channels where divergence exceeds ±25%
    - Computes rank in each attribution view, reports rank change
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ad-platform", required=True, help="Ad-platform conversions CSV")
    p.add_argument("--ga4", required=True, help="GA4 conversions CSV")
    p.add_argument("--channel-col", default="channel", help="Channel column name")
    p.add_argument("--divergence-threshold", type=float, default=25.0, help="Flag |divergence| > N%% (default: 25)")
    p.add_argument("--output", default="-", help="Output CSV (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def aggregate(path, channel_col, conv_field="conversions"):
    out = defaultdict(lambda: {"conversions": 0.0, "spend": 0.0})
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ch = r.get(channel_col) or r.get("platform") or r.get("default_channel_grouping") or "(unknown)"
            out[ch]["conversions"] += to_float(r.get(conv_field))
            out[ch]["spend"] += to_float(r.get("spend") or r.get("cost"))
    return out


def main():
    args = parse_args()
    ads = aggregate(args.ad_platform, args.channel_col)
    ga4 = aggregate(args.ga4, args.channel_col)

    all_channels = sorted(set(ads.keys()) | set(ga4.keys()))
    if not all_channels:
        print("No channels found.", file=sys.stderr)
        return 1

    # Compute conversion volumes per view
    rows = []
    for ch in all_channels:
        plat_conv = ads[ch]["conversions"] if ch in ads else 0
        ga4_conv = ga4[ch]["conversions"] if ch in ga4 else 0
        spend = ads[ch]["spend"] if ch in ads else 0

        if ga4_conv > 0:
            divergence_pct = (plat_conv - ga4_conv) / ga4_conv * 100
        elif plat_conv > 0:
            divergence_pct = float("inf")
        else:
            divergence_pct = 0

        plat_cpa = spend / plat_conv if plat_conv > 0 else None
        ga4_cpa = spend / ga4_conv if ga4_conv > 0 else None

        rows.append({
            "channel": ch,
            "platform_conversions": int(plat_conv),
            "ga4_conversions": int(ga4_conv),
            "divergence_pct": round(divergence_pct, 1) if divergence_pct != float("inf") else "n/a (ga4=0)",
            "platform_cpa": round(plat_cpa, 2) if plat_cpa is not None else "n/a",
            "ga4_cpa": round(ga4_cpa, 2) if ga4_cpa is not None else "n/a",
            "spend": round(spend, 2),
            "flag": "",
        })

    # Compute ranks in each view (descending conv count)
    plat_ranked = sorted(rows, key=lambda r: -r["platform_conversions"])
    for i, r in enumerate(plat_ranked, 1):
        r["platform_rank"] = i

    ga4_ranked = sorted(rows, key=lambda r: -r["ga4_conversions"])
    for i, r in enumerate(ga4_ranked, 1):
        r["ga4_rank"] = i

    for r in rows:
        r["rank_change"] = r["platform_rank"] - r["ga4_rank"]  # positive = better-ranked in platform view
        if isinstance(r["divergence_pct"], (int, float)) and abs(r["divergence_pct"]) >= args.divergence_threshold:
            r["flag"] = "diverges"

    # Sort by spend descending
    rows.sort(key=lambda r: -r["spend"])

    fields = ["channel", "flag", "platform_conversions", "ga4_conversions", "divergence_pct",
              "platform_rank", "ga4_rank", "rank_change",
              "platform_cpa", "ga4_cpa", "spend"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        n_flagged = sum(1 for r in rows if r["flag"])
        print(f"Wrote {len(rows)} channels to {args.output}. {n_flagged} flagged for divergence > {args.divergence_threshold}%.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
