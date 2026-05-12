#!/usr/bin/env python3
"""
Daily morning standup check.

Compares yesterday's performance against a trailing baseline per channel
and per campaign. Flags anomalies on spend, CPA, conversions, and ROAS.

Expected CSV columns:
    - channel (or platform)
    - campaign_name (optional — if present, results are also per-campaign)
    - date (daily)
    - spend
    - conversions
    - revenue (optional, for ROAS)

Usage:
    python daily_check.py input.csv \
        --spend-threshold 25 \
        --cpa-threshold 30 \
        --roas-threshold 20 \
        --output check.csv

The script:
    1. Identifies the most recent date in the data (yesterday)
    2. Uses the prior 7 days as the baseline
    3. Computes percent deviation per metric per channel
    4. Flags any metric outside its configured threshold

Severity levels:
    - "ok"      — all metrics within ±10% of baseline
    - "watch"   — at least one metric ±10–25%
    - "act"     — at least one metric beyond threshold
"""

import argparse
import sys
import csv
from collections import defaultdict
from datetime import datetime, timedelta


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Daily channel-level CSV")
    p.add_argument("--channel-col", default="channel", help="Channel column (default: channel)")
    p.add_argument("--date-col", default="date", help="Date column (default: date)")
    p.add_argument("--baseline-days", type=int, default=7, help="Trailing baseline window (default: 7)")
    p.add_argument("--spend-threshold", type=float, default=25.0, help="Spend deviation %% to flag (default: 25)")
    p.add_argument("--cpa-threshold", type=float, default=30.0, help="CPA deviation %% to flag (default: 30)")
    p.add_argument("--roas-threshold", type=float, default=20.0, help="ROAS deviation %% to flag (default: 20)")
    p.add_argument("--output", default="-", help="Output CSV (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date: {s}")


def pct_change(curr, base):
    if base == 0:
        return None
    return (curr - base) / base * 100


def severity(deviations, thresholds):
    """Return severity level based on the worst deviation."""
    worst = 0
    for metric, dev in deviations.items():
        if dev is None:
            continue
        abs_dev = abs(dev)
        thresh = thresholds.get(metric, 25)
        if abs_dev >= thresh:
            return "act"
        if abs_dev > worst:
            worst = abs_dev
    if worst >= 10:
        return "watch"
    return "ok"


def main():
    args = parse_args()
    thresholds = {
        "spend": args.spend_threshold,
        "cpa": args.cpa_threshold,
        "roas": args.roas_threshold,
    }

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    parsed = []
    for r in rows:
        try:
            d = parse_date(r[args.date_col])
        except (ValueError, KeyError):
            continue
        parsed.append({
            "channel": r.get(args.channel_col, "(unknown)"),
            "campaign": r.get("campaign_name", ""),
            "date": d,
            "spend": to_float(r.get("spend") or r.get("cost")),
            "conversions": to_float(r.get("conversions")),
            "revenue": to_float(r.get("revenue") or r.get("conversion_value")),
        })

    if not parsed:
        print("No valid dated rows.", file=sys.stderr)
        return 1

    yesterday = max(r["date"] for r in parsed)
    baseline_start = yesterday - timedelta(days=args.baseline_days)
    baseline_end = yesterday - timedelta(days=1)

    # Aggregate per channel
    channels = defaultdict(lambda: {
        "yesterday": {"spend": 0.0, "conversions": 0.0, "revenue": 0.0},
        "baseline": {"spend": 0.0, "conversions": 0.0, "revenue": 0.0, "days": set()},
    })

    for r in parsed:
        ch = channels[r["channel"]]
        if r["date"] == yesterday:
            ch["yesterday"]["spend"] += r["spend"]
            ch["yesterday"]["conversions"] += r["conversions"]
            ch["yesterday"]["revenue"] += r["revenue"]
        elif baseline_start <= r["date"] <= baseline_end:
            ch["baseline"]["spend"] += r["spend"]
            ch["baseline"]["conversions"] += r["conversions"]
            ch["baseline"]["revenue"] += r["revenue"]
            ch["baseline"]["days"].add(r["date"])

    out_rows = []
    for name, d in channels.items():
        y = d["yesterday"]
        b = d["baseline"]
        n_days = len(b["days"]) or 1

        baseline_spend = b["spend"] / n_days
        baseline_conv = b["conversions"] / n_days
        baseline_rev = b["revenue"] / n_days
        baseline_cpa = b["spend"] / b["conversions"] if b["conversions"] > 0 else None
        baseline_roas = b["revenue"] / b["spend"] if b["spend"] > 0 else None

        y_cpa = y["spend"] / y["conversions"] if y["conversions"] > 0 else None
        y_roas = y["revenue"] / y["spend"] if y["spend"] > 0 else None

        deviations = {
            "spend": pct_change(y["spend"], baseline_spend),
            "conversions": pct_change(y["conversions"], baseline_conv),
            "cpa": pct_change(y_cpa, baseline_cpa) if y_cpa is not None and baseline_cpa is not None else None,
            "roas": pct_change(y_roas, baseline_roas) if y_roas is not None and baseline_roas is not None else None,
        }

        # Special case: zero conversions when baseline had conversions
        zero_conv_flag = ""
        if y["conversions"] == 0 and baseline_conv > 1:
            zero_conv_flag = "ZERO conversions — check tracking"

        sev = severity(deviations, thresholds)
        if zero_conv_flag:
            sev = "act"

        out_rows.append({
            "channel": name,
            "severity": sev,
            "spend_yesterday": round(y["spend"], 2),
            "spend_baseline_daily_avg": round(baseline_spend, 2),
            "spend_dev_pct": round(deviations["spend"], 1) if deviations["spend"] is not None else "n/a",
            "conversions_yesterday": int(y["conversions"]),
            "conversions_baseline_avg": round(baseline_conv, 1),
            "conversions_dev_pct": round(deviations["conversions"], 1) if deviations["conversions"] is not None else "n/a",
            "cpa_yesterday": round(y_cpa, 2) if y_cpa is not None else "n/a",
            "cpa_baseline": round(baseline_cpa, 2) if baseline_cpa is not None else "n/a",
            "cpa_dev_pct": round(deviations["cpa"], 1) if deviations["cpa"] is not None else "n/a",
            "roas_yesterday": round(y_roas, 2) if y_roas is not None else "n/a",
            "roas_baseline": round(baseline_roas, 2) if baseline_roas is not None else "n/a",
            "roas_dev_pct": round(deviations["roas"], 1) if deviations["roas"] is not None else "n/a",
            "note": zero_conv_flag,
        })

    severity_order = {"act": 0, "watch": 1, "ok": 2}
    out_rows.sort(key=lambda r: (severity_order.get(r["severity"], 9), r["channel"]))

    fields = ["severity", "channel", "spend_yesterday", "spend_baseline_daily_avg", "spend_dev_pct",
              "conversions_yesterday", "conversions_baseline_avg", "conversions_dev_pct",
              "cpa_yesterday", "cpa_baseline", "cpa_dev_pct",
              "roas_yesterday", "roas_baseline", "roas_dev_pct", "note"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        n_act = sum(1 for r in out_rows if r["severity"] == "act")
        n_watch = sum(1 for r in out_rows if r["severity"] == "watch")
        print(f"Wrote {len(out_rows)} channels to {args.output} — {n_act} need action, {n_watch} on watch.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
