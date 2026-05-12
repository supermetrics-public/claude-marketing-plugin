#!/usr/bin/env python3
"""
Budget reallocation modeler with diminishing-returns dampening.

Given current channel ROAS and a target total spend, models a recommended
reallocation. Doesn't naively dump all spend into the highest-ROAS channel
— applies dampening based on each channel's observed ROAS variance over
spend volume.

Expected CSV columns:
    - channel
    - date (daily)
    - spend
    - revenue (or conversion_value or purchase_value)

Usage:
    python budget_optimizer.py daily.csv \
        --target-spend 250000 \
        --max-shift-pct 25 \
        --locked "Google Ads:50000" \
        --output plan.csv

Logic:
    1. Aggregate daily data per channel to compute current ROAS and spend
    2. Estimate diminishing-returns coefficient per channel:
       - Group days by daily-spend quartile
       - Compute ROAS in each quartile
       - If ROAS drops from low to high spend quartile, dampening is higher
       - If ROAS holds steady, dampening is lower
    3. Reallocate toward higher-ROAS channels, but cap any single channel's
       shift at --max-shift-pct of its current spend
    4. Output proposed spend, projected revenue, and the assumptions

This is a model, not a prediction. The output is "given these assumptions
about diminishing returns, here's the math."
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Daily channel-level CSV")
    p.add_argument("--channel-col", default="channel", help="Channel column")
    p.add_argument("--target-spend", type=float, required=True, help="Target total spend for next period")
    p.add_argument("--max-shift-pct", type=float, default=25.0, help="Max %% shift per channel (default: 25)")
    p.add_argument("--locked", default="", help="Locked channels: 'Channel:Amount,Channel:Amount'")
    p.add_argument("--metric", default="roas", choices=["roas", "cpa"], help="Optimize for (default: roas)")
    p.add_argument("--output", default="-", help="Output CSV (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def parse_locked(s):
    out = {}
    for item in s.split(","):
        if ":" not in item:
            continue
        ch, amt = item.rsplit(":", 1)
        out[ch.strip()] = to_float(amt)
    return out


def main():
    args = parse_args()
    locked = parse_locked(args.locked)

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    # Aggregate per (channel, date)
    daily = defaultdict(lambda: defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "conversions": 0.0}))
    for r in rows:
        ch = r.get(args.channel_col, "(unknown)")
        date = r.get("date", "")
        daily[ch][date]["spend"] += to_float(r.get("spend") or r.get("cost"))
        daily[ch][date]["revenue"] += to_float(r.get("revenue") or r.get("conversion_value"))
        daily[ch][date]["conversions"] += to_float(r.get("conversions"))

    # Per channel: total spend, total revenue, and dampening coefficient
    channels = {}
    for ch, days in daily.items():
        total_spend = sum(d["spend"] for d in days.values())
        total_rev = sum(d["revenue"] for d in days.values())
        total_conv = sum(d["conversions"] for d in days.values())

        if total_spend <= 0:
            continue

        # Estimate dampening: compare ROAS across spend quartiles
        day_list = [(d["spend"], d["revenue"]) for d in days.values() if d["spend"] > 0]
        day_list.sort(key=lambda x: x[0])
        n = len(day_list)
        if n >= 8:
            low_q = day_list[: n // 4]
            high_q = day_list[-n // 4 :]
            low_roas = sum(r for _, r in low_q) / sum(s for s, _ in low_q) if sum(s for s, _ in low_q) > 0 else 0
            high_roas = sum(r for _, r in high_q) / sum(s for s, _ in high_q) if sum(s for s, _ in high_q) > 0 else 0
            if low_roas > 0:
                roas_ratio = high_roas / low_roas
                # Dampening: 1.0 = no compression, 0.5 = strong compression
                dampening = max(0.5, min(1.0, roas_ratio))
            else:
                dampening = 0.85
        else:
            dampening = 0.85  # Default when not enough data

        channels[ch] = {
            "spend": total_spend,
            "revenue": total_rev,
            "conversions": total_conv,
            "roas": total_rev / total_spend if total_spend > 0 else 0,
            "cpa": total_spend / total_conv if total_conv > 0 else None,
            "dampening": dampening,
        }

    if not channels:
        print("No channels with spend > 0.", file=sys.stderr)
        return 1

    # Separate locked from optimizable
    optimizable = {ch: d for ch, d in channels.items() if ch not in locked}
    locked_spend = sum(locked.values())
    optimizable_target = args.target_spend - locked_spend

    if optimizable_target <= 0:
        print("Target spend is fully consumed by locked channels.", file=sys.stderr)
        return 1

    # Reallocate: weight by ROAS × dampening, with shift caps
    if args.metric == "roas":
        weights = {ch: d["roas"] * d["dampening"] for ch, d in optimizable.items()}
    else:  # cpa — invert: lower CPA = better
        weights = {ch: (1 / d["cpa"]) * d["dampening"] if d["cpa"] and d["cpa"] > 0 else 0 for ch, d in optimizable.items()}

    total_weight = sum(weights.values())
    if total_weight <= 0:
        print("All optimizable channels have zero weight.", file=sys.stderr)
        return 1

    # Initial allocation by weight
    proposed = {ch: optimizable_target * (w / total_weight) for ch, w in weights.items()}

    # Apply shift caps
    max_shift = args.max_shift_pct / 100
    capped = {}
    leftover = 0
    for ch, prop in proposed.items():
        current = optimizable[ch]["spend"]
        upper = current * (1 + max_shift)
        lower = current * (1 - max_shift)
        if prop > upper:
            leftover += prop - upper
            capped[ch] = upper
        elif prop < lower:
            leftover -= lower - prop
            capped[ch] = lower
        else:
            capped[ch] = prop

    # Distribute leftover proportionally to weight (capped)
    if abs(leftover) > 1:
        # Simple redistribution to channels that aren't already at their cap
        eligible = [ch for ch in capped if capped[ch] < optimizable[ch]["spend"] * (1 + max_shift)]
        if eligible:
            per_channel = leftover / len(eligible)
            for ch in eligible:
                capped[ch] = max(optimizable[ch]["spend"] * (1 - max_shift),
                                min(optimizable[ch]["spend"] * (1 + max_shift), capped[ch] + per_channel))

    # Build output
    out_rows = []
    for ch in sorted(channels.keys(), key=lambda c: -channels[c]["spend"]):
        d = channels[ch]
        is_locked = ch in locked
        proposed_spend = locked[ch] if is_locked else capped.get(ch, d["spend"])
        shift_pct = (proposed_spend - d["spend"]) / d["spend"] * 100 if d["spend"] > 0 else 0
        # Project revenue assuming dampened ROAS holds for the proposed spend
        projected_rev = proposed_spend * d["roas"] * d["dampening"]

        out_rows.append({
            "channel": ch,
            "locked": "yes" if is_locked else "",
            "current_spend": round(d["spend"], 2),
            "proposed_spend": round(proposed_spend, 2),
            "shift_pct": round(shift_pct, 1),
            "current_roas": round(d["roas"], 2),
            "dampening_factor": round(d["dampening"], 2),
            "projected_revenue": round(projected_rev, 2),
        })

    # Totals row
    total_current_spend = sum(d["spend"] for d in channels.values())
    total_proposed_spend = sum(r["proposed_spend"] for r in out_rows)
    total_current_revenue = sum(d["revenue"] for d in channels.values())
    total_projected_revenue = sum(r["projected_revenue"] for r in out_rows)

    fields = ["channel", "locked", "current_spend", "proposed_spend", "shift_pct",
              "current_roas", "dampening_factor", "projected_revenue"]

    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    writer = csv.DictWriter(out_stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out_rows)
    out_stream.write("\n--- Summary ---\n")
    out_stream.write(f"Current total spend:       ${total_current_spend:,.2f}\n")
    out_stream.write(f"Proposed total spend:      ${total_proposed_spend:,.2f}\n")
    out_stream.write(f"Current total revenue:     ${total_current_revenue:,.2f}\n")
    out_stream.write(f"Projected total revenue:   ${total_projected_revenue:,.2f}\n")
    proj_lift = (total_projected_revenue - total_current_revenue) / total_current_revenue * 100 if total_current_revenue > 0 else 0
    out_stream.write(f"Projected revenue lift:    {proj_lift:+.1f}%\n\n")
    out_stream.write("Assumptions: ROAS holds (with dampening) at proposed spend levels. Recommend 2-week checkpoint to verify the model.\n")

    if close_after:
        out_stream.close()
        print(f"Wrote plan to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
