#!/usr/bin/env python3
"""
Gated content / webinar funnel analyzer.

Builds the full funnel from paid promotion through registration,
attendance/download, and downstream MQL behavior for a specific content
asset.

Expected CSV columns:
    - channel (paid channel name; can include "Organic" for non-paid)
    - spend
    - clicks
    - registrations (form fills for this content)
    - attended_or_downloaded (consumed the content)
    - mqls_within_30_days (registered → became MQL within 30 days)
    - opportunities_within_60_days (optional)

Usage:
    python gated_content_funnel.py funnel.csv --output report.csv

Outputs per channel: full conversion funnel rates and cost per MQL via
this content asset.
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Funnel CSV")
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
    total_spend = 0
    total_regs = 0
    total_mqls = 0

    for r in rows:
        channel = r.get("channel", "(unknown)")
        spend = to_float(r.get("spend"))
        clicks = to_float(r.get("clicks"))
        regs = to_float(r.get("registrations"))
        attended = to_float(r.get("attended_or_downloaded"))
        mqls = to_float(r.get("mqls_within_30_days"))
        opps = to_float(r.get("opportunities_within_60_days"))

        total_spend += spend
        total_regs += regs
        total_mqls += mqls

        reg_rate = regs / clicks * 100 if clicks > 0 else None
        attend_rate = attended / regs * 100 if regs > 0 else None
        mql_rate_from_reg = mqls / regs * 100 if regs > 0 else None
        opp_rate_from_reg = opps / regs * 100 if regs > 0 else None
        cost_per_reg = spend / regs if regs > 0 else None
        cost_per_mql = spend / mqls if mqls > 0 else None

        out_rows.append({
            "channel": channel,
            "spend": round(spend, 2),
            "clicks": int(clicks),
            "registrations": int(regs),
            "registration_rate_pct": round(reg_rate, 2) if reg_rate is not None else "n/a",
            "attended_or_downloaded": int(attended),
            "attendance_rate_pct": round(attend_rate, 1) if attend_rate is not None else "n/a",
            "mqls_within_30d": int(mqls),
            "mql_rate_from_reg_pct": round(mql_rate_from_reg, 1) if mql_rate_from_reg is not None else "n/a",
            "opportunities_within_60d": int(opps),
            "opp_rate_from_reg_pct": round(opp_rate_from_reg, 1) if opp_rate_from_reg is not None else "n/a",
            "cost_per_registration": round(cost_per_reg, 2) if cost_per_reg is not None else "n/a",
            "cost_per_mql": round(cost_per_mql, 2) if cost_per_mql is not None else "n/a",
        })

    out_rows.sort(key=lambda r: r["cost_per_mql"] if isinstance(r["cost_per_mql"], (int, float)) else float("inf"))

    fields = ["channel", "spend", "clicks", "registrations", "registration_rate_pct",
              "attended_or_downloaded", "attendance_rate_pct",
              "mqls_within_30d", "mql_rate_from_reg_pct",
              "opportunities_within_60d", "opp_rate_from_reg_pct",
              "cost_per_registration", "cost_per_mql"]
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
        blended_cpmql = total_spend / total_mqls if total_mqls > 0 else None
        if blended_cpmql is not None:
            print(f"Blended cost per MQL via this content: ${blended_cpmql:.2f}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
