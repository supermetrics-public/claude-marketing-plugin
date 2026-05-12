#!/usr/bin/env python3
"""
Lead generation efficiency comparator.

Compares cost per lead and lead conversion rate across platforms for B2B
lead-gen campaigns. Outputs a side-by-side comparison and the per-platform
"what this means" lines that go into the summary deliverable.

Usage:
    python lead_efficiency.py input.csv --output comparison.csv

Expected CSV columns:
    - platform (or channel)
    - campaign_name
    - spend
    - clicks
    - impressions
    - leads (form fills, lead-gen form submissions, etc.)

The script aggregates per platform across all rows (assumes the user has
pre-filtered to lead-gen campaigns only — that's part of the workflow).

Outputs:
    - Per-platform: spend, leads, CPL, CTR, lead rate (leads/clicks)
    - Side-by-side comparison table
    - Spread (which platform is N% cheaper per lead)
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Lead-gen campaign CSV")
    p.add_argument("--platform-col", default="platform", help="Platform column (default: platform)")
    p.add_argument("--output", default="-", help="Output CSV path (default: stdout)")
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
        print("No data in input file.", file=sys.stderr)
        return 1

    platforms = defaultdict(lambda: {"spend": 0.0, "clicks": 0.0, "impressions": 0.0, "leads": 0.0, "campaigns": 0})
    for r in rows:
        p = r.get(args.platform_col) or r.get("channel") or "(unknown)"
        platforms[p]["spend"] += to_float(r.get("spend") or r.get("cost"))
        platforms[p]["clicks"] += to_float(r.get("clicks"))
        platforms[p]["impressions"] += to_float(r.get("impressions"))
        platforms[p]["leads"] += to_float(r.get("leads") or r.get("conversions"))
        platforms[p]["campaigns"] += 1

    out_rows = []
    for p, d in platforms.items():
        cpl = d["spend"] / d["leads"] if d["leads"] > 0 else float("inf")
        lead_rate = (d["leads"] / d["clicks"] * 100) if d["clicks"] > 0 else 0
        ctr = (d["clicks"] / d["impressions"] * 100) if d["impressions"] > 0 else 0
        out_rows.append({
            "platform": p,
            "spend": round(d["spend"], 2),
            "leads": int(d["leads"]),
            "cpl": round(cpl, 2) if cpl != float("inf") else "n/a",
            "lead_rate_pct": round(lead_rate, 2),
            "ctr_pct": round(ctr, 2),
            "campaigns": d["campaigns"],
        })

    # Rank by CPL ascending (cheaper is better)
    out_rows.sort(key=lambda r: r["cpl"] if r["cpl"] != "n/a" else float("inf"))

    fields = ["platform", "cpl", "leads", "spend", "lead_rate_pct", "ctr_pct", "campaigns"]

    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    writer = csv.DictWriter(out_stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out_rows)

    # Comparison summary
    if len(out_rows) >= 2:
        cheap = out_rows[0]
        exp = out_rows[-1]
        if cheap["cpl"] != "n/a" and exp["cpl"] != "n/a" and cheap["cpl"] > 0:
            spread_pct = (exp["cpl"] - cheap["cpl"]) / cheap["cpl"] * 100
            out_stream.write(f"\n--- Comparison ---\n")
            out_stream.write(f"Most efficient: {cheap['platform']} at ${cheap['cpl']}/lead\n")
            out_stream.write(f"Least efficient: {exp['platform']} at ${exp['cpl']}/lead\n")
            out_stream.write(f"Spread: {spread_pct:.1f}% more expensive on {exp['platform']}\n")
            out_stream.write(f"\nCaveat: 'lead' definitions can differ by platform. ")
            out_stream.write(f"LinkedIn Lead Gen Forms are auto-filled and may produce lower-friction, ")
            out_stream.write(f"lower-intent leads than form fills on a landing page. ")
            out_stream.write(f"Validate quality with downstream CRM data before reallocating budget.\n")

    if close_after:
        out_stream.close()
        print(f"Wrote comparison to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
