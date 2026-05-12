#!/usr/bin/env python3
"""
ABM (account-based marketing) target account engagement analyzer.

Computes coverage and engagement metrics across a defined target account
list, combining signals from ad impressions, web sessions, CRM activities,
and pipeline status.

Expected CSV columns (one row per target account):
    - account_name (or account_id)
    - tier (optional: Tier 1, Tier 2, etc.)
    - ad_impressions (LinkedIn account-based targeting impressions, etc.)
    - ad_clicks
    - web_sessions (from GA4 with company identification, if available)
    - meetings_booked (from CRM)
    - opportunity_status (none, open, closed-won, closed-lost)
    - opportunity_amount (optional)
    - last_touchpoint_date

Usage:
    python abm_engagement.py target_accounts.csv --output engagement.csv

The script computes an engagement score (0-100) per account based on
ad exposure, web visits, and CRM activities. Outputs coverage %, engaged
account %, in-pipeline %, and a ranked list.
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Target accounts CSV")
    p.add_argument("--output", default="-")
    p.add_argument("--by-tier", action="store_true", help="Aggregate per tier instead of per account")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def engagement_score(impressions, clicks, sessions, meetings):
    """Composite 0-100 score."""
    score = 0
    if impressions >= 100:
        score += 20
    elif impressions >= 10:
        score += 10
    if clicks >= 5:
        score += 25
    elif clicks >= 1:
        score += 15
    if sessions >= 3:
        score += 25
    elif sessions >= 1:
        score += 15
    if meetings >= 1:
        score += 30
    return min(100, score)


def engagement_tier(score):
    if score >= 70:
        return "engaged"
    if score >= 40:
        return "warming"
    if score >= 15:
        return "aware"
    return "cold"


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        accounts = list(csv.DictReader(f))

    if not accounts:
        print("No accounts.", file=sys.stderr)
        return 1

    enriched = []
    for a in accounts:
        impr = to_float(a.get("ad_impressions"))
        clicks = to_float(a.get("ad_clicks"))
        sessions = to_float(a.get("web_sessions"))
        meetings = to_float(a.get("meetings_booked"))

        score = engagement_score(impr, clicks, sessions, meetings)
        tier = engagement_tier(score)

        opp_status = (a.get("opportunity_status") or "none").lower()
        in_pipeline = opp_status in ("open", "active") or opp_status.startswith("stage")
        closed_won = opp_status in ("closed-won", "won")

        enriched.append({
            "account_name": a.get("account_name") or a.get("account_id") or "(unknown)",
            "tier": a.get("tier", ""),
            "engagement_score": score,
            "engagement_tier": tier,
            "ad_impressions": int(impr),
            "ad_clicks": int(clicks),
            "web_sessions": int(sessions),
            "meetings_booked": int(meetings),
            "opportunity_status": opp_status,
            "opportunity_amount": round(to_float(a.get("opportunity_amount")), 2),
            "in_pipeline": "yes" if in_pipeline else "",
            "closed_won": "yes" if closed_won else "",
            "last_touchpoint_date": a.get("last_touchpoint_date", ""),
        })

    # Aggregate summary
    total = len(enriched)
    reached = sum(1 for a in enriched if a["ad_impressions"] > 0 or a["web_sessions"] > 0)
    engaged = sum(1 for a in enriched if a["engagement_tier"] in ("engaged", "warming"))
    in_pipe = sum(1 for a in enriched if a["in_pipeline"])
    won = sum(1 for a in enriched if a["closed_won"])

    print(f"--- ABM target account summary ---", file=sys.stderr)
    print(f"Total target accounts: {total}", file=sys.stderr)
    print(f"Reached (any ad or web touch): {reached} ({reached/total*100:.1f}%)", file=sys.stderr)
    print(f"Engaged (warming or higher):   {engaged} ({engaged/total*100:.1f}%)", file=sys.stderr)
    print(f"In active pipeline:            {in_pipe} ({in_pipe/total*100:.1f}%)", file=sys.stderr)
    print(f"Closed won:                    {won} ({won/total*100:.1f}%)", file=sys.stderr)

    if args.by_tier:
        agg = defaultdict(lambda: {"total": 0, "reached": 0, "engaged": 0, "in_pipeline": 0, "closed_won": 0})
        for a in enriched:
            t = a["tier"] or "(no tier)"
            agg[t]["total"] += 1
            if a["ad_impressions"] > 0 or a["web_sessions"] > 0:
                agg[t]["reached"] += 1
            if a["engagement_tier"] in ("engaged", "warming"):
                agg[t]["engaged"] += 1
            if a["in_pipeline"]:
                agg[t]["in_pipeline"] += 1
            if a["closed_won"]:
                agg[t]["closed_won"] += 1
        out_rows = []
        for t, d in sorted(agg.items()):
            out_rows.append({
                "tier": t,
                "total_accounts": d["total"],
                "reached": d["reached"],
                "reached_pct": round(d["reached"]/d["total"]*100, 1) if d["total"] else 0,
                "engaged": d["engaged"],
                "engaged_pct": round(d["engaged"]/d["total"]*100, 1) if d["total"] else 0,
                "in_pipeline": d["in_pipeline"],
                "in_pipeline_pct": round(d["in_pipeline"]/d["total"]*100, 1) if d["total"] else 0,
                "closed_won": d["closed_won"],
                "closed_won_pct": round(d["closed_won"]/d["total"]*100, 1) if d["total"] else 0,
            })
        fields = ["tier", "total_accounts", "reached", "reached_pct", "engaged", "engaged_pct",
                 "in_pipeline", "in_pipeline_pct", "closed_won", "closed_won_pct"]
    else:
        enriched.sort(key=lambda a: -a["engagement_score"])
        out_rows = enriched
        fields = ["account_name", "tier", "engagement_score", "engagement_tier",
                  "ad_impressions", "ad_clicks", "web_sessions", "meetings_booked",
                  "opportunity_status", "opportunity_amount", "in_pipeline", "closed_won",
                  "last_touchpoint_date"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} rows to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
