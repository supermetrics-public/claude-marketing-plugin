#!/usr/bin/env python3
"""
Newsletter performance analyzer.

Expected CSV columns:
    - campaign_name
    - send_date
    - subject_line
    - segment (optional)
    - content_type (optional: newsletter, promotional, educational, product)
    - recipients
    - opens
    - clicks
    - unsubscribes
    - conversions (optional)
    - revenue (optional)

Usage:
    python newsletter_performance.py campaigns.csv --output review.csv

Analyzes performance by content type, subject line patterns, and flags
campaigns with anomalously high unsubscribe rates.
"""

import argparse
import sys
import csv
from collections import defaultdict
from statistics import mean


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Email campaign CSV")
    p.add_argument("--output", default="-")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def classify_subject(subject):
    """Simple subject line classification."""
    s = subject.strip()
    is_question = "?" in s
    has_number = any(c.isdigit() for c in s)
    word_count = len(s.split())
    has_emoji = any(ord(c) > 0x1F000 for c in s)

    if word_count <= 4:
        length_class = "short"
    elif word_count <= 8:
        length_class = "medium"
    else:
        length_class = "long"

    features = []
    if is_question:
        features.append("question")
    if has_number:
        features.append("has_number")
    if has_emoji:
        features.append("has_emoji")
    return length_class, features


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data.", file=sys.stderr)
        return 1

    campaigns = []
    for r in rows:
        recipients = to_float(r.get("recipients") or r.get("recipients_count"))
        opens = to_float(r.get("opens"))
        clicks = to_float(r.get("clicks"))
        unsubs = to_float(r.get("unsubscribes"))
        conv = to_float(r.get("conversions"))
        rev = to_float(r.get("revenue"))

        subject = r.get("subject_line", "")
        length_class, features = classify_subject(subject)

        open_rate = opens / recipients * 100 if recipients > 0 else 0
        ctr = clicks / recipients * 100 if recipients > 0 else 0
        click_to_open = clicks / opens * 100 if opens > 0 else 0
        unsub_rate = unsubs / recipients * 100 if recipients > 0 else 0

        campaigns.append({
            "campaign_name": r.get("campaign_name", ""),
            "send_date": r.get("send_date", ""),
            "subject_line": subject,
            "subject_length": length_class,
            "subject_features": "|".join(features),
            "content_type": r.get("content_type", ""),
            "segment": r.get("segment", ""),
            "recipients": int(recipients),
            "open_rate_pct": round(open_rate, 1),
            "ctr_pct": round(ctr, 2),
            "click_to_open_pct": round(click_to_open, 1),
            "unsub_rate_pct": round(unsub_rate, 3),
            "conversions": int(conv),
            "revenue": round(rev, 2),
        })

    # Flag anomalously high unsub
    unsub_rates = [c["unsub_rate_pct"] for c in campaigns if c["unsub_rate_pct"] > 0]
    if unsub_rates:
        avg_unsub = mean(unsub_rates)
        unsub_threshold = avg_unsub * 2
    else:
        unsub_threshold = 0.5

    for c in campaigns:
        c["flag"] = "high_unsub" if c["unsub_rate_pct"] > unsub_threshold else ""

    # Sort by send_date descending
    campaigns.sort(key=lambda c: c["send_date"], reverse=True)

    # Print summary stats
    print(f"--- Newsletter performance summary ---", file=sys.stderr)
    print(f"Campaigns analyzed: {len(campaigns)}", file=sys.stderr)
    if campaigns:
        print(f"Avg open rate: {mean(c['open_rate_pct'] for c in campaigns):.1f}%", file=sys.stderr)
        print(f"Avg CTR: {mean(c['ctr_pct'] for c in campaigns):.2f}%", file=sys.stderr)
        print(f"Avg unsubscribe rate: {mean(c['unsub_rate_pct'] for c in campaigns):.3f}%", file=sys.stderr)

    # Aggregate by content_type
    by_type = defaultdict(lambda: {"n": 0, "open_sum": 0, "ctr_sum": 0, "unsub_sum": 0})
    for c in campaigns:
        ct = c["content_type"] or "(untagged)"
        by_type[ct]["n"] += 1
        by_type[ct]["open_sum"] += c["open_rate_pct"]
        by_type[ct]["ctr_sum"] += c["ctr_pct"]
        by_type[ct]["unsub_sum"] += c["unsub_rate_pct"]

    print(f"\n--- By content type ---", file=sys.stderr)
    for ct, d in by_type.items():
        n = d["n"]
        print(f"  {ct}: {n} campaigns, avg open {d['open_sum']/n:.1f}%, avg CTR {d['ctr_sum']/n:.2f}%, avg unsub {d['unsub_sum']/n:.3f}%", file=sys.stderr)

    fields = ["send_date", "campaign_name", "flag", "subject_line", "subject_length", "subject_features",
              "content_type", "segment", "recipients", "open_rate_pct", "ctr_pct", "click_to_open_pct",
              "unsub_rate_pct", "conversions", "revenue"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(campaigns)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(campaigns)
        print(f"\nWrote {len(campaigns)} campaigns to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
