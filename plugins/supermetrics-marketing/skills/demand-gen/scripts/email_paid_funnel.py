#!/usr/bin/env python3
"""
Email + paid integrated funnel analyzer.

Joins paid acquisition data with email subscriber data to build a unified
view of how paid acquisition feeds email nurture, and how email nurture
contributes to conversions.

Expected CSV columns:
    - channel (paid channel name; "Email/Organic" for non-paid subscribers)
    - clicks (paid clicks)
    - spend
    - subscribed (count who became subscribers in the period)
    - converted_direct (converted without entering email nurture)
    - converted_via_email (converted after subscribing, attributable to email)
    - still_nurturing (subscribed but not yet converted)

Usage:
    python email_paid_funnel.py funnel.csv --output flow.csv

Outputs per channel: subscribe rate, direct conversion rate, eventual
conversion rate via nurture, blended conversion rate, blended cost per
conversion.
"""

import argparse
import sys
import csv


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Funnel CSV")
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
        rows = list(csv.DictReader(f))

    out_rows = []
    for r in rows:
        channel = r.get("channel", "(unknown)")
        clicks = to_float(r.get("clicks"))
        spend = to_float(r.get("spend"))
        subscribed = to_float(r.get("subscribed"))
        conv_direct = to_float(r.get("converted_direct"))
        conv_email = to_float(r.get("converted_via_email"))
        nurturing = to_float(r.get("still_nurturing"))

        total_conv = conv_direct + conv_email
        # Use clicks as the denominator when available; otherwise subscribed + direct conversions
        denom = clicks if clicks > 0 else (subscribed + conv_direct)

        subscribe_rate = subscribed / clicks * 100 if clicks > 0 else None
        direct_conv_rate = conv_direct / clicks * 100 if clicks > 0 else None
        email_conv_rate = conv_email / subscribed * 100 if subscribed > 0 else None
        blended_rate = total_conv / denom * 100 if denom > 0 else None
        cost_per_conv = spend / total_conv if total_conv > 0 else None

        # Classify channel pattern
        if subscribed > 0 and conv_email > conv_direct:
            pattern = "nurture-amplified"
        elif conv_direct > 0 and conv_email < conv_direct * 0.3:
            pattern = "direct-converter"
        elif subscribed > 0 and nurturing > (conv_direct + conv_email):
            pattern = "list-builder"
        else:
            pattern = "mixed"

        out_rows.append({
            "channel": channel,
            "pattern": pattern,
            "clicks": int(clicks),
            "spend": round(spend, 2),
            "subscribed": int(subscribed),
            "subscribe_rate_pct": round(subscribe_rate, 2) if subscribe_rate is not None else "n/a",
            "converted_direct": int(conv_direct),
            "direct_conv_rate_pct": round(direct_conv_rate, 2) if direct_conv_rate is not None else "n/a",
            "converted_via_email": int(conv_email),
            "email_conv_rate_pct": round(email_conv_rate, 2) if email_conv_rate is not None else "n/a",
            "still_nurturing": int(nurturing),
            "total_conversions": int(total_conv),
            "blended_conv_rate_pct": round(blended_rate, 2) if blended_rate is not None else "n/a",
            "cost_per_conversion": round(cost_per_conv, 2) if cost_per_conv is not None else "n/a",
        })

    out_rows.sort(key=lambda r: -r["total_conversions"])

    fields = ["channel", "pattern", "clicks", "spend", "subscribed", "subscribe_rate_pct",
              "converted_direct", "direct_conv_rate_pct", "converted_via_email", "email_conv_rate_pct",
              "still_nurturing", "total_conversions", "blended_conv_rate_pct", "cost_per_conversion"]
    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} channels to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
