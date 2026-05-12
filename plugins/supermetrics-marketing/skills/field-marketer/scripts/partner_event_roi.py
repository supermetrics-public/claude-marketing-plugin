#!/usr/bin/env python3
"""
Partner / co-marketing event ROI analyzer.

Computes user-only ROI separately from blended (user + partner) ROI
when partner-side numbers are available.

Expected CSV columns:
    - cost_category (sponsorship_fee, user_promotion, user_production, partner_inkind)
    - amount

And optionally:
    --user-registrations N
    --user-mqls N
    --user-pipeline N
    --partner-registrations N (if partner shared their number)
    --partner-mqls N
    --partner-pipeline N

Usage:
    python partner_event_roi.py costs.csv \
        --user-registrations 220 --user-mqls 38 --user-pipeline 280000 \
        --partner-registrations 180 --partner-mqls 25 --partner-pipeline 195000 \
        --output recap.csv
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Cost categories CSV")
    p.add_argument("--user-registrations", type=int, default=0)
    p.add_argument("--user-mqls", type=int, default=0)
    p.add_argument("--user-pipeline", type=float, default=0)
    p.add_argument("--partner-registrations", type=int, default=0)
    p.add_argument("--partner-mqls", type=int, default=0)
    p.add_argument("--partner-pipeline", type=float, default=0)
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

    costs = defaultdict(float)
    with open(args.input, newline="") as f:
        for r in csv.DictReader(f):
            cat = r.get("cost_category", "(unknown)")
            costs[cat] += to_float(r.get("amount"))

    total_user_cost = sum(v for k, v in costs.items() if not k.startswith("partner"))
    total_partner_cost = sum(v for k, v in costs.items() if k.startswith("partner"))
    total_blended_cost = total_user_cost + total_partner_cost

    # User-only ROI
    user_total_regs = args.user_registrations
    user_cpr = total_user_cost / user_total_regs if user_total_regs > 0 else None
    user_cpmql = total_user_cost / args.user_mqls if args.user_mqls > 0 else None
    user_pipeline_roas = args.user_pipeline / total_user_cost if total_user_cost > 0 else None

    # Blended ROI
    blended_regs = args.user_registrations + args.partner_registrations
    blended_mqls = args.user_mqls + args.partner_mqls
    blended_pipeline = args.user_pipeline + args.partner_pipeline
    blended_cpr = total_user_cost / blended_regs if blended_regs > 0 else None  # User cost over blended audience
    blended_cpmql = total_user_cost / blended_mqls if blended_mqls > 0 else None
    blended_pipeline_roas = blended_pipeline / total_user_cost if total_user_cost > 0 else None

    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    out_stream.write("--- Partner event ROI summary ---\n\n")
    out_stream.write("Cost breakdown:\n")
    for cat in sorted(costs.keys()):
        out_stream.write(f"  {cat}: ${costs[cat]:,.2f}\n")
    out_stream.write(f"  User-only total: ${total_user_cost:,.2f}\n")
    out_stream.write(f"  Partner contribution: ${total_partner_cost:,.2f}\n")
    out_stream.write(f"  Blended total: ${total_blended_cost:,.2f}\n\n")

    out_stream.write("User-only view (the user's investment, the user's outcomes):\n")
    out_stream.write(f"  Registrations: {user_total_regs:,}\n")
    out_stream.write(f"  MQLs: {args.user_mqls:,}\n")
    out_stream.write(f"  Pipeline created: ${args.user_pipeline:,.2f}\n")
    out_stream.write(f"  Cost per registration: ${user_cpr:,.2f}\n" if user_cpr is not None else "  Cost per registration: n/a\n")
    out_stream.write(f"  Cost per MQL: ${user_cpmql:,.2f}\n" if user_cpmql is not None else "  Cost per MQL: n/a\n")
    out_stream.write(f"  Pipeline ROAS: {user_pipeline_roas:.2f}x\n" if user_pipeline_roas is not None else "  Pipeline ROAS: n/a\n")

    if args.partner_registrations or args.partner_mqls or args.partner_pipeline:
        out_stream.write("\nBlended view (user investment, user + partner outcomes):\n")
        out_stream.write(f"  Total registrations: {blended_regs:,}\n")
        out_stream.write(f"  Total MQLs: {blended_mqls:,}\n")
        out_stream.write(f"  Total pipeline: ${blended_pipeline:,.2f}\n")
        out_stream.write(f"  User-cost-per-blended-registration: ${blended_cpr:,.2f}\n" if blended_cpr is not None else "")
        out_stream.write(f"  User-cost-per-blended-MQL: ${blended_cpmql:,.2f}\n" if blended_cpmql is not None else "")
        out_stream.write(f"  Blended pipeline ROAS: {blended_pipeline_roas:.2f}x\n" if blended_pipeline_roas is not None else "")
        out_stream.write("\n(Note: blended view counts the partner's outcomes too — useful only if both sides agreed on attribution.)\n")

    if close_after:
        out_stream.close()
        print(f"Wrote partner event ROI to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
