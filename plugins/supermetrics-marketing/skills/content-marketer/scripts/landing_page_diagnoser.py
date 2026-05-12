#!/usr/bin/env python3
"""
Landing page diagnoser.

Identifies pages with high traffic but underperforming engagement and
conversion. Sorts by lost-opportunity (traffic volume × conversion gap)
so the highest-impact fixes surface first.

Expected CSV columns (typically from GA4):
    - page_path (or landing_page or page)
    - sessions
    - bounce_rate (as percent, e.g. 73.5)
    - avg_time_on_page (seconds)
    - conversion_rate (as percent, e.g. 0.8) OR conversions

Usage:
    python landing_page_diagnoser.py ga4_pages.csv \
        --bounce-threshold 70 \
        --cvr-threshold 1.0 \
        --min-sessions 500 \
        --target-cvr 2.0 \
        --output fix_list.csv

The "lost opportunity" score: sessions × (target_cvr - actual_cvr).
If a page has 10,000 sessions converting at 0.5% and the target is 2%,
the lost opportunity is 10000 × 1.5% = 150 missed conversions per period.
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="GA4 page-level CSV")
    p.add_argument("--page-col", default="page_path", help="Page identifier column")
    p.add_argument("--bounce-threshold", type=float, default=70.0, help="Bounce rate % above which to flag (default: 70)")
    p.add_argument("--cvr-threshold", type=float, default=1.0, help="Conversion rate % below which to flag (default: 1.0)")
    p.add_argument("--min-sessions", type=int, default=500, help="Minimum sessions to include a page (default: 500)")
    p.add_argument("--target-cvr", type=float, default=2.0, help="Target conversion rate for opportunity scoring (default: 2.0)")
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

    # Detect page column (flexible)
    page_col = args.page_col
    first_row_keys = list(rows[0].keys())
    if page_col not in first_row_keys:
        for candidate in ("page_path", "landing_page", "page", "url", "page_title"):
            if candidate in first_row_keys:
                page_col = candidate
                break

    diagnosed = []
    for r in rows:
        page = r.get(page_col, "(unknown)")
        sessions = to_float(r.get("sessions"))
        bounce = to_float(r.get("bounce_rate"))
        time_on_page = to_float(r.get("avg_time_on_page") or r.get("avg_session_duration") or r.get("engagement_time"))

        # Conversion rate: prefer direct, fall back to computed
        cvr = to_float(r.get("conversion_rate"))
        if cvr == 0:
            conversions = to_float(r.get("conversions"))
            cvr = (conversions / sessions * 100) if sessions > 0 else 0

        if sessions < args.min_sessions:
            continue
        if bounce <= args.bounce_threshold or cvr >= args.cvr_threshold:
            continue

        # Lost opportunity
        cvr_gap = max(args.target_cvr - cvr, 0)
        lost_opportunity = sessions * (cvr_gap / 100)

        diagnosed.append({
            "page": page,
            "sessions": int(sessions),
            "bounce_rate_pct": round(bounce, 1),
            "avg_time_on_page_sec": round(time_on_page, 1),
            "conversion_rate_pct": round(cvr, 2),
            "cvr_gap_pct": round(cvr_gap, 2),
            "lost_opportunity_conversions": round(lost_opportunity, 1),
            "priority": "",
        })

    if not diagnosed:
        print(f"No pages meet the criteria (bounce > {args.bounce_threshold}% AND cvr < {args.cvr_threshold}% AND sessions >= {args.min_sessions}).", file=sys.stderr)
        return 0

    # Sort by lost opportunity descending
    diagnosed.sort(key=lambda r: -r["lost_opportunity_conversions"])

    # Assign priority labels based on quartiles
    n = len(diagnosed)
    for i, r in enumerate(diagnosed):
        if i < n / 4:
            r["priority"] = "high"
        elif i < n / 2:
            r["priority"] = "medium"
        else:
            r["priority"] = "low"

    fields = ["priority", "page", "sessions", "bounce_rate_pct", "avg_time_on_page_sec",
              "conversion_rate_pct", "cvr_gap_pct", "lost_opportunity_conversions"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(diagnosed)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(diagnosed)
        print(f"Wrote {len(diagnosed)} underperforming pages to {args.output}.", file=sys.stderr)
        print(f"Total estimated lost conversions per period: {sum(r['lost_opportunity_conversions'] for r in diagnosed):.0f}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
