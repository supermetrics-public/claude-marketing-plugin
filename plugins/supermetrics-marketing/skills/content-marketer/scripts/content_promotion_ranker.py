#!/usr/bin/env python3
"""
Content asset promotion ranker.

Ranks promoted content assets (whitepapers, ebooks, guides, etc.) by their
paid-promotion engagement metrics: CPC, CTR, and optionally lead rate.
Produces a composite "promotion-worthiness" score that informs which
assets deserve more paid budget next period.

Expected CSV columns:
    - asset_name (or ad_name — the content asset being promoted)
    - platform (or channel)
    - spend
    - clicks
    - impressions
    - conversions or leads (optional)

Usage:
    python content_promotion_ranker.py input.csv \
        --min-spend 100 \
        --output ranked.csv

The score:
    - CPC rank (ascending) gets weight 0.4
    - CTR rank (descending) gets weight 0.4
    - Lead rate rank (descending) gets weight 0.2 if lead data exists, else CPC/CTR weights become 0.5/0.5
    - Final score = sum of (weight × normalized_rank_score)
    - Assets are sorted by final score descending
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Content promotion CSV")
    p.add_argument("--asset-col", default="asset_name", help="Asset identifier column (default: asset_name)")
    p.add_argument("--min-spend", type=float, default=100.0, help="Exclude assets with spend below this (default: 100)")
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

    asset_col = args.asset_col
    if asset_col not in rows[0]:
        for candidate in ("asset_name", "ad_name", "creative_name", "content_asset"):
            if candidate in rows[0]:
                asset_col = candidate
                break

    assets = defaultdict(lambda: {"spend": 0.0, "clicks": 0.0, "impressions": 0.0, "leads": 0.0, "platforms": set()})
    for r in rows:
        a = r.get(asset_col, "(unknown)")
        assets[a]["spend"] += to_float(r.get("spend") or r.get("cost"))
        assets[a]["clicks"] += to_float(r.get("clicks"))
        assets[a]["impressions"] += to_float(r.get("impressions"))
        assets[a]["leads"] += to_float(r.get("leads") or r.get("conversions"))
        if "platform" in r:
            assets[a]["platforms"].add(r["platform"])

    # Filter by minimum spend
    assets = {a: d for a, d in assets.items() if d["spend"] >= args.min_spend}

    if not assets:
        print(f"No assets meet --min-spend {args.min_spend}.", file=sys.stderr)
        return 1

    # Compute per-asset metrics
    summary = []
    for a, d in assets.items():
        cpc = (d["spend"] / d["clicks"]) if d["clicks"] > 0 else float("inf")
        ctr = (d["clicks"] / d["impressions"] * 100) if d["impressions"] > 0 else 0
        lead_rate = (d["leads"] / d["clicks"] * 100) if d["clicks"] > 0 else 0
        summary.append({
            "asset": a,
            "platforms": ", ".join(sorted(d["platforms"])) if d["platforms"] else "",
            "spend": round(d["spend"], 2),
            "clicks": int(d["clicks"]),
            "impressions": int(d["impressions"]),
            "cpc": round(cpc, 2) if cpc != float("inf") else None,
            "ctr_pct": round(ctr, 2),
            "leads": int(d["leads"]) if d["leads"] > 0 else 0,
            "lead_rate_pct": round(lead_rate, 2),
        })

    # Compute ranks (1 = best)
    # CPC ascending (lower is better), CTR descending, lead_rate descending
    valid_cpc = [s for s in summary if s["cpc"] is not None]
    valid_cpc.sort(key=lambda x: x["cpc"])
    for rank, s in enumerate(valid_cpc, 1):
        s["_cpc_rank"] = rank

    summary.sort(key=lambda x: -x["ctr_pct"])
    for rank, s in enumerate(summary, 1):
        s["_ctr_rank"] = rank

    has_leads = any(s["leads"] > 0 for s in summary)
    if has_leads:
        summary.sort(key=lambda x: -x["lead_rate_pct"])
        for rank, s in enumerate(summary, 1):
            s["_lead_rank"] = rank

    n = len(summary)

    # Composite score (higher is better)
    for s in summary:
        cpc_score = (n - s.get("_cpc_rank", n)) / max(n - 1, 1) if "_cpc_rank" in s else 0
        ctr_score = (n - s["_ctr_rank"]) / max(n - 1, 1)
        if has_leads:
            lead_score = (n - s["_lead_rank"]) / max(n - 1, 1)
            s["promotion_score"] = round(0.4 * cpc_score + 0.4 * ctr_score + 0.2 * lead_score, 3)
        else:
            s["promotion_score"] = round(0.5 * cpc_score + 0.5 * ctr_score, 3)

    # Final sort
    summary.sort(key=lambda x: -x["promotion_score"])
    for rank, s in enumerate(summary, 1):
        s["final_rank"] = rank

    # Clean output
    out_fields = ["final_rank", "asset", "platforms", "promotion_score", "cpc", "ctr_pct",
                  "lead_rate_pct", "leads", "spend", "clicks", "impressions"]
    out_rows = [{k: s.get(k, "") for k in out_fields} for s in summary]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Ranked {len(out_rows)} content assets, wrote to {args.output}.", file=sys.stderr)
        if not has_leads:
            print("Note: no lead/conversion data found. Score uses CPC + CTR only.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
