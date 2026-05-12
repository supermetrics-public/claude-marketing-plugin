#!/usr/bin/env python3
"""
SEO content audit — classify pages as growing, decaying, stuck, etc.

Expected CSV columns (monthly granularity, 6+ months):
    - page (URL or page identifier)
    - month (YYYY-MM)
    - impressions
    - clicks
    - average_position
    - sessions (optional, from GA4)
    - engaged_sessions (optional)
    - conversions (optional)

Usage:
    python seo_audit.py monthly.csv --output audit.csv

The script classifies each page based on impressions and clicks trends
over the observation period plus current performance metrics.
"""

import argparse
import sys
import csv
from collections import defaultdict
from statistics import mean


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Monthly page-level CSV")
    p.add_argument("--page-col", default="page")
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


def classify(impr_trend, clicks_trend, avg_position, current_clicks):
    """Classify the page into a content-audit bucket."""
    # Page 2-3 stuck (high impressions, position 11-30, low CTR)
    if avg_position > 10 and avg_position <= 30 and current_clicks > 0:
        return "stuck_p2_p3"
    # Decaying: significant click loss
    if clicks_trend < -25:
        return "decaying"
    # Growing
    if clicks_trend > 25 and impr_trend > 15:
        return "growing"
    # Low engagement = underperforming (handled if engaged_sessions available)
    # Default: stable
    return "stable"


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data.", file=sys.stderr)
        return 1

    pages = defaultdict(lambda: defaultdict(lambda: {
        "impressions": 0.0, "clicks": 0.0, "position_sum": 0.0, "position_n": 0,
        "sessions": 0.0, "engaged_sessions": 0.0, "conversions": 0.0
    }))
    for r in rows:
        p = r.get(args.page_col, "")
        m = r.get(args.month_col, "")
        if not p or not m:
            continue
        d = pages[p][m]
        d["impressions"] += to_float(r.get("impressions"))
        d["clicks"] += to_float(r.get("clicks"))
        pos = to_float(r.get("average_position") or r.get("position"))
        if pos > 0:
            d["position_sum"] += pos
            d["position_n"] += 1
        d["sessions"] += to_float(r.get("sessions"))
        d["engaged_sessions"] += to_float(r.get("engaged_sessions"))
        d["conversions"] += to_float(r.get("conversions"))

    out_rows = []
    for page, months in pages.items():
        sorted_months = sorted(months.keys())
        if len(sorted_months) < 3:
            continue
        third = max(1, len(sorted_months) // 3)
        early = sorted_months[:third]
        late = sorted_months[-third:]

        early_impr = mean(months[m]["impressions"] for m in early)
        late_impr = mean(months[m]["impressions"] for m in late)
        early_clicks = mean(months[m]["clicks"] for m in early)
        late_clicks = mean(months[m]["clicks"] for m in late)

        impr_trend = pct_change(late_impr, early_impr)
        clicks_trend = pct_change(late_clicks, early_clicks)

        # Recent monthly position
        recent_pos_sum = sum(months[m]["position_sum"] for m in late)
        recent_pos_n = sum(months[m]["position_n"] for m in late)
        avg_position = recent_pos_sum / recent_pos_n if recent_pos_n > 0 else 0

        # Engagement quality
        total_sessions = sum(months[m]["sessions"] for m in sorted_months)
        total_engaged = sum(months[m]["engaged_sessions"] for m in sorted_months)
        engagement_rate = (total_engaged / total_sessions) if total_sessions > 0 else None

        classification = classify(impr_trend, clicks_trend, avg_position, late_clicks)
        # Override for underperforming engagement
        if classification == "stable" and engagement_rate is not None and engagement_rate < 0.3 and total_sessions > 500:
            classification = "underperforming"

        # Priority for the audit: decaying high-traffic pages first
        if classification == "decaying":
            priority = 1
        elif classification == "stuck_p2_p3":
            priority = 2
        elif classification == "underperforming":
            priority = 3
        elif classification == "growing":
            priority = 4
        else:
            priority = 5

        out_rows.append({
            "page": page,
            "classification": classification,
            "priority": priority,
            "recent_monthly_clicks": round(late_clicks, 1),
            "clicks_trend_pct": round(clicks_trend, 1),
            "impr_trend_pct": round(impr_trend, 1),
            "current_avg_position": round(avg_position, 1),
            "engagement_rate_pct": round(engagement_rate * 100, 1) if engagement_rate is not None else "n/a",
            "total_sessions": int(total_sessions),
            "total_conversions": int(sum(months[m]["conversions"] for m in sorted_months)),
        })

    out_rows.sort(key=lambda r: (r["priority"], -r["recent_monthly_clicks"]))

    fields = ["priority", "classification", "page", "recent_monthly_clicks", "clicks_trend_pct",
              "impr_trend_pct", "current_avg_position", "engagement_rate_pct",
              "total_sessions", "total_conversions"]
    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        n_decay = sum(1 for r in out_rows if r["classification"] == "decaying")
        n_stuck = sum(1 for r in out_rows if r["classification"] == "stuck_p2_p3")
        print(f"Wrote {len(out_rows)} pages. {n_decay} decaying, {n_stuck} stuck on page 2-3.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
