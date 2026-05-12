#!/usr/bin/env python3
"""
Promotional campaign anomaly detector.

Flags ad sets where yesterday's cost-per-purchase exceeded a configurable
multiple (default 3x) of the rolling N-day average. Identifies the
specific ad sets responsible and surfaces candidate causes (tracking
failure vs. real performance issue).

Expected CSV columns:
    - ad_set_name (or ad_set or adset)
    - date (daily)
    - spend (or cost)
    - purchases (or conversions)
    - revenue (optional, for ROAS-based detection)

Usage:
    python anomaly_detector.py input.csv \
        --multiplier 3.0 \
        --baseline-days 6 \
        --metric cost_per_purchase \
        --output anomalies.csv

The script:
    1. Identifies the most recent date in the data (the "spike day")
    2. Computes the trailing N-day average per ad set
    3. Flags ad sets where spike-day metric exceeds multiplier × baseline
    4. Surfaces candidate causes for each flag:
       - "Purchases dropped to zero" → suspected tracking failure
       - "Spend up substantially, purchases flat" → likely real performance issue
       - "Both spend and purchases moved" → ambiguous, needs human review
"""

import argparse
import sys
import csv
from collections import defaultdict
from datetime import datetime, timedelta


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Daily ad set-level CSV")
    p.add_argument("--ad-set-col", default="ad_set_name", help="Ad set column (default: ad_set_name)")
    p.add_argument("--date-col", default="date", help="Date column (default: date)")
    p.add_argument("--multiplier", type=float, default=3.0, help="Anomaly threshold multiplier (default: 3.0)")
    p.add_argument("--baseline-days", type=int, default=6, help="Rolling baseline window in days (default: 6)")
    p.add_argument("--metric", default="cost_per_purchase", choices=["cost_per_purchase", "roas"],
                   help="Metric to monitor (default: cost_per_purchase)")
    p.add_argument("--min-purchases", type=int, default=3, help="Minimum baseline purchases to consider an ad set (default: 3)")
    p.add_argument("--output", default="-", help="Output path (default: stdout)")
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


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    ad_set_col = args.ad_set_col
    if ad_set_col not in rows[0]:
        for c in ("ad_set_name", "ad_set", "adset", "adset_name"):
            if c in rows[0]:
                ad_set_col = c
                break

    parsed = []
    for r in rows:
        try:
            d = parse_date(r[args.date_col])
        except (ValueError, KeyError):
            continue
        parsed.append({
            "ad_set": r.get(ad_set_col, "(unknown)"),
            "date": d,
            "spend": to_float(r.get("spend") or r.get("cost")),
            "purchases": to_float(r.get("purchases") or r.get("conversions")),
            "revenue": to_float(r.get("revenue") or r.get("conversion_value")),
        })

    if not parsed:
        print("No valid dated rows.", file=sys.stderr)
        return 1

    most_recent = max(r["date"] for r in parsed)
    baseline_end = most_recent - timedelta(days=1)
    baseline_start = baseline_end - timedelta(days=args.baseline_days - 1)

    # Aggregate per ad set
    ad_sets = defaultdict(lambda: {
        "spike": {"spend": 0.0, "purchases": 0.0, "revenue": 0.0},
        "baseline": {"spend": 0.0, "purchases": 0.0, "revenue": 0.0, "days": set()},
    })
    for r in parsed:
        ad = ad_sets[r["ad_set"]]
        if r["date"] == most_recent:
            ad["spike"]["spend"] += r["spend"]
            ad["spike"]["purchases"] += r["purchases"]
            ad["spike"]["revenue"] += r["revenue"]
        elif baseline_start <= r["date"] <= baseline_end:
            ad["baseline"]["spend"] += r["spend"]
            ad["baseline"]["purchases"] += r["purchases"]
            ad["baseline"]["revenue"] += r["revenue"]
            ad["baseline"]["days"].add(r["date"])

    # Compute metric and flag anomalies
    anomalies = []
    for ad_name, d in ad_sets.items():
        sp = d["spike"]
        bs = d["baseline"]
        n_baseline_days = len(bs["days"])

        if n_baseline_days == 0 or bs["purchases"] < args.min_purchases:
            continue  # Not enough baseline data

        # Baseline avg cost per purchase (or ROAS)
        baseline_avg_cpp = bs["spend"] / bs["purchases"] if bs["purchases"] > 0 else None
        baseline_avg_roas = bs["revenue"] / bs["spend"] if bs["spend"] > 0 else None

        spike_cpp = sp["spend"] / sp["purchases"] if sp["purchases"] > 0 else float("inf")
        spike_roas = sp["revenue"] / sp["spend"] if sp["spend"] > 0 else 0

        if args.metric == "cost_per_purchase":
            if baseline_avg_cpp is None or baseline_avg_cpp == 0:
                continue
            if spike_cpp == float("inf"):
                # Zero purchases yesterday — strong signal but suspect tracking
                ratio = float("inf")
                flagged = sp["spend"] > 0  # only flag if spend actually happened
            else:
                ratio = spike_cpp / baseline_avg_cpp
                flagged = ratio >= args.multiplier
            spike_metric = spike_cpp
            baseline_metric = baseline_avg_cpp
        else:  # roas
            if baseline_avg_roas is None or baseline_avg_roas == 0:
                continue
            ratio = baseline_avg_roas / spike_roas if spike_roas > 0 else float("inf")
            flagged = ratio >= args.multiplier
            spike_metric = spike_roas
            baseline_metric = baseline_avg_roas

        if not flagged:
            continue

        # Candidate cause
        baseline_daily_spend = bs["spend"] / n_baseline_days
        baseline_daily_purchases = bs["purchases"] / n_baseline_days
        spend_change = (sp["spend"] - baseline_daily_spend) / baseline_daily_spend if baseline_daily_spend > 0 else None
        purchase_change = (sp["purchases"] - baseline_daily_purchases) / baseline_daily_purchases if baseline_daily_purchases > 0 else None

        if sp["purchases"] == 0 and sp["spend"] > 0:
            cause = "Likely tracking failure (zero purchases logged despite spend)"
        elif spend_change is not None and purchase_change is not None and spend_change > 0.2 and abs(purchase_change) < 0.2:
            cause = "Spend up significantly, purchases flat — likely real performance issue"
        elif purchase_change is not None and purchase_change < -0.5:
            cause = "Purchases dropped >50% — possible tracking issue or audience saturation"
        else:
            cause = "Mixed signal — needs human review"

        anomalies.append({
            "ad_set": ad_name,
            "spike_date": str(most_recent),
            "spike_spend": round(sp["spend"], 2),
            "spike_purchases": int(sp["purchases"]),
            f"spike_{args.metric}": round(spike_metric, 2) if spike_metric != float("inf") else "n/a",
            f"baseline_{args.metric}": round(baseline_metric, 2),
            "ratio": round(ratio, 2) if ratio != float("inf") else "n/a (zero purchases)",
            "baseline_days_observed": n_baseline_days,
            "candidate_cause": cause,
        })

    if not anomalies:
        msg = f"No anomalies detected with current thresholds (multiplier: {args.multiplier}x, baseline: {args.baseline_days} days)."
        if args.output == "-":
            print(msg)
        else:
            with open(args.output, "w") as f:
                f.write(msg + "\n")
            print(msg, file=sys.stderr)
        return 0

    # Sort by ratio descending (worst first)
    anomalies.sort(key=lambda r: -1 * (r["ratio"] if isinstance(r["ratio"], (int, float)) else float("inf")))

    fields = ["ad_set", "spike_date", "ratio", f"spike_{args.metric}", f"baseline_{args.metric}",
              "spike_spend", "spike_purchases", "baseline_days_observed", "candidate_cause"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(anomalies)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(anomalies)
        print(f"Flagged {len(anomalies)} ad sets as anomalous on {most_recent}.", file=sys.stderr)
        print(f"Before alerting the team: verify the spike is real, not a tracking issue. The 'candidate_cause' column flags the most likely explanation per ad set.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
