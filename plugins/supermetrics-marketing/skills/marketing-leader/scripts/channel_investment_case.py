#!/usr/bin/env python3
"""
Channel saturation analyzer for new-channel investment cases.

Audits current channels for saturation signals — rising CPM, climbing
frequency, declining CTR at flat/rising CPCs — to inform whether a new
channel is worth testing.

Expected CSV columns (monthly granularity, 6+ months):
    - channel
    - month (YYYY-MM)
    - impressions
    - clicks
    - cost (or spend)
    - frequency (optional)

Usage:
    python channel_investment_case.py monthly.csv --output saturation.csv

For each channel, the script computes:
    - CPM trend (% change from earliest to latest month)
    - CTR trend
    - CPC trend
    - Frequency trend (if available)
    - A composite saturation score (0-100, higher = more saturated)

Channels with saturation score > 60 are flagged as candidates for
reallocation toward a new channel.
"""

import argparse
import sys
import csv
from collections import defaultdict
from statistics import mean


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Monthly channel-level CSV")
    p.add_argument("--channel-col", default="channel")
    p.add_argument("--month-col", default="month")
    p.add_argument("--output", default="-")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def pct_change(curr, prev):
    if prev == 0:
        return 0
    return (curr - prev) / prev * 100


def saturation_score(cpm_trend, ctr_trend, cpc_trend, freq_trend):
    """Compose a 0-100 saturation score from individual metric trends."""
    score = 50  # neutral starting point
    # Rising CPM = saturation signal
    if cpm_trend > 15:
        score += 15
    elif cpm_trend > 5:
        score += 8
    elif cpm_trend < -10:
        score -= 8
    # Declining CTR = saturation signal
    if ctr_trend < -15:
        score += 15
    elif ctr_trend < -5:
        score += 8
    elif ctr_trend > 10:
        score -= 8
    # Rising CPC = saturation signal
    if cpc_trend > 20:
        score += 10
    elif cpc_trend > 10:
        score += 5
    # Rising frequency = saturation signal
    if freq_trend is not None:
        if freq_trend > 15:
            score += 10
        elif freq_trend > 5:
            score += 5
    return max(0, min(100, score))


def saturation_verdict(score):
    if score >= 70:
        return "saturated"
    if score >= 60:
        return "approaching_saturation"
    if score >= 45:
        return "healthy"
    return "underexplored"


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data.", file=sys.stderr)
        return 1

    # Aggregate per (channel, month)
    data = defaultdict(lambda: defaultdict(lambda: {"impressions": 0.0, "clicks": 0.0, "cost": 0.0, "frequency_sum": 0.0, "frequency_n": 0}))
    for r in rows:
        ch = r.get(args.channel_col, "(unknown)")
        m = r.get(args.month_col, "")
        data[ch][m]["impressions"] += to_float(r.get("impressions"))
        data[ch][m]["clicks"] += to_float(r.get("clicks"))
        data[ch][m]["cost"] += to_float(r.get("cost") or r.get("spend"))
        freq = to_float(r.get("frequency"))
        if freq > 0:
            data[ch][m]["frequency_sum"] += freq
            data[ch][m]["frequency_n"] += 1

    out_rows = []
    for ch, months in data.items():
        sorted_months = sorted(months.keys())
        if len(sorted_months) < 3:
            continue

        # Compute monthly metrics
        monthly_cpms, monthly_ctrs, monthly_cpcs, monthly_freqs = [], [], [], []
        for m in sorted_months:
            d = months[m]
            cpm = (d["cost"] / d["impressions"] * 1000) if d["impressions"] > 0 else 0
            ctr = (d["clicks"] / d["impressions"] * 100) if d["impressions"] > 0 else 0
            cpc = (d["cost"] / d["clicks"]) if d["clicks"] > 0 else 0
            freq = (d["frequency_sum"] / d["frequency_n"]) if d["frequency_n"] > 0 else None
            monthly_cpms.append(cpm)
            monthly_ctrs.append(ctr)
            monthly_cpcs.append(cpc)
            monthly_freqs.append(freq)

        # Trends from first third to last third
        third = max(1, len(sorted_months) // 3)
        cpm_trend = pct_change(mean(monthly_cpms[-third:]), mean(monthly_cpms[:third]))
        ctr_trend = pct_change(mean(monthly_ctrs[-third:]), mean(monthly_ctrs[:third]))
        cpc_trend = pct_change(mean(monthly_cpcs[-third:]), mean(monthly_cpcs[:third]))

        freq_vals = [f for f in monthly_freqs if f is not None]
        if len(freq_vals) >= 3:
            freq_trend = pct_change(mean(freq_vals[-third:]), mean(freq_vals[:third]))
        else:
            freq_trend = None

        score = saturation_score(cpm_trend, ctr_trend, cpc_trend, freq_trend)
        verdict = saturation_verdict(score)

        total_spend = sum(months[m]["cost"] for m in sorted_months)

        out_rows.append({
            "channel": ch,
            "verdict": verdict,
            "saturation_score": score,
            "cpm_trend_pct": round(cpm_trend, 1),
            "ctr_trend_pct": round(ctr_trend, 1),
            "cpc_trend_pct": round(cpc_trend, 1),
            "frequency_trend_pct": round(freq_trend, 1) if freq_trend is not None else "n/a",
            "total_spend": round(total_spend, 2),
            "months_observed": len(sorted_months),
        })

    out_rows.sort(key=lambda r: -r["saturation_score"])

    fields = ["channel", "verdict", "saturation_score", "cpm_trend_pct", "ctr_trend_pct",
              "cpc_trend_pct", "frequency_trend_pct", "total_spend", "months_observed"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        n_saturated = sum(1 for r in out_rows if r["verdict"] in ("saturated", "approaching_saturation"))
        print(f"Wrote {len(out_rows)} channels. {n_saturated} showing saturation signals.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
