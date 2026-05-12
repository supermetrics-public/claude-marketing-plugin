#!/usr/bin/env python3
"""
Product / SKU-level performance analyzer.

Joins ad-driven product performance with total sales data to surface
which SKUs deserve more or less ad investment.

Expected CSV columns:
    - sku
    - product_name
    - total_units_sold
    - total_revenue
    - gross_margin_pct (optional, 0-100)
    - ad_spend
    - ad_attributed_units (optional)
    - ad_attributed_revenue
    - return_rate_pct (optional)
    - inventory_units (optional)

Usage:
    python sku_performance.py products.csv --output report.csv
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Product-level CSV")
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
        skus = list(csv.DictReader(f))

    if not skus:
        print("No SKUs.", file=sys.stderr)
        return 1

    out_rows = []
    for s in skus:
        sku = s.get("sku", "")
        name = s.get("product_name", "")
        total_units = to_float(s.get("total_units_sold"))
        total_revenue = to_float(s.get("total_revenue"))
        margin_pct = to_float(s.get("gross_margin_pct"))
        ad_spend = to_float(s.get("ad_spend"))
        ad_units = to_float(s.get("ad_attributed_units"))
        ad_revenue = to_float(s.get("ad_attributed_revenue"))
        return_rate = to_float(s.get("return_rate_pct"))
        inventory = to_float(s.get("inventory_units"))

        ad_roas = ad_revenue / ad_spend if ad_spend > 0 else None
        ad_share_pct = (ad_revenue / total_revenue * 100) if total_revenue > 0 else 0
        margin_dollars_per_unit = (total_revenue / total_units) * (margin_pct / 100) if total_units > 0 and margin_pct > 0 else None

        # Margin tier
        if margin_pct >= 60:
            margin_tier = "high"
        elif margin_pct >= 35:
            margin_tier = "medium"
        elif margin_pct > 0:
            margin_tier = "low"
        else:
            margin_tier = "unknown"

        # Recommendation logic
        rec = "hold"
        rationale = []
        if ad_roas is not None:
            if ad_roas >= 3.0 and margin_tier in ("high", "medium") and ad_share_pct < 80:
                rec = "scale_up"
                rationale.append(f"ROAS {ad_roas:.1f}x")
                rationale.append(f"{margin_tier} margin")
                if inventory > 0:
                    if total_units > 0 and inventory > total_units * 1.5:
                        rationale.append("inventory sufficient")
                    elif total_units > 0 and inventory < total_units * 0.5:
                        rec = "hold"
                        rationale.append("inventory tight")
            elif ad_roas < 1.0 or (margin_tier == "low" and ad_roas < 2.0):
                rec = "cut_from_ads"
                rationale.append(f"ROAS {ad_roas:.1f}x")
                rationale.append(f"{margin_tier} margin")
        elif total_revenue > 1000 and margin_tier in ("high", "medium") and ad_spend == 0:
            rec = "add_to_ads"
            rationale.append("strong organic, not advertised")
            rationale.append(f"{margin_tier} margin")

        if return_rate >= 15:
            rationale.append(f"high return rate {return_rate:.0f}%")
            if rec == "scale_up":
                rec = "hold"

        out_rows.append({
            "sku": sku,
            "product_name": name,
            "recommendation": rec,
            "rationale": "; ".join(rationale),
            "total_revenue": round(total_revenue, 2),
            "total_units": int(total_units),
            "gross_margin_pct": round(margin_pct, 1) if margin_pct > 0 else "n/a",
            "margin_tier": margin_tier,
            "ad_spend": round(ad_spend, 2),
            "ad_attributed_revenue": round(ad_revenue, 2),
            "ad_roas": round(ad_roas, 2) if ad_roas is not None else "n/a",
            "ad_share_pct": round(ad_share_pct, 1),
            "return_rate_pct": round(return_rate, 1) if return_rate > 0 else "n/a",
            "inventory_units": int(inventory) if inventory > 0 else "n/a",
        })

    # Sort: scale_up first, then hold, then cut, then add_to_ads
    order = {"scale_up": 0, "add_to_ads": 1, "hold": 2, "cut_from_ads": 3}
    out_rows.sort(key=lambda r: (order.get(r["recommendation"], 9), -r["total_revenue"]))

    fields = ["recommendation", "rationale", "sku", "product_name",
              "total_revenue", "total_units", "gross_margin_pct", "margin_tier",
              "ad_spend", "ad_attributed_revenue", "ad_roas", "ad_share_pct",
              "return_rate_pct", "inventory_units"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        # Summary
        recs = {}
        for r in out_rows:
            recs[r["recommendation"]] = recs.get(r["recommendation"], 0) + 1
        print(f"Wrote {len(out_rows)} SKUs to {args.output}", file=sys.stderr)
        for rec, n in recs.items():
            print(f"  {rec}: {n}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
