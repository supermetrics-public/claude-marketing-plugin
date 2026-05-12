#!/usr/bin/env python3
"""
Pre-promo planning model.

Takes prior-year promo performance + growth assumption + planned budget,
projects upcoming promo outcomes per channel.

Expected CSV columns (prior year promo data):
    - channel
    - spend
    - purchases
    - revenue
    - aov (optional, computed if not provided)

Usage:
    python promo_planner.py last_year.csv \
        --growth-pct 15 \
        --target-budget 480000 \
        --output plan.csv
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Prior year promo CSV")
    p.add_argument("--growth-pct", type=float, default=10.0, help="Assumed Y/Y growth (default: 10%)")
    p.add_argument("--target-budget", type=float, default=None, help="Target promo budget (defaults to last year * (1+growth))")
    p.add_argument("--aov-growth-pct", type=float, default=5.0, help="Assumed AOV growth (default: 5%)")
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
        print("No prior-year data.", file=sys.stderr)
        return 1

    prior = []
    total_prior_spend = 0
    total_prior_revenue = 0
    total_prior_purchases = 0
    for r in rows:
        ch = r.get("channel", "")
        spend = to_float(r.get("spend"))
        purchases = to_float(r.get("purchases"))
        revenue = to_float(r.get("revenue"))
        aov = to_float(r.get("aov")) or (revenue / purchases if purchases > 0 else 0)
        roas = revenue / spend if spend > 0 else 0
        cpa = spend / purchases if purchases > 0 else 0
        prior.append({"channel": ch, "spend": spend, "purchases": purchases, "revenue": revenue, "aov": aov, "roas": roas, "cpa": cpa})
        total_prior_spend += spend
        total_prior_revenue += revenue
        total_prior_purchases += purchases

    target_budget = args.target_budget if args.target_budget else total_prior_spend * (1 + args.growth_pct / 100)
    spend_growth_factor = target_budget / total_prior_spend if total_prior_spend > 0 else 1
    aov_factor = 1 + args.aov_growth_pct / 100

    # Project per channel — keep last year's relative mix but apply spend factor
    out_rows = []
    proj_total_revenue = 0
    proj_total_purchases = 0
    for p in prior:
        proj_spend = p["spend"] * spend_growth_factor
        proj_aov = p["aov"] * aov_factor
        # Assume CPA holds (could be improved by reducing); revenue from new spend
        proj_purchases = proj_spend / p["cpa"] if p["cpa"] > 0 else 0
        proj_revenue = proj_purchases * proj_aov
        proj_roas = proj_revenue / proj_spend if proj_spend > 0 else 0

        # Stretch and conservative scenarios
        stretch_revenue = proj_revenue * 1.15
        conservative_revenue = proj_revenue * 0.85

        out_rows.append({
            "channel": p["channel"],
            "prior_year_spend": round(p["spend"], 2),
            "proposed_spend": round(proj_spend, 2),
            "spend_change_pct": round((proj_spend - p["spend"]) / p["spend"] * 100, 1) if p["spend"] > 0 else "n/a",
            "prior_year_revenue": round(p["revenue"], 2),
            "projected_revenue": round(proj_revenue, 2),
            "projected_purchases": int(proj_purchases),
            "projected_aov": round(proj_aov, 2),
            "projected_roas": round(proj_roas, 2),
            "conservative_revenue": round(conservative_revenue, 2),
            "stretch_revenue": round(stretch_revenue, 2),
        })
        proj_total_revenue += proj_revenue
        proj_total_purchases += proj_purchases

    fields = ["channel", "prior_year_spend", "proposed_spend", "spend_change_pct",
              "prior_year_revenue", "projected_revenue", "projected_purchases",
              "projected_aov", "projected_roas",
              "conservative_revenue", "stretch_revenue"]

    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    writer = csv.DictWriter(out_stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out_rows)

    out_stream.write(f"\n--- Promo plan summary ---\n")
    out_stream.write(f"Prior year total spend:    ${total_prior_spend:,.2f}\n")
    out_stream.write(f"Proposed total spend:      ${target_budget:,.2f} ({spend_growth_factor:.2f}x prior year)\n")
    out_stream.write(f"Prior year total revenue:  ${total_prior_revenue:,.2f}\n")
    out_stream.write(f"Projected total revenue:   ${proj_total_revenue:,.2f}\n")
    out_stream.write(f"Conservative scenario:     ${proj_total_revenue * 0.85:,.2f}\n")
    out_stream.write(f"Stretch scenario:          ${proj_total_revenue * 1.15:,.2f}\n")
    out_stream.write(f"Blended projected ROAS:    {proj_total_revenue / target_budget if target_budget > 0 else 0:.2f}x\n")
    out_stream.write(f"\nAssumptions: AOV grows {args.aov_growth_pct}%, channel-level CPA holds, mix proportional to prior year.\n")

    if close_after:
        out_stream.close()
        print(f"Wrote promo plan to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
