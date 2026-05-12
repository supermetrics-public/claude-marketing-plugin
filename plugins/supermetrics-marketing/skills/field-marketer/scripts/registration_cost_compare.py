#!/usr/bin/env python3
"""
Pre-event channel cost-per-registration comparator.

Compares CPR across channels for event campaigns and flags conclusions
that may be based on insufficient sample size.

Expected CSV columns:
    - channel (or platform)
    - campaign_name (optional, for filtering)
    - spend
    - clicks
    - registrations (or conversions)

Usage:
    python registration_cost_compare.py input.csv \
        --min-sample 30 \
        --projected-days 0 \
        --output comparison.csv

Sample size flag: when a channel has fewer than --min-sample registrations,
the script marks the comparison as "low confidence" — a 20% CPR difference
at small N is likely noise, not signal.

--projected-days: optional. If set to N > 0, the script extrapolates
expected registrations and spend if the campaign continues at current
pace for an additional N days. Useful for "should we extend?"
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Event campaign CSV")
    p.add_argument("--channel-col", default="channel", help="Channel column (default: channel)")
    p.add_argument("--days-in-period", type=int, default=30, help="Days covered by input data (default: 30)")
    p.add_argument("--min-sample", type=int, default=30, help="Minimum registrations for confident comparison (default: 30)")
    p.add_argument("--projected-days", type=int, default=0, help="Project N additional days at current pace (default: 0)")
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

    channels = defaultdict(lambda: {"spend": 0.0, "clicks": 0.0, "registrations": 0.0})
    for r in rows:
        ch = r.get(args.channel_col) or r.get("platform") or "(unknown)"
        channels[ch]["spend"] += to_float(r.get("spend") or r.get("cost"))
        channels[ch]["clicks"] += to_float(r.get("clicks"))
        channels[ch]["registrations"] += to_float(r.get("registrations") or r.get("conversions"))

    out_rows = []
    for ch, d in channels.items():
        cpr = d["spend"] / d["registrations"] if d["registrations"] > 0 else float("inf")
        cpc = d["spend"] / d["clicks"] if d["clicks"] > 0 else float("inf")
        reg_rate = d["registrations"] / d["clicks"] * 100 if d["clicks"] > 0 else 0

        confidence = "low" if d["registrations"] < args.min_sample else "ok"

        row = {
            "channel": ch,
            "spend": round(d["spend"], 2),
            "clicks": int(d["clicks"]),
            "registrations": int(d["registrations"]),
            "cost_per_registration": round(cpr, 2) if cpr != float("inf") else "n/a",
            "registration_rate_pct": round(reg_rate, 2),
            "cpc": round(cpc, 2) if cpc != float("inf") else "n/a",
            "confidence": confidence,
        }

        if args.projected_days > 0 and args.days_in_period > 0:
            daily_spend = d["spend"] / args.days_in_period
            daily_regs = d["registrations"] / args.days_in_period
            row["projected_additional_spend"] = round(daily_spend * args.projected_days, 2)
            row["projected_additional_registrations"] = int(daily_regs * args.projected_days)

        out_rows.append(row)

    # Sort by CPR ascending (cheaper is better)
    out_rows.sort(key=lambda r: r["cost_per_registration"] if r["cost_per_registration"] != "n/a" else float("inf"))

    fields = ["channel", "cost_per_registration", "registrations", "spend", "clicks",
              "registration_rate_pct", "cpc", "confidence"]
    if args.projected_days > 0:
        fields += ["projected_additional_spend", "projected_additional_registrations"]

    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    writer = csv.DictWriter(out_stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out_rows)

    # Summary
    if len(out_rows) >= 2:
        cheap = out_rows[0]
        exp = out_rows[-1]
        low_confidence = any(r["confidence"] == "low" for r in [cheap, exp])
        out_stream.write("\n--- Comparison ---\n")
        out_stream.write(f"Most efficient: {cheap['channel']} at ${cheap['cost_per_registration']}/registration\n")
        out_stream.write(f"Least efficient: {exp['channel']} at ${exp['cost_per_registration']}/registration\n")
        if low_confidence:
            out_stream.write(f"\n*** Low confidence ***\n")
            out_stream.write(f"At least one channel has fewer than {args.min_sample} registrations. ")
            out_stream.write(f"The CPR gap could be statistical noise. Recommend a smaller, hedged budget shift ")
            out_stream.write(f"(e.g. 15%) rather than a large one until more data accumulates.\n")

    if close_after:
        out_stream.close()
        print(f"Wrote comparison to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
