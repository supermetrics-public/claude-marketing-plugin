#!/usr/bin/env python3
"""
Target account engagement scoring around an event.

Scores each target account on engagement signals across the period
spanning the event (pre/during/post).

Expected CSV columns:
    - account_name
    - tier (optional: Tier 1, Tier 2, etc.)
    - attendees_from_account (count from this account who attended)
    - max_seniority (CEO, VP, Director, Manager, IC — for weighting)
    - pre_event_ad_impressions
    - pre_event_ad_clicks
    - post_event_web_sessions
    - meetings_booked (sales activities logged post-event)
    - in_pipeline (yes/no)
    - opportunity_amount (if in pipeline)

Usage:
    python account_engagement.py target_accounts.csv --output engagement.csv

Engagement signals weighted: attended (with seniority bonus), pre-event
ad exposure, post-event site visits, meetings booked.
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Target accounts CSV")
    p.add_argument("--output", default="-")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def seniority_weight(s):
    s = (s or "").lower()
    if "ceo" in s or "founder" in s or "president" in s:
        return 3.0
    if "vp" in s or "vice president" in s or "head of" in s:
        return 2.5
    if "director" in s:
        return 2.0
    if "manager" in s:
        return 1.5
    return 1.0  # IC or unknown


def engagement_score(attendees, seniority_w, pre_impr, pre_clicks, post_sessions, meetings):
    """0-100 composite score."""
    score = 0
    # Attendance is the dominant signal
    if attendees > 0:
        score += min(35, 25 + (seniority_w - 1) * 5)  # 25 base + up to 10 seniority bonus
        if attendees >= 2:
            score += 10  # multi-person attendance
    # Pre-event ad exposure
    if pre_impr >= 100:
        score += 10
    elif pre_impr >= 10:
        score += 5
    if pre_clicks >= 3:
        score += 10
    elif pre_clicks >= 1:
        score += 5
    # Post-event web traffic
    if post_sessions >= 3:
        score += 15
    elif post_sessions >= 1:
        score += 8
    # Meetings = strongest signal
    if meetings >= 2:
        score += 25
    elif meetings >= 1:
        score += 15
    return min(100, score)


def tier_classification(score):
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

    out_rows = []
    for a in accounts:
        attendees = to_float(a.get("attendees_from_account"))
        seniority_w = seniority_weight(a.get("max_seniority", ""))
        pre_impr = to_float(a.get("pre_event_ad_impressions"))
        pre_clicks = to_float(a.get("pre_event_ad_clicks"))
        post_sessions = to_float(a.get("post_event_web_sessions"))
        meetings = to_float(a.get("meetings_booked"))

        score = engagement_score(attendees, seniority_w, pre_impr, pre_clicks, post_sessions, meetings)
        tier = tier_classification(score)
        in_pipeline = (a.get("in_pipeline", "").lower() in ("yes", "true", "1"))
        opp_amount = to_float(a.get("opportunity_amount"))

        out_rows.append({
            "account_name": a.get("account_name", ""),
            "abm_tier": a.get("tier", ""),
            "engagement_tier": tier,
            "engagement_score": score,
            "attendees_from_account": int(attendees),
            "max_seniority": a.get("max_seniority", ""),
            "pre_event_impressions": int(pre_impr),
            "pre_event_clicks": int(pre_clicks),
            "post_event_web_sessions": int(post_sessions),
            "meetings_booked": int(meetings),
            "in_pipeline": "yes" if in_pipeline else "",
            "opportunity_amount": round(opp_amount, 2),
            "needs_follow_up": "yes" if tier in ("engaged", "warming") and not in_pipeline else "",
        })

    out_rows.sort(key=lambda r: -r["engagement_score"])

    # Summary
    total = len(out_rows)
    engaged = sum(1 for r in out_rows if r["engagement_tier"] == "engaged")
    warming = sum(1 for r in out_rows if r["engagement_tier"] == "warming")
    in_pipe = sum(1 for r in out_rows if r["in_pipeline"])
    needs_fu = sum(1 for r in out_rows if r["needs_follow_up"])

    print(f"--- Target account engagement summary ---", file=sys.stderr)
    print(f"Total target accounts: {total}", file=sys.stderr)
    print(f"Engaged: {engaged} ({engaged/total*100:.1f}%)", file=sys.stderr)
    print(f"Warming: {warming} ({warming/total*100:.1f}%)", file=sys.stderr)
    print(f"In pipeline: {in_pipe} ({in_pipe/total*100:.1f}%)", file=sys.stderr)
    print(f"Needs sales follow-up (engaged/warming, not yet in pipeline): {needs_fu}", file=sys.stderr)

    fields = ["account_name", "abm_tier", "engagement_tier", "engagement_score",
              "attendees_from_account", "max_seniority",
              "pre_event_impressions", "pre_event_clicks", "post_event_web_sessions", "meetings_booked",
              "in_pipeline", "opportunity_amount", "needs_follow_up"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} accounts to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
