#!/usr/bin/env python3
"""
Content attribution: scores content by influence on conversion paths.

Expected CSV columns:
    - content_url (or content_title)
    - sessions
    - engaged_sessions (or engagement_rate)
    - avg_engagement_time_seconds (optional)
    - first_touch_conversions
    - middle_touch_conversions
    - last_touch_conversions

Usage:
    python content_attribution.py content.csv --output attribution.csv

Composes an influence score from path presence (first/middle/last touch)
and engagement signals.
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Content attribution CSV")
    p.add_argument("--output", default="-")
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
        print("No data.", file=sys.stderr)
        return 1

    out_rows = []
    for r in rows:
        url = r.get("content_url") or r.get("content_title") or "(unknown)"
        sessions = to_float(r.get("sessions"))
        engaged = to_float(r.get("engaged_sessions"))
        ft = to_float(r.get("first_touch_conversions"))
        mt = to_float(r.get("middle_touch_conversions"))
        lt = to_float(r.get("last_touch_conversions"))
        engage_time = to_float(r.get("avg_engagement_time_seconds"))

        total_conv_touches = ft + mt + lt
        # Influence score: weighted touchpoints + engagement
        influence = (ft * 1.0) + (mt * 0.5) + (lt * 1.5)
        # Add engagement bonus
        engagement_rate = engaged / sessions if sessions > 0 else 0
        engagement_bonus = engagement_rate * 20  # up to 20 points
        influence_score = round(influence + engagement_bonus, 1)

        # Path role classification
        if total_conv_touches == 0:
            role = "no_path_presence"
        else:
            ft_share = ft / total_conv_touches
            lt_share = lt / total_conv_touches
            if lt_share > 0.5:
                role = "closer"
            elif ft_share > 0.5:
                role = "discovery"
            else:
                role = "middle_of_funnel"

        out_rows.append({
            "content": url,
            "role": role,
            "influence_score": influence_score,
            "sessions": int(sessions),
            "engagement_rate_pct": round(engagement_rate * 100, 1),
            "first_touch_conv": int(ft),
            "middle_touch_conv": int(mt),
            "last_touch_conv": int(lt),
            "total_path_touches": int(total_conv_touches),
            "avg_engagement_sec": int(engage_time),
        })

    out_rows.sort(key=lambda r: -r["influence_score"])

    fields = ["content", "role", "influence_score", "sessions", "engagement_rate_pct",
              "first_touch_conv", "middle_touch_conv", "last_touch_conv", "total_path_touches", "avg_engagement_sec"]
    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} content pieces to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
