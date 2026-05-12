#!/usr/bin/env python3
"""
Webinar funnel analyzer, cohorted by registration source.

Expected CSV columns:
    - source (registration source: LinkedIn Ads, Email, Organic, Partner, etc.)
    - spend (promotion cost attributable to this source)
    - registrations
    - attended_live
    - attended_on_demand
    - high_engagement (Q&A participation, poll responses, etc.)
    - mqls_within_30d

Usage:
    python webinar_funnel.py webinar.csv --output funnel.csv

Outputs per source:
    - All conversion rates between funnel stages
    - Total cost per MQL via this webinar
    - Engagement quality flag
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Webinar funnel CSV")
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
    totals = {"spend": 0, "regs": 0, "live": 0, "od": 0, "engaged": 0, "mqls": 0}

    for r in rows:
        source = r.get("source", "(unknown)")
        spend = to_float(r.get("spend"))
        regs = to_float(r.get("registrations"))
        live = to_float(r.get("attended_live"))
        od = to_float(r.get("attended_on_demand"))
        engaged = to_float(r.get("high_engagement"))
        mqls = to_float(r.get("mqls_within_30d"))

        total_attended = live + od
        live_rate = live / regs * 100 if regs > 0 else None
        total_attend_rate = total_attended / regs * 100 if regs > 0 else None
        engagement_rate = engaged / total_attended * 100 if total_attended > 0 else None
        mql_rate = mqls / total_attended * 100 if total_attended > 0 else None
        cpmql = spend / mqls if mqls > 0 else None
        cost_per_reg = spend / regs if regs > 0 else None

        totals["spend"] += spend
        totals["regs"] += regs
        totals["live"] += live
        totals["od"] += od
        totals["engaged"] += engaged
        totals["mqls"] += mqls

        # Engagement quality flag
        if engagement_rate is None:
            quality = "n/a"
        elif engagement_rate >= 30:
            quality = "high"
        elif engagement_rate >= 15:
            quality = "moderate"
        else:
            quality = "low"

        out_rows.append({
            "source": source,
            "engagement_quality": quality,
            "spend": round(spend, 2),
            "registrations": int(regs),
            "cost_per_registration": round(cost_per_reg, 2) if cost_per_reg is not None else "n/a",
            "attended_live": int(live),
            "live_attendance_rate_pct": round(live_rate, 1) if live_rate is not None else "n/a",
            "attended_on_demand": int(od),
            "total_attended": int(total_attended),
            "total_attendance_rate_pct": round(total_attend_rate, 1) if total_attend_rate is not None else "n/a",
            "high_engagement": int(engaged),
            "engagement_rate_pct": round(engagement_rate, 1) if engagement_rate is not None else "n/a",
            "mqls_within_30d": int(mqls),
            "mql_rate_pct": round(mql_rate, 1) if mql_rate is not None else "n/a",
            "cost_per_mql": round(cpmql, 2) if cpmql is not None else "n/a",
        })

    out_rows.sort(key=lambda r: r["cost_per_mql"] if isinstance(r["cost_per_mql"], (int, float)) else float("inf"))

    fields = ["source", "engagement_quality", "spend", "registrations", "cost_per_registration",
              "attended_live", "live_attendance_rate_pct",
              "attended_on_demand", "total_attended", "total_attendance_rate_pct",
              "high_engagement", "engagement_rate_pct",
              "mqls_within_30d", "mql_rate_pct", "cost_per_mql"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        # Totals
        print(f"--- Webinar totals ---", file=sys.stderr)
        print(f"Spend: ${totals['spend']:,.0f}", file=sys.stderr)
        print(f"Registrations: {int(totals['regs']):,}", file=sys.stderr)
        print(f"Live attendees: {int(totals['live']):,}", file=sys.stderr)
        print(f"On-demand attendees: {int(totals['od']):,}", file=sys.stderr)
        print(f"MQLs within 30d: {int(totals['mqls']):,}", file=sys.stderr)
        if totals['mqls'] > 0:
            print(f"Blended cost per MQL: ${totals['spend']/totals['mqls']:.2f}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
