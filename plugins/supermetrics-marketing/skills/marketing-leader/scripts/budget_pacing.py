#!/usr/bin/env python3
"""
Budget pacing and forecasting helper.

Given month-to-date daily spend and conversion data per channel, projects
month-end totals based on the current run rate, and flags channels pacing
more than threshold% off their monthly budget.

Expected CSV columns:
    - channel (or platform)
    - date (daily)
    - spend
    - conversions (optional but recommended)

Budget targets are passed via --budgets as a comma-separated channel:amount
list, e.g.:  --budgets "Google Ads:50000,Facebook Ads:30000,LinkedIn Ads:20000"

Usage:
    python budget_pacing.py mtd.csv \
        --budgets "Google Ads:50000,Facebook Ads:30000" \
        --month-end 2026-05-31 \
        --threshold 15 \
        --output pacing.csv

If --month-end is omitted, the script uses the last day of the current
calendar month inferred from the most recent date in the data.

Optional: --freeze-from DATE freezes the daily run rate at the average
through that date, simulating "what if we hold spend flat from here?"
"""

import argparse
import sys
import csv
from collections import defaultdict
from datetime import date, datetime, timedelta
import calendar


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Daily channel-level CSV")
    p.add_argument("--channel-col", default="channel", help="Channel column (default: channel)")
    p.add_argument("--date-col", default="date", help="Date column (default: date)")
    p.add_argument("--budgets", required=True, help="Channel:budget pairs, comma-separated")
    p.add_argument("--month-end", default=None, help="Month-end date (YYYY-MM-DD); default: last day of month in data")
    p.add_argument("--threshold", type=float, default=15.0, help="Variance threshold percent for flagging (default: 15)")
    p.add_argument("--freeze-from", default=None, help="Optional: freeze run rate from this date (YYYY-MM-DD)")
    p.add_argument("--output", default="-", help="Output CSV path (default: stdout)")
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
    raise ValueError(f"Unrecognized date format: {s}")


def parse_budgets(s):
    out = {}
    for item in s.split(","):
        if ":" not in item:
            continue
        ch, amt = item.rsplit(":", 1)
        out[ch.strip()] = to_float(amt)
    return out


def main():
    args = parse_args()
    budgets = parse_budgets(args.budgets)

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    # Parse all rows
    parsed = []
    for r in rows:
        try:
            d = parse_date(r[args.date_col])
        except (ValueError, KeyError):
            continue
        parsed.append({
            "channel": r.get(args.channel_col, "(unknown)"),
            "date": d,
            "spend": to_float(r.get("spend") or r.get("cost")),
            "conversions": to_float(r.get("conversions")),
        })

    if not parsed:
        print("No valid dated rows.", file=sys.stderr)
        return 1

    most_recent = max(r["date"] for r in parsed)

    if args.month_end:
        month_end = parse_date(args.month_end)
    else:
        last_day = calendar.monthrange(most_recent.year, most_recent.month)[1]
        month_end = date(most_recent.year, most_recent.month, last_day)

    month_start = date(most_recent.year, most_recent.month, 1)
    freeze_from = parse_date(args.freeze_from) if args.freeze_from else None

    # Aggregate per channel
    channels = defaultdict(lambda: {"days": set(), "spend": 0.0, "conversions": 0.0, "spend_freeze": 0.0, "days_freeze": set()})
    for r in parsed:
        if r["date"] < month_start or r["date"] > most_recent:
            continue
        ch = channels[r["channel"]]
        ch["spend"] += r["spend"]
        ch["conversions"] += r["conversions"]
        ch["days"].add(r["date"])
        if freeze_from and r["date"] <= freeze_from:
            ch["spend_freeze"] += r["spend"]
            ch["days_freeze"].add(r["date"])

    days_elapsed = (most_recent - month_start).days + 1
    days_remaining = (month_end - most_recent).days
    days_in_month = (month_end - month_start).days + 1

    out_rows = []
    for ch_name, ch in channels.items():
        actual_days = len(ch["days"]) or days_elapsed
        if freeze_from and ch["days_freeze"]:
            daily_rate_spend = ch["spend_freeze"] / len(ch["days_freeze"])
        else:
            daily_rate_spend = ch["spend"] / actual_days

        daily_rate_conv = ch["conversions"] / actual_days if actual_days > 0 else 0
        projected_spend = ch["spend"] + daily_rate_spend * days_remaining
        projected_conv = ch["conversions"] + daily_rate_conv * days_remaining

        target = budgets.get(ch_name, 0)
        variance_pct = ((projected_spend - target) / target * 100) if target > 0 else None

        if variance_pct is None:
            status = "no target"
        elif abs(variance_pct) <= args.threshold:
            status = "on track"
        elif variance_pct > 0:
            status = "overspend"
        else:
            status = "underspend"

        out_rows.append({
            "channel": ch_name,
            "mtd_spend": round(ch["spend"], 2),
            "mtd_conversions": int(ch["conversions"]),
            "daily_run_rate": round(daily_rate_spend, 2),
            "projected_month_end_spend": round(projected_spend, 2),
            "projected_month_end_conversions": int(projected_conv),
            "monthly_target": round(target, 2) if target else "n/a",
            "variance_pct": round(variance_pct, 1) if variance_pct is not None else "n/a",
            "status": status,
        })

    # Sort: flagged first (overspend, underspend), then alphabetical
    status_order = {"overspend": 0, "underspend": 1, "on track": 2, "no target": 3}
    out_rows.sort(key=lambda r: (status_order.get(r["status"], 9), r["channel"]))

    fields = ["channel", "status", "mtd_spend", "daily_run_rate", "projected_month_end_spend",
              "monthly_target", "variance_pct", "mtd_conversions", "projected_month_end_conversions"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        flagged = sum(1 for r in out_rows if r["status"] in ("overspend", "underspend"))
        print(f"Wrote {len(out_rows)} channels to {args.output} ({flagged} flagged).", file=sys.stderr)
        print(f"Days elapsed: {days_elapsed}, days remaining: {days_remaining}, days in month: {days_in_month}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
