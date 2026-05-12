#!/usr/bin/env python3
"""
Pipeline attribution by channel.

Joins ad spend per channel with CRM opportunity data to compute cost
per opportunity (CPO) and pipeline ROAS (pipeline value / spend).

Expected inputs: two CSVs.

Spend CSV columns:
    - channel
    - spend

Opportunities CSV columns:
    - source (channel name — must match spend CSV channel)
    - amount (opportunity value)
    - stage (optional, for filtering)

Usage:
    python pipeline_attribution.py \
        --spend spend.csv --opps opportunities.csv \
        --stage-filter "Stage 2,Stage 3" \
        --output attribution.csv

Outputs per channel: spend, opp count, pipeline value, CPO, pipeline ROAS.
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spend", required=True)
    p.add_argument("--opps", required=True)
    p.add_argument("--stage-filter", default="", help="Comma-separated stages to include (default: all)")
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
    stage_filter = {s.strip() for s in args.stage_filter.split(",") if s.strip()}

    spend = defaultdict(float)
    with open(args.spend, newline="") as f:
        for r in csv.DictReader(f):
            ch = r.get("channel") or r.get("source") or "(unknown)"
            spend[ch] += to_float(r.get("spend") or r.get("cost"))

    opps_count = defaultdict(int)
    opps_value = defaultdict(float)
    with open(args.opps, newline="") as f:
        for r in csv.DictReader(f):
            ch = r.get("source") or r.get("channel") or "(unknown)"
            stage = r.get("stage", "")
            if stage_filter and stage not in stage_filter:
                continue
            opps_count[ch] += 1
            opps_value[ch] += to_float(r.get("amount") or r.get("value"))

    channels = sorted(set(spend.keys()) | set(opps_count.keys()))

    out_rows = []
    for ch in channels:
        s = spend[ch]
        n = opps_count[ch]
        v = opps_value[ch]
        cpo = s / n if n > 0 else None
        roas = v / s if s > 0 else None
        out_rows.append({
            "channel": ch,
            "spend": round(s, 2),
            "opportunities": n,
            "pipeline_value": round(v, 2),
            "cost_per_opportunity": round(cpo, 2) if cpo is not None else "n/a",
            "pipeline_roas": round(roas, 2) if roas is not None else "n/a",
        })

    out_rows.sort(key=lambda r: -r["pipeline_value"])

    fields = ["channel", "spend", "opportunities", "pipeline_value", "cost_per_opportunity", "pipeline_roas"]
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
