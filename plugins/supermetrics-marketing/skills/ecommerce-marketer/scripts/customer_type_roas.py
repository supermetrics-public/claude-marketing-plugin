#!/usr/bin/env python3
"""
ROAS by customer type (new vs returning) per channel.

Expected CSV columns:
    - channel
    - spend
    - new_customer_purchases
    - new_customer_revenue
    - returning_customer_purchases
    - returning_customer_revenue

Usage:
    python customer_type_roas.py channels.csv --output split.csv
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Channel-level customer-type CSV")
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

    out_rows = []
    for r in rows:
        channel = r.get("channel", "")
        spend = to_float(r.get("spend"))
        new_pur = to_float(r.get("new_customer_purchases"))
        new_rev = to_float(r.get("new_customer_revenue"))
        ret_pur = to_float(r.get("returning_customer_purchases"))
        ret_rev = to_float(r.get("returning_customer_revenue"))

        total_pur = new_pur + ret_pur
        total_rev = new_rev + ret_rev
        total_roas = total_rev / spend if spend > 0 else None
        new_roas = new_rev / spend if spend > 0 else None
        ret_roas = ret_rev / spend if spend > 0 else None
        new_rev_share = new_rev / total_rev * 100 if total_rev > 0 else 0
        cac_new = spend / new_pur if new_pur > 0 else None
        cost_per_ret = spend / ret_pur if ret_pur > 0 else None
        new_aov = new_rev / new_pur if new_pur > 0 else None
        ret_aov = ret_rev / ret_pur if ret_pur > 0 else None

        # Classify channel pattern
        if new_rev_share >= 75:
            pattern = "acquisition_channel"
        elif new_rev_share <= 25:
            pattern = "retention_channel"
        else:
            pattern = "balanced"

        out_rows.append({
            "channel": channel,
            "pattern": pattern,
            "spend": round(spend, 2),
            "total_roas": round(total_roas, 2) if total_roas is not None else "n/a",
            "new_customer_revenue_share_pct": round(new_rev_share, 1),
            "new_customer_purchases": int(new_pur),
            "new_customer_revenue": round(new_rev, 2),
            "new_customer_roas": round(new_roas, 2) if new_roas is not None else "n/a",
            "cac_new_customer": round(cac_new, 2) if cac_new is not None else "n/a",
            "new_customer_aov": round(new_aov, 2) if new_aov is not None else "n/a",
            "returning_customer_purchases": int(ret_pur),
            "returning_customer_revenue": round(ret_rev, 2),
            "returning_customer_roas": round(ret_roas, 2) if ret_roas is not None else "n/a",
            "cost_per_returning_purchase": round(cost_per_ret, 2) if cost_per_ret is not None else "n/a",
            "returning_customer_aov": round(ret_aov, 2) if ret_aov is not None else "n/a",
        })

    out_rows.sort(key=lambda r: -r["spend"])

    fields = ["channel", "pattern", "spend", "total_roas", "new_customer_revenue_share_pct",
              "new_customer_purchases", "new_customer_revenue", "new_customer_roas",
              "cac_new_customer", "new_customer_aov",
              "returning_customer_purchases", "returning_customer_revenue", "returning_customer_roas",
              "cost_per_returning_purchase", "returning_customer_aov"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} channels to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
