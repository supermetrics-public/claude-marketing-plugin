#!/usr/bin/env python3
"""
AOV and basket composition analyzer.

Expected CSV columns (one row per order):
    - order_id
    - order_date
    - channel (optional)
    - order_value
    - item_count

Usage:
    python aov_analyzer.py orders.csv \
        --free-shipping-thresholds 50,75,100 \
        --output aov.csv
"""

import argparse
import sys
import csv
from collections import defaultdict
from statistics import median


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Order-level CSV")
    p.add_argument("--free-shipping-thresholds", default="50,75,100", help="Comma-separated dollar thresholds")
    p.add_argument("--proximity-window", type=float, default=10.0, help="Dollar window below threshold to count as 'just under' (default: 10)")
    p.add_argument("--output", default="-")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def percentile(values, p):
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def main():
    args = parse_args()
    thresholds = [to_float(t) for t in args.free_shipping_thresholds.split(",") if t.strip()]
    window = args.proximity_window

    by_channel = defaultdict(lambda: {"values": [], "items": []})
    all_values = []
    all_items = []

    with open(args.input, newline="") as f:
        for r in csv.DictReader(f):
            channel = r.get("channel") or "(unknown)"
            value = to_float(r.get("order_value") or r.get("revenue"))
            items = to_float(r.get("item_count") or r.get("items"))
            if value <= 0:
                continue
            by_channel[channel]["values"].append(value)
            if items > 0:
                by_channel[channel]["items"].append(items)
            all_values.append(value)
            if items > 0:
                all_items.append(items)

    if not all_values:
        print("No valid orders.", file=sys.stderr)
        return 1

    # Per channel
    out_rows = []
    channels = list(by_channel.keys()) + ["TOTAL"]
    for ch in channels:
        if ch == "TOTAL":
            values = all_values
            items = all_items
        else:
            values = by_channel[ch]["values"]
            items = by_channel[ch]["items"]

        if not values:
            continue
        aov = sum(values) / len(values)
        med = median(values)
        p25 = percentile(values, 25)
        p75 = percentile(values, 75)
        p90 = percentile(values, 90)
        avg_items = sum(items) / len(items) if items else None

        # Item-count distribution
        single_item = sum(1 for i in items if i == 1) / len(items) * 100 if items else None
        two_items = sum(1 for i in items if i == 2) / len(items) * 100 if items else None
        three_plus = sum(1 for i in items if i >= 3) / len(items) * 100 if items else None

        row = {
            "channel": ch,
            "orders": len(values),
            "total_revenue": round(sum(values), 2),
            "AOV": round(aov, 2),
            "median_order_value": round(med, 2),
            "p25": round(p25, 2),
            "p75": round(p75, 2),
            "p90": round(p90, 2),
            "avg_items_per_order": round(avg_items, 2) if avg_items else "n/a",
            "single_item_orders_pct": round(single_item, 1) if single_item is not None else "n/a",
            "two_item_orders_pct": round(two_items, 1) if two_items is not None else "n/a",
            "three_plus_orders_pct": round(three_plus, 1) if three_plus is not None else "n/a",
        }
        for t in thresholds:
            just_under = sum(1 for v in values if t - window <= v < t) / len(values) * 100
            above = sum(1 for v in values if v >= t) / len(values) * 100
            row[f"pct_just_under_${int(t)}"] = round(just_under, 1)
            row[f"pct_at_or_above_${int(t)}"] = round(above, 1)
        out_rows.append(row)

    fields = list(out_rows[0].keys()) if out_rows else []

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote AOV breakdown for {len(out_rows)} channels (incl. TOTAL) to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
