#!/usr/bin/env python3
"""
Event-attributed pipeline tracker.

Joins event attendee list with CRM opportunities to track pipeline
created in 30/60/90 day windows after the event.

Expected CSV columns:
    - attendee_email
    - attendee_company (optional, for fuzzy matching)
    - event_date (single date or per-row)
    - matched_in_crm (yes/no — whether the attendee matched to a CRM contact)
    - opp_created_date (empty if no opp; may be multiple opps per row if comma-separated)
    - opp_amount (matching list to opp_created_date)
    - opp_stage (matching list to opp_created_date)

Usage:
    python event_pipeline_tracker.py attendees.csv \
        --event-date 2026-04-15 \
        --event-cost 75000 \
        --output pipeline.csv
"""

import argparse
import sys
import csv
from datetime import datetime


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Attendees CSV")
    p.add_argument("--event-date", required=True, help="Event date YYYY-MM-DD")
    p.add_argument("--event-cost", type=float, default=0, help="Event total cost for ROAS calc")
    p.add_argument("--output", default="-")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(s).strip(), fmt).date()
        except ValueError:
            continue
    return None


def main():
    args = parse_args()
    event_date = parse_date(args.event_date)
    if not event_date:
        print(f"Invalid event date: {args.event_date}", file=sys.stderr)
        return 1

    with open(args.input, newline="") as f:
        attendees = list(csv.DictReader(f))

    total_attendees = len(attendees)
    matched = 0
    windows = {30: {"opps": 0, "value": 0.0, "closed_won": 0, "won_value": 0.0},
               60: {"opps": 0, "value": 0.0, "closed_won": 0, "won_value": 0.0},
               90: {"opps": 0, "value": 0.0, "closed_won": 0, "won_value": 0.0}}

    per_attendee = []
    for a in attendees:
        is_matched = (a.get("matched_in_crm", "").lower() in ("yes", "true", "1"))
        if is_matched:
            matched += 1

        opp_dates_raw = a.get("opp_created_date", "")
        opp_amounts_raw = a.get("opp_amount", "")
        opp_stages_raw = a.get("opp_stage", "")

        opp_dates = [parse_date(s.strip()) for s in opp_dates_raw.split(",") if s.strip()]
        opp_amounts = [to_float(s.strip()) for s in opp_amounts_raw.split(",") if s.strip()]
        opp_stages = [s.strip() for s in opp_stages_raw.split(",") if s.strip()]

        attendee_total_opps = 0
        attendee_total_value = 0.0
        for i, opp_date in enumerate(opp_dates):
            if not opp_date or opp_date < event_date:
                continue
            days_since = (opp_date - event_date).days
            amount = opp_amounts[i] if i < len(opp_amounts) else 0
            stage = opp_stages[i] if i < len(opp_stages) else ""
            is_won = stage.lower() in ("closed-won", "won", "closed won")

            attendee_total_opps += 1
            attendee_total_value += amount

            for win in (30, 60, 90):
                if days_since <= win:
                    windows[win]["opps"] += 1
                    windows[win]["value"] += amount
                    if is_won:
                        windows[win]["closed_won"] += 1
                        windows[win]["won_value"] += amount

        per_attendee.append({
            "email": a.get("attendee_email", ""),
            "company": a.get("attendee_company", ""),
            "matched_in_crm": "yes" if is_matched else "no",
            "opps_post_event": attendee_total_opps,
            "opp_value": round(attendee_total_value, 2),
        })

    # Output: summary first, then per-attendee
    if args.output == "-":
        out_stream = sys.stdout
        close_after = False
    else:
        out_stream = open(args.output, "w", newline="")
        close_after = True

    out_stream.write(f"--- Event pipeline summary ---\n")
    out_stream.write(f"Event date: {event_date}\n")
    out_stream.write(f"Total attendees: {total_attendees}\n")
    out_stream.write(f"Matched to CRM: {matched} ({matched/total_attendees*100:.1f}%)\n\n" if total_attendees > 0 else "\n")

    out_stream.write(f"{'Window':<12}{'Opps':>8}{'Pipeline':>16}{'Won':>8}{'Won value':>16}{'Pipeline ROAS':>18}\n")
    for win in (30, 60, 90):
        w = windows[win]
        roas = w["value"] / args.event_cost if args.event_cost > 0 else None
        out_stream.write(f"{win}d{'':<10}{w['opps']:>8}${w['value']:>14,.0f}{w['closed_won']:>8}${w['won_value']:>14,.0f}")
        out_stream.write(f"{roas:>17.2f}x\n" if roas is not None else f"{'n/a':>18}\n")

    out_stream.write(f"\n--- Per attendee ---\n")
    writer = csv.DictWriter(out_stream, fieldnames=["email", "company", "matched_in_crm", "opps_post_event", "opp_value"])
    writer.writeheader()
    writer.writerows(per_attendee)

    if close_after:
        out_stream.close()
        print(f"Wrote pipeline tracking to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
