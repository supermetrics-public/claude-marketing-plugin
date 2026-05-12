#!/usr/bin/env python3
"""
Ad-platform vs GA4 funnel reconciler.

Joins ad platform data with GA4 data on channel name and surfaces the
divergence between what the ad platform reported and what GA4 measured.
The "leaky funnel" lives in the divergence.

Usage:
    python funnel_reconciler.py \
        --ad-platform ads.csv \
        --ga4 ga4.csv \
        --channel-col channel \
        --output reconciliation.csv

Expected ad-platform CSV columns:
    - channel (or source / platform — must match the GA4 channel name)
    - spend
    - clicks
    - platform_conversions (what the ad platform claims to have driven)

Expected GA4 CSV columns:
    - channel (or default_channel_grouping)
    - sessions
    - conversions (GA4-measured)

Output: a table per channel with both views side-by-side, plus:
    - click-to-session gap (UTM/tracking health indicator)
    - platform-CPA vs GA4-CPA
    - divergence % (how badly the two systems disagree)
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ad-platform", required=True, help="Ad platform CSV (spend, clicks, conversions per channel)")
    p.add_argument("--ga4", required=True, help="GA4 CSV (sessions, conversions per channel)")
    p.add_argument("--channel-col", default="channel", help="Channel column name (default: channel)")
    p.add_argument("--output", default="-", help="Output CSV path (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def aggregate_ad_platform(path, channel_col):
    out = defaultdict(lambda: {"spend": 0.0, "clicks": 0.0, "conversions": 0.0})
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ch = r.get(channel_col, "(unknown)")
            out[ch]["spend"] += to_float(r.get("spend") or r.get("cost"))
            out[ch]["clicks"] += to_float(r.get("clicks"))
            out[ch]["conversions"] += to_float(r.get("platform_conversions") or r.get("conversions"))
    return out


def aggregate_ga4(path, channel_col):
    out = defaultdict(lambda: {"sessions": 0.0, "conversions": 0.0})
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ch = r.get(channel_col) or r.get("default_channel_grouping") or r.get("source") or "(unknown)"
            out[ch]["sessions"] += to_float(r.get("sessions"))
            out[ch]["conversions"] += to_float(r.get("conversions"))
    return out


def main():
    args = parse_args()
    ads = aggregate_ad_platform(args.ad_platform, args.channel_col)
    ga4 = aggregate_ga4(args.ga4, args.channel_col)

    all_channels = sorted(set(ads.keys()) | set(ga4.keys()))
    if not all_channels:
        print("No channels found in either file.", file=sys.stderr)
        return 1

    out_rows = []
    for ch in all_channels:
        a = ads.get(ch, {"spend": 0.0, "clicks": 0.0, "conversions": 0.0})
        g = ga4.get(ch, {"sessions": 0.0, "conversions": 0.0})

        # Click-to-session gap (UTM/tracking health)
        if a["clicks"] > 0:
            click_session_ratio = g["sessions"] / a["clicks"]
            click_gap_pct = (a["clicks"] - g["sessions"]) / a["clicks"] * 100
        else:
            click_session_ratio = None
            click_gap_pct = None

        # CPAs
        platform_cpa = a["spend"] / a["conversions"] if a["conversions"] > 0 else None
        ga4_cpa = a["spend"] / g["conversions"] if g["conversions"] > 0 else None

        # Conversion divergence
        if a["conversions"] > 0 and g["conversions"] > 0:
            divergence_pct = (a["conversions"] - g["conversions"]) / a["conversions"] * 100
        else:
            divergence_pct = None

        # GA4-measured conversion rate (clicks → conversions per GA4)
        ga4_cvr = (g["conversions"] / g["sessions"] * 100) if g["sessions"] > 0 else None

        # Tracking health flag
        tracking_flag = ""
        if click_gap_pct is not None and abs(click_gap_pct) > 25:
            tracking_flag = "check UTMs"

        out_rows.append({
            "channel": ch,
            "spend": round(a["spend"], 2),
            "ad_clicks": int(a["clicks"]),
            "ga4_sessions": int(g["sessions"]),
            "click_session_gap_pct": round(click_gap_pct, 1) if click_gap_pct is not None else "n/a",
            "platform_conversions": int(a["conversions"]),
            "ga4_conversions": int(g["conversions"]),
            "conversion_divergence_pct": round(divergence_pct, 1) if divergence_pct is not None else "n/a",
            "platform_cpa": round(platform_cpa, 2) if platform_cpa is not None else "n/a",
            "ga4_cpa": round(ga4_cpa, 2) if ga4_cpa is not None else "n/a",
            "ga4_cvr_pct": round(ga4_cvr, 2) if ga4_cvr is not None else "n/a",
            "tracking_flag": tracking_flag,
        })

    # Sort by spend descending — biggest channels first
    out_rows.sort(key=lambda r: -r["spend"])

    fields = ["channel", "spend", "ad_clicks", "ga4_sessions", "click_session_gap_pct",
              "platform_conversions", "ga4_conversions", "conversion_divergence_pct",
              "platform_cpa", "ga4_cpa", "ga4_cvr_pct", "tracking_flag"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        flagged = sum(1 for r in out_rows if r["tracking_flag"])
        print(f"Wrote {len(out_rows)} channels to {args.output} ({flagged} flagged for tracking issues).", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
