#!/usr/bin/env python3
"""
Post-event geo lift analyzer.

Compares performance metrics in a target region (where a physical event
occurred) against a "national" baseline that *excludes* the target region.
Reports whether the regional metrics show meaningful lift.

Expected CSV columns:
    - region (or geo or location)
    - clicks
    - impressions
    - conversions
    - spend

Usage:
    python geo_lift_analyzer.py input.csv --target-region "San Francisco"

The script:
    1. Computes target region metrics (CTR, CPC, conversion rate)
    2. Computes "rest of country" baseline from all other regions
    3. Reports lift as percentage above baseline
    4. Flags whether the gap is meaningful given sample size

A "meaningful lift" requires:
    - At least 1000 impressions in the target region (otherwise sample too small)
    - At least 20% lift on the engagement metric (CTR), OR
    - At least 20% lift on the conversion metric
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Geo-segmented campaign CSV")
    p.add_argument("--region-col", default="region", help="Region column (default: region)")
    p.add_argument("--target-region", required=True, help="Target region for the event")
    p.add_argument("--min-impressions", type=int, default=1000, help="Min impressions in target for meaningful comparison (default: 1000)")
    p.add_argument("--lift-threshold", type=float, default=20.0, help="Min lift % to consider meaningful (default: 20)")
    p.add_argument("--output", default="-", help="Output path (default: stdout)")
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

    region_col = args.region_col
    if region_col not in rows[0]:
        for c in ("region", "geo", "location", "city", "country"):
            if c in rows[0]:
                region_col = c
                break

    regions = defaultdict(lambda: {"clicks": 0.0, "impressions": 0.0, "conversions": 0.0, "spend": 0.0})
    for r in rows:
        reg = r.get(region_col, "(unknown)")
        regions[reg]["clicks"] += to_float(r.get("clicks"))
        regions[reg]["impressions"] += to_float(r.get("impressions"))
        regions[reg]["conversions"] += to_float(r.get("conversions"))
        regions[reg]["spend"] += to_float(r.get("spend") or r.get("cost"))

    if args.target_region not in regions:
        # Case-insensitive fallback
        match = None
        for r in regions:
            if r.lower() == args.target_region.lower():
                match = r
                break
        if not match:
            print(f"Target region '{args.target_region}' not found. Available regions: {sorted(regions.keys())}", file=sys.stderr)
            return 1
        args.target_region = match

    target = regions[args.target_region]
    rest = defaultdict(float)
    for r, d in regions.items():
        if r == args.target_region:
            continue
        for k in d:
            rest[k] += d[k]

    target_ctr = (target["clicks"] / target["impressions"] * 100) if target["impressions"] > 0 else 0
    target_cpc = (target["spend"] / target["clicks"]) if target["clicks"] > 0 else float("inf")
    target_cvr = (target["conversions"] / target["clicks"] * 100) if target["clicks"] > 0 else 0

    rest_ctr = (rest["clicks"] / rest["impressions"] * 100) if rest["impressions"] > 0 else 0
    rest_cpc = (rest["spend"] / rest["clicks"]) if rest["clicks"] > 0 else float("inf")
    rest_cvr = (rest["conversions"] / rest["clicks"] * 100) if rest["clicks"] > 0 else 0

    def lift_pct(target_val, base_val):
        if base_val == 0:
            return None
        return (target_val - base_val) / base_val * 100

    ctr_lift = lift_pct(target_ctr, rest_ctr)
    cvr_lift = lift_pct(target_cvr, rest_cvr)
    cpc_change = lift_pct(target_cpc, rest_cpc) if target_cpc != float("inf") and rest_cpc != float("inf") else None

    # Verdict
    sufficient_sample = target["impressions"] >= args.min_impressions

    if not sufficient_sample:
        verdict = "Insufficient data"
        verdict_detail = f"Target region has {int(target['impressions'])} impressions; need at least {args.min_impressions} for a confident comparison."
    else:
        ctr_meaningful = ctr_lift is not None and ctr_lift >= args.lift_threshold
        cvr_meaningful = cvr_lift is not None and cvr_lift >= args.lift_threshold

        if ctr_meaningful or cvr_meaningful:
            verdict = "Measurable lift"
            parts = []
            if ctr_meaningful:
                parts.append(f"CTR +{ctr_lift:.1f}%")
            if cvr_meaningful:
                parts.append(f"conversion rate +{cvr_lift:.1f}%")
            verdict_detail = f"Target region shows: {', '.join(parts)} vs. rest of country."
        else:
            verdict = "No detectable lift"
            verdict_detail = f"Differences between target region and rest of country are within {args.lift_threshold}% noise range — can't claim the event drove digital engagement."

    out_lines = []
    out_lines.append(f"--- Geo Lift Analysis: {args.target_region} ---\n")
    out_lines.append(f"Verdict: {verdict}")
    out_lines.append(f"{verdict_detail}\n")
    out_lines.append("--- Target region ---")
    out_lines.append(f"Impressions: {int(target['impressions']):,}")
    out_lines.append(f"Clicks: {int(target['clicks']):,}")
    out_lines.append(f"Conversions: {int(target['conversions']):,}")
    out_lines.append(f"Spend: ${target['spend']:,.2f}")
    out_lines.append(f"CTR: {target_ctr:.3f}%")
    out_lines.append(f"CPC: ${target_cpc:.2f}" if target_cpc != float("inf") else "CPC: n/a")
    out_lines.append(f"Conversion rate: {target_cvr:.2f}%\n")
    out_lines.append("--- Rest of country (baseline) ---")
    out_lines.append(f"Impressions: {int(rest['impressions']):,}")
    out_lines.append(f"Clicks: {int(rest['clicks']):,}")
    out_lines.append(f"Conversions: {int(rest['conversions']):,}")
    out_lines.append(f"Spend: ${rest['spend']:,.2f}")
    out_lines.append(f"CTR: {rest_ctr:.3f}%")
    out_lines.append(f"CPC: ${rest_cpc:.2f}" if rest_cpc != float("inf") else "CPC: n/a")
    out_lines.append(f"Conversion rate: {rest_cvr:.2f}%\n")
    out_lines.append("--- Lift ---")
    out_lines.append(f"CTR: {ctr_lift:+.1f}%" if ctr_lift is not None else "CTR: n/a")
    out_lines.append(f"Conversion rate: {cvr_lift:+.1f}%" if cvr_lift is not None else "Conversion rate: n/a")
    out_lines.append(f"CPC: {cpc_change:+.1f}%" if cpc_change is not None else "CPC: n/a")
    out_lines.append("\nCaveat: this analysis can't distinguish event-driven lift from paid-promotion-driven lift. If targeted ads ran in the region during this window, the lift is jointly attributable to both — not the event alone.")

    output_text = "\n".join(out_lines) + "\n"

    if args.output == "-":
        sys.stdout.write(output_text)
    else:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Wrote analysis to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
