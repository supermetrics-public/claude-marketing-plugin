#!/usr/bin/env python3
"""
Subscription / repeat-purchase cohort retention and revenue analyzer.

Expected CSV columns:
    - cohort_month (YYYY-MM, acquisition month)
    - new_customers (total customers acquired in cohort)
    - cohort_acquisition_cost (total acquisition spend for cohort)
    - month_offset (0 = month of acquisition, 1 = month after, etc.)
    - active_customers (still active in that month_offset)
    - revenue_in_month (revenue from cohort in that month)

Usage:
    python subscription_cohorts.py cohorts.csv --output retention.csv
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Cohort CSV")
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

    cohorts = defaultdict(lambda: {"new_customers": 0.0, "cost": 0.0, "months": {}})

    with open(args.input, newline="") as f:
        for r in csv.DictReader(f):
            cm = r.get("cohort_month", "").strip()
            if not cm:
                continue
            try:
                offset = int(r.get("month_offset", "0"))
            except ValueError:
                continue
            cohorts[cm]["new_customers"] = max(cohorts[cm]["new_customers"], to_float(r.get("new_customers") or r.get("customers")))
            cohorts[cm]["cost"] = max(cohorts[cm]["cost"], to_float(r.get("cohort_acquisition_cost") or r.get("acquisition_cost") or r.get("marketing_spend")))
            cohorts[cm]["months"][offset] = {
                "active": to_float(r.get("active_customers")),
                "revenue": to_float(r.get("revenue_in_month") or r.get("revenue")),
            }

    if not cohorts:
        print("No cohorts.", file=sys.stderr)
        return 1

    horizons = [1, 3, 6, 12, 24]
    out_rows = []
    blended_customers = 0
    blended_cost = 0
    blended_rev_by_horizon = defaultdict(float)
    blended_retention_by_horizon = defaultdict(float)
    blended_retention_count = defaultdict(int)

    for cm in sorted(cohorts.keys()):
        c = cohorts[cm]
        cust = c["new_customers"]
        cost = c["cost"]
        if cust <= 0:
            continue

        cac = cost / cust if cust > 0 else None

        retention = {}
        cumulative_revenue = {}
        cum_rev = 0
        for h in sorted(set(horizons + list(c["months"].keys()))):
            if h in c["months"]:
                if h in horizons:
                    retention[h] = c["months"][h]["active"] / cust * 100 if cust > 0 else None
                cum_rev += c["months"][h]["revenue"]
            if h in horizons:
                cumulative_revenue[h] = cum_rev

        # Payback period
        payback = None
        cum = 0
        for offset in sorted(c["months"].keys()):
            cum += c["months"][offset]["revenue"]
            arpc = cum / cust if cust > 0 else 0
            if cac is not None and arpc >= cac:
                payback = offset
                break

        row = {
            "cohort_month": cm,
            "new_customers": int(cust),
            "acquisition_cost": round(cost, 2),
            "CAC": round(cac, 2) if cac is not None else "n/a",
            "payback_months": payback if payback is not None else f">{max(c['months'].keys()) if c['months'] else 0}",
        }
        for h in horizons:
            row[f"retention_M{h}_pct"] = round(retention[h], 1) if h in retention and retention[h] is not None else "n/a"
            row[f"cum_revenue_M{h}_per_customer"] = round(cumulative_revenue[h] / cust, 2) if h in cumulative_revenue and cust > 0 else "n/a"
        out_rows.append(row)

        blended_customers += cust
        blended_cost += cost
        for h in horizons:
            if h in retention and retention[h] is not None:
                blended_retention_by_horizon[h] += retention[h]
                blended_retention_count[h] += 1
            if h in cumulative_revenue:
                blended_rev_by_horizon[h] += cumulative_revenue[h]

    if blended_customers > 0:
        blended_cac = blended_cost / blended_customers
        blended_row = {
            "cohort_month": "BLENDED",
            "new_customers": int(blended_customers),
            "acquisition_cost": round(blended_cost, 2),
            "CAC": round(blended_cac, 2),
            "payback_months": "see cohorts",
        }
        for h in horizons:
            blended_row[f"retention_M{h}_pct"] = (
                round(blended_retention_by_horizon[h] / blended_retention_count[h], 1)
                if blended_retention_count[h] > 0 else "n/a"
            )
            blended_row[f"cum_revenue_M{h}_per_customer"] = (
                round(blended_rev_by_horizon[h] / blended_customers, 2) if blended_customers > 0 else "n/a"
            )
        out_rows.append(blended_row)

    fields = ["cohort_month", "new_customers", "acquisition_cost", "CAC", "payback_months"]
    for h in horizons:
        fields.append(f"retention_M{h}_pct")
        fields.append(f"cum_revenue_M{h}_per_customer")

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote retention for {len(out_rows) - 1} cohorts plus blended to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
