#!/usr/bin/env python3
"""
Multi-event portfolio analyzer.

Ranks events across a quarter or year by composite ROI score.

Expected CSV columns:
    - event_name
    - event_type (in-person, webinar, virtual conference, dinner, workshop)
    - location (optional)
    - date
    - total_cost (promotion + venue + production)
    - registrations
    - attendees
    - mqls_within_30d (optional)
    - pipeline_value (optional)

Usage:
    python event_portfolio.py events.csv --output portfolio.csv
"""

import argparse
import sys
import csv
from collections import defaultdict
from statistics import mean


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Events CSV")
    p.add_argument("--output", default="-")
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
        events = list(csv.DictReader(f))

    if not events:
        print("No events.", file=sys.stderr)
        return 1

    enriched = []
    for e in events:
        cost = to_float(e.get("total_cost"))
        regs = to_float(e.get("registrations"))
        attendees = to_float(e.get("attendees"))
        mqls = to_float(e.get("mqls_within_30d"))
        pipeline = to_float(e.get("pipeline_value"))

        cpr = cost / regs if regs > 0 else None
        cpa = cost / attendees if attendees > 0 else None
        attend_rate = attendees / regs * 100 if regs > 0 else None
        mql_rate = mqls / attendees * 100 if attendees > 0 else None
        cpmql = cost / mqls if mqls > 0 else None
        pipeline_roas = pipeline / cost if cost > 0 else None

        enriched.append({
            "event_name": e.get("event_name", ""),
            "event_type": e.get("event_type", ""),
            "location": e.get("location", ""),
            "date": e.get("date", ""),
            "total_cost": round(cost, 2),
            "registrations": int(regs),
            "attendees": int(attendees),
            "attendance_rate_pct": round(attend_rate, 1) if attend_rate is not None else "n/a",
            "cost_per_registration": round(cpr, 2) if cpr is not None else "n/a",
            "cost_per_attendee": round(cpa, 2) if cpa is not None else "n/a",
            "mqls_within_30d": int(mqls),
            "mql_rate_pct": round(mql_rate, 1) if mql_rate is not None else "n/a",
            "cost_per_mql": round(cpmql, 2) if cpmql is not None else "n/a",
            "pipeline_value": round(pipeline, 2),
            "pipeline_roas": round(pipeline_roas, 2) if pipeline_roas is not None else "n/a",
        })

    # Composite score: normalize CPA and MQL rate within event type
    by_type = defaultdict(list)
    for e in enriched:
        by_type[e["event_type"]].append(e)

    for event_type, type_events in by_type.items():
        # Lower CPA is better; higher MQL rate is better
        cpas = [e["cost_per_attendee"] for e in type_events if isinstance(e["cost_per_attendee"], (int, float))]
        mqls = [e["mql_rate_pct"] for e in type_events if isinstance(e["mql_rate_pct"], (int, float))]
        if cpas:
            min_cpa, max_cpa = min(cpas), max(cpas)
            cpa_range = max_cpa - min_cpa if max_cpa > min_cpa else 1
        else:
            min_cpa, cpa_range = 0, 1
        if mqls:
            min_mql, max_mql = min(mqls), max(mqls)
            mql_range = max_mql - min_mql if max_mql > min_mql else 1
        else:
            min_mql, mql_range = 0, 1

        for e in type_events:
            cpa_norm = 100 - ((e["cost_per_attendee"] - min_cpa) / cpa_range * 100) if isinstance(e["cost_per_attendee"], (int, float)) and cpa_range > 0 else 50
            mql_norm = ((e["mql_rate_pct"] - min_mql) / mql_range * 100) if isinstance(e["mql_rate_pct"], (int, float)) and mql_range > 0 else 50
            e["composite_score"] = round((cpa_norm * 0.5) + (mql_norm * 0.5), 1)

    enriched.sort(key=lambda e: -e["composite_score"])

    fields = ["event_name", "event_type", "location", "date", "composite_score",
              "total_cost", "registrations", "attendees", "attendance_rate_pct",
              "cost_per_registration", "cost_per_attendee",
              "mqls_within_30d", "mql_rate_pct", "cost_per_mql",
              "pipeline_value", "pipeline_roas"]

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(enriched)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(enriched)
        # Summary by type
        print(f"--- Portfolio summary by event type ---", file=sys.stderr)
        for event_type, type_events in by_type.items():
            costs = sum(e["total_cost"] for e in type_events)
            attendees = sum(e["attendees"] for e in type_events)
            pipeline = sum(e["pipeline_value"] for e in type_events)
            print(f"  {event_type}: {len(type_events)} events, ${costs:,.0f} spent, {attendees:,} attendees, ${pipeline:,.0f} pipeline", file=sys.stderr)
        print(f"Wrote {len(enriched)} events to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
