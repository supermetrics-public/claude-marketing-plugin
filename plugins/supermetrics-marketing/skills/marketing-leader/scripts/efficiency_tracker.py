#!/usr/bin/env python3
"""
Marketing efficiency tracker — actuals vs committed targets.

Computes CAC, MER, payback period, blended ROAS, CPL against user-provided
targets. Surfaces variance and trend.

Expected CSV columns:
    - month (YYYY-MM)
    - spend (total marketing spend)
    - revenue (total marketing-attributable revenue)
    - new_customers (count of acquired customers in the period)
    - leads (optional, for CPL)

Targets passed via flags. At least one target must be specified.

Usage:
    python efficiency_tracker.py monthly.csv \
        --cac-target 120 \
        --mer-target 4.5 \
        --payback-months-target 6 \
        --output efficiency.csv

The script:
    1. Computes the actual value for each metric over the most recent month and the trailing 3 months
    2. Compares actuals to targets
    3. Computes trend direction (improving / holding / declining)
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Monthly aggregated CSV")
    p.add_argument("--month-col", default="month")
    p.add_argument("--cac-target", type=float, default=None, help="Target CAC")
    p.add_argument("--mer-target", type=float, default=None, help="Target MER (revenue/spend)")
    p.add_argument("--blended-roas-target", type=float, default=None, help="Target blended ROAS")
    p.add_argument("--cpl-target", type=float, default=None, help="Target CPL")
    p.add_argument("--payback-months-target", type=float, default=None, help="Target payback period in months")
    p.add_argument("--monthly-revenue-per-customer", type=float, default=None, help="ARPU for payback calc")
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
    targets = {
        "CAC": args.cac_target,
        "MER": args.mer_target,
        "Blended ROAS": args.blended_roas_target,
        "CPL": args.cpl_target,
        "Payback (months)": args.payback_months_target,
    }
    targets = {k: v for k, v in targets.items() if v is not None}
    if not targets:
        print("Provide at least one target via --cac-target, --mer-target, --cpl-target, --blended-roas-target, or --payback-months-target.", file=sys.stderr)
        return 1

    # "lower is better" metrics
    lower_better = {"CAC", "CPL", "Payback (months)"}

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data.", file=sys.stderr)
        return 1

    # Aggregate per month
    months = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "customers": 0.0, "leads": 0.0})
    for r in rows:
        m = r.get(args.month_col, "").strip()
        if not m:
            continue
        months[m]["spend"] += to_float(r.get("spend") or r.get("cost"))
        months[m]["revenue"] += to_float(r.get("revenue") or r.get("conversion_value"))
        months[m]["customers"] += to_float(r.get("new_customers") or r.get("customers"))
        months[m]["leads"] += to_float(r.get("leads"))

    sorted_months = sorted(months.keys())
    if not sorted_months:
        print("No valid monthly data.", file=sys.stderr)
        return 1

    def compute_metrics(m_data):
        spend = sum(d["spend"] for d in m_data)
        revenue = sum(d["revenue"] for d in m_data)
        customers = sum(d["customers"] for d in m_data)
        leads = sum(d["leads"] for d in m_data)
        return {
            "CAC": spend / customers if customers > 0 else None,
            "MER": revenue / spend if spend > 0 else None,
            "Blended ROAS": revenue / spend if spend > 0 else None,
            "CPL": spend / leads if leads > 0 else None,
            "Payback (months)": (spend / customers) / args.monthly_revenue_per_customer
                if customers > 0 and args.monthly_revenue_per_customer else None,
        }

    # Latest month
    latest_data = [months[sorted_months[-1]]]
    latest = compute_metrics(latest_data)
    # Trailing 3 months
    trailing_data = [months[m] for m in sorted_months[-3:]]
    trailing = compute_metrics(trailing_data)
    # Prior 3 months (months -6 to -3)
    if len(sorted_months) >= 6:
        prior_data = [months[m] for m in sorted_months[-6:-3]]
    else:
        prior_data = trailing_data
    prior = compute_metrics(prior_data)

    out_rows = []
    for metric, target in targets.items():
        a_latest = latest.get(metric)
        a_trail = trailing.get(metric)
        a_prior = prior.get(metric)

        if a_trail is None:
            continue

        better = metric in lower_better
        variance_pct = ((a_trail - target) / target * 100) if target else None

        if a_prior:
            trend_pct = (a_trail - a_prior) / a_prior * 100
            if (better and trend_pct < -5) or (not better and trend_pct > 5):
                trend = "improving"
            elif (better and trend_pct > 5) or (not better and trend_pct < -5):
                trend = "declining"
            else:
                trend = "holding"
        else:
            trend = "n/a"
            trend_pct = None

        # Status
        if a_trail is None or target is None:
            status = "n/a"
        elif better:
            status = "on_target" if a_trail <= target * 1.05 else "off_target"
        else:
            status = "on_target" if a_trail >= target * 0.95 else "off_target"

        out_rows.append({
            "metric": metric,
            "target": target,
            "latest_month": round(a_latest, 2) if a_latest is not None else "n/a",
            "trailing_3_months": round(a_trail, 2),
            "variance_from_target_pct": round(variance_pct, 1) if variance_pct is not None else "n/a",
            "trend": trend,
            "trend_pct": round(trend_pct, 1) if trend_pct is not None else "n/a",
            "status": status,
        })

    fields = ["metric", "status", "target", "trailing_3_months", "latest_month",
              "variance_from_target_pct", "trend", "trend_pct"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        n_off = sum(1 for r in out_rows if r["status"] == "off_target")
        print(f"Wrote {len(out_rows)} metrics to {args.output}. {n_off} off target.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
