#!/usr/bin/env python3
"""
Content gap analyzer.

Identifies keywords where competitors rank but the user doesn't (or
ranks poorly). Filters for relevance and ranks by opportunity size.

Expected CSV columns:
    - keyword
    - monthly_volume
    - user_position (empty or 0 if not ranking)
    - competitor_position (best competitor position; can be one column,
                          or pass multiple "competitor_<name>_position")
    - search_intent (optional: informational, commercial, transactional, navigational)

Usage:
    python content_gap_analyzer.py keywords.csv \
        --min-volume 100 \
        --user-threshold 30 \
        --output gaps.csv

The script finds keywords where:
    - User ranks below user_threshold (default 30) or not at all
    - At least one competitor ranks in top 10
    - Monthly volume >= min_volume
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Keywords CSV")
    p.add_argument("--min-volume", type=int, default=100, help="Minimum monthly volume (default: 100)")
    p.add_argument("--user-threshold", type=int, default=30, help="User position threshold to qualify as gap (default: 30)")
    p.add_argument("--competitor-top", type=int, default=10, help="Competitor must rank in top N (default: 10)")
    p.add_argument("--output", default="-")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def to_int_or_none(v):
    if v is None or v == "":
        return None
    try:
        n = int(float(str(v).replace(",", "")))
        return n if n > 0 else None
    except ValueError:
        return None


def suggest_content_type(intent, volume):
    if intent == "transactional" or intent == "commercial":
        return "landing_page"
    if intent == "informational":
        if volume >= 1000:
            return "pillar_post"
        return "blog_post"
    if intent == "navigational":
        return "brand_page"
    # Heuristic if intent missing
    if volume >= 1000:
        return "long_form_blog"
    return "blog_post"


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data.", file=sys.stderr)
        return 1

    gaps = []
    for r in rows:
        kw = r.get("keyword", "").strip()
        if not kw:
            continue
        volume = to_float(r.get("monthly_volume") or r.get("volume"))
        if volume < args.min_volume:
            continue

        user_pos = to_int_or_none(r.get("user_position"))
        comp_pos = to_int_or_none(r.get("competitor_position") or r.get("best_competitor_position"))

        # If individual competitor columns, find the best
        if comp_pos is None:
            for col, val in r.items():
                if col.startswith("competitor_") and col.endswith("_position"):
                    p = to_int_or_none(val)
                    if p is not None and (comp_pos is None or p < comp_pos):
                        comp_pos = p

        if comp_pos is None or comp_pos > args.competitor_top:
            continue
        # User doesn't rank or ranks worse than threshold
        if user_pos is not None and user_pos <= args.user_threshold:
            continue

        intent = r.get("search_intent", "")
        content_type = suggest_content_type(intent, volume)

        # Opportunity score: volume × (1 if user not ranking, 0.5 if ranking below threshold) × (competitor position bonus)
        if user_pos is None:
            user_factor = 1.0
            user_status = "not_ranking"
        else:
            user_factor = 0.5
            user_status = f"position_{user_pos}"
        comp_bonus = 1 / max(1, comp_pos)  # higher for competitor at position 1 vs position 10
        opportunity_score = round(volume * user_factor * (1 + comp_bonus * 5), 1)

        gaps.append({
            "keyword": kw,
            "monthly_volume": int(volume),
            "user_status": user_status,
            "best_competitor_position": comp_pos,
            "search_intent": intent,
            "suggested_content_type": content_type,
            "opportunity_score": opportunity_score,
        })

    gaps.sort(key=lambda r: -r["opportunity_score"])

    fields = ["keyword", "opportunity_score", "monthly_volume", "user_status",
              "best_competitor_position", "search_intent", "suggested_content_type"]
    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(gaps)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(gaps)
        total_vol = sum(g["monthly_volume"] for g in gaps)
        top10_vol = sum(g["monthly_volume"] for g in gaps[:10])
        print(f"Wrote {len(gaps)} content gaps to {args.output}", file=sys.stderr)
        print(f"Total gap volume: {total_vol:,} monthly searches", file=sys.stderr)
        if total_vol > 0:
            print(f"Top 10 gaps capture {top10_vol/total_vol*100:.1f}% of total volume", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
