#!/usr/bin/env python3
"""
Search term audit and negative keyword suggester.

Analyzes a Google Ads or Microsoft Ads search term report to find queries
costing money without converting. Proposes negative keywords by pattern.

Expected CSV columns:
    - search_term (the actual user query)
    - matched_keyword (optional, the keyword the user bid on)
    - campaign (optional)
    - ad_group (optional)
    - clicks
    - cost
    - conversions

Usage:
    python search_term_auditor.py search_terms.csv \
        --min-cost 50 \
        --max-conversions 0 \
        --exclude-patterns "free,jobs,wikipedia" \
        --output recommendations.csv

The user must provide --exclude-patterns. The script doesn't invent
irrelevance patterns — those are domain-specific to the user's business.
Common starter patterns (suggest if user has none):
    - "free, jobs, career, salary, wikipedia, login, ceo, contact"
    - Competitor brand names (specific to the user)
    - Geographic exclusions if the user only serves certain regions
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Search term report CSV")
    p.add_argument("--term-col", default="search_term", help="Search term column")
    p.add_argument("--min-cost", type=float, default=50.0, help="Min cost (USD) to flag a term (default: 50)")
    p.add_argument("--max-conversions", type=float, default=0.0, help="Max conversions tolerated (default: 0)")
    p.add_argument("--cpc-multiplier", type=float, default=2.0, help="Flag terms with CPC >Nx campaign avg (default: 2.0)")
    p.add_argument("--exclude-patterns", default="", help="Comma-separated irrelevance patterns (e.g. 'free,jobs,wikipedia')")
    p.add_argument("--output", default="-", help="Output CSV (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def detect_pattern(term, patterns):
    """Return the matching pattern, or empty string."""
    term_lower = term.lower()
    for p in patterns:
        if p and p.lower() in term_lower:
            return p
    return ""


def main():
    args = parse_args()
    patterns = [p.strip() for p in args.exclude_patterns.split(",") if p.strip()]

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data in input file.", file=sys.stderr)
        return 1

    term_col = args.term_col
    if term_col not in rows[0]:
        for c in ("search_term", "query", "search_query"):
            if c in rows[0]:
                term_col = c
                break

    # Aggregate per search term
    terms = defaultdict(lambda: {"clicks": 0.0, "cost": 0.0, "conversions": 0.0, "campaigns": set(), "ad_groups": set()})
    total_clicks = 0
    total_cost = 0
    for r in rows:
        t = r.get(term_col, "").strip()
        if not t:
            continue
        terms[t]["clicks"] += to_float(r.get("clicks"))
        terms[t]["cost"] += to_float(r.get("cost") or r.get("spend"))
        terms[t]["conversions"] += to_float(r.get("conversions"))
        if r.get("campaign"):
            terms[t]["campaigns"].add(r["campaign"])
        if r.get("ad_group"):
            terms[t]["ad_groups"].add(r["ad_group"])
        total_clicks += to_float(r.get("clicks"))
        total_cost += to_float(r.get("cost") or r.get("spend"))

    avg_cpc = total_cost / total_clicks if total_clicks > 0 else 0
    cpc_threshold = avg_cpc * args.cpc_multiplier if avg_cpc > 0 else float("inf")

    flagged = []
    for term, d in terms.items():
        cpc = d["cost"] / d["clicks"] if d["clicks"] > 0 else 0

        # Flagging logic
        reasons = []
        if d["cost"] >= args.min_cost and d["conversions"] <= args.max_conversions:
            reasons.append(f"${d['cost']:.0f} spent, {int(d['conversions'])} conv")
        if cpc > cpc_threshold and d["cost"] > args.min_cost / 2:
            reasons.append(f"CPC ${cpc:.2f} ({cpc/avg_cpc:.1f}x avg)")
        pattern_match = detect_pattern(term, patterns)
        if pattern_match and d["cost"] > 0:
            reasons.append(f"matches '{pattern_match}'")

        if not reasons:
            continue

        # Suggest match type
        word_count = len(term.split())
        if pattern_match:
            match_type = "broad" if word_count > 2 else "phrase"
        elif word_count == 1:
            match_type = "exact"
        elif word_count <= 3:
            match_type = "phrase"
        else:
            match_type = "exact"

        flagged.append({
            "search_term": term,
            "cost": round(d["cost"], 2),
            "clicks": int(d["clicks"]),
            "conversions": int(d["conversions"]),
            "cpc": round(cpc, 2),
            "suggested_match_type": match_type,
            "suggested_negative": term if match_type == "exact" else pattern_match or term,
            "campaigns_affected": "; ".join(sorted(d["campaigns"]))[:200] if d["campaigns"] else "",
            "rationale": "; ".join(reasons),
        })

    if not flagged:
        print(f"No terms meet the criteria (min cost ${args.min_cost}, max conv {args.max_conversions}).", file=sys.stderr)
        return 0

    flagged.sort(key=lambda r: -r["cost"])

    fields = ["search_term", "cost", "clicks", "conversions", "cpc",
              "suggested_match_type", "suggested_negative", "campaigns_affected", "rationale"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(flagged)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(flagged)
        total_waste = sum(r["cost"] for r in flagged)
        print(f"Wrote {len(flagged)} negative keyword recommendations to {args.output}.", file=sys.stderr)
        print(f"Total wasted spend across flagged terms: ${total_waste:,.2f}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
