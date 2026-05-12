#!/usr/bin/env python3
"""
Unit economics calculator: CAC, LTV, LTV:CAC, payback period.

Computes blended unit economics from marketing spend + customer
acquisition data + cohort revenue data.

Expected CSV columns:
    - cohort_month (YYYY-MM, the month customers were acquired)
    - new_customers (count of customers acquired in that cohort)
    - marketing_spend_in_cohort_month (total marketing spend in that month)
    - month_offset (months since acquisition, 0 = month of acquisition)
    - revenue (revenue from cohort in that month_offset)

Usage:
    python unit_economics.py cohorts.csv \
        --ltv-horizon-months 12 \
        --output unit_econ.csv

Outputs per-cohort:
    - CAC
    - LTV at various horizons (3/6/12/24 months)
    - LTV:CAC ratio
    - Payback period (months to recover CAC)

Plus blended/aggregate view.
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Cohort revenue CSV")
    p.add_argument("--cohort-col", default="cohort_month")
    p.add_argument("--ltv-horizon-months", type=int, default=12, help="Primary LTV horizon (default: 12)")
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

    # cohorts[cohort_month] = {
    #   "new_customers": float,
    #   "marketing_spend": float,
    #   "revenue_by_offset": {0: x, 1: y, ...}  # cumulative-friendly later
    # }
    cohorts = defaultdict(lambda: {"new_customers": 0.0, "marketing_spend": 0.0, "revenue_by_offset": defaultdict(float)})

    for r in rows:
        cm = r.get(args.cohort_col, "").strip()
        if not cm:
            continue
        offset_raw = r.get("month_offset", "0")
        try:
            offset = int(offset_raw)
        except ValueError:
            continue

        c = cohorts[cm]
        # New customers and marketing spend should be the same on every row of the cohort —
        # take the max to handle duplicate rows
        c["new_customers"] = max(c["new_customers"], to_float(r.get("new_customers") or r.get("customers")))
        c["marketing_spend"] = max(c["marketing_spend"], to_float(r.get("marketing_spend_in_cohort_month") or r.get("marketing_spend")))
        c["revenue_by_offset"][offset] += to_float(r.get("revenue"))

    if not cohorts:
        print("No valid cohort data.", file=sys.stderr)
        return 1

    out_rows = []
    horizons = [3, 6, args.ltv_horizon_months, 24]
    horizons = sorted(set(h for h in horizons if h > 0))

    blended_customers = 0
    blended_spend = 0
    blended_rev_by_horizon = defaultdict(float)

    for cm in sorted(cohorts.keys()):
        c = cohorts[cm]
        customers = c["new_customers"]
        spend = c["marketing_spend"]
        if customers <= 0:
            continue

        cac = spend / customers

        ltvs = {}
        for h in horizons:
            cumulative = sum(c["revenue_by_offset"][o] for o in range(h + 1))
            ltvs[h] = cumulative / customers if customers > 0 else 0
            blended_rev_by_horizon[h] += cumulative

        primary_ltv = ltvs[args.ltv_horizon_months]
        ltv_cac = primary_ltv / cac if cac > 0 else None

        # Payback period: find the smallest offset where cumulative revenue per customer ≥ CAC
        payback = None
        cum = 0
        for o in sorted(c["revenue_by_offset"].keys()):
            cum += c["revenue_by_offset"][o]
            arpc = cum / customers
            if arpc >= cac:
                payback = o
                break

        blended_customers += customers
        blended_spend += spend

        row = {
            "cohort_month": cm,
            "new_customers": int(customers),
            "marketing_spend": round(spend, 2),
            "CAC": round(cac, 2),
            f"LTV_{args.ltv_horizon_months}mo": round(primary_ltv, 2),
            "LTV_CAC_ratio": round(ltv_cac, 2) if ltv_cac is not None else "n/a",
            "payback_months": payback if payback is not None else f">{max(c['revenue_by_offset'].keys()) if c['revenue_by_offset'] else 0}",
        }
        for h in horizons:
            if h != args.ltv_horizon_months:
                row[f"LTV_{h}mo"] = round(ltvs[h], 2)
        out_rows.append(row)

    # Blended row
    if blended_customers > 0:
        blended_cac = blended_spend / blended_customers
        blended_primary_ltv = blended_rev_by_horizon[args.ltv_horizon_months] / blended_customers
        blended_ltv_cac = blended_primary_ltv / blended_cac if blended_cac > 0 else None

        blended_row = {
            "cohort_month": "BLENDED",
            "new_customers": int(blended_customers),
            "marketing_spend": round(blended_spend, 2),
            "CAC": round(blended_cac, 2),
            f"LTV_{args.ltv_horizon_months}mo": round(blended_primary_ltv, 2),
            "LTV_CAC_ratio": round(blended_ltv_cac, 2) if blended_ltv_cac is not None else "n/a",
            "payback_months": "see cohorts",
        }
        for h in horizons:
            if h != args.ltv_horizon_months:
                blended_row[f"LTV_{h}mo"] = round(blended_rev_by_horizon[h] / blended_customers, 2)
        out_rows.append(blended_row)

    fields = ["cohort_month", "new_customers", "marketing_spend", "CAC"] + \
             [f"LTV_{h}mo" for h in horizons] + \
             ["LTV_CAC_ratio", "payback_months"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote unit economics for {len(out_rows) - 1} cohorts plus blended to {args.output}.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
