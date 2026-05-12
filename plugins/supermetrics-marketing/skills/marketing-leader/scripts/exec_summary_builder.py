#!/usr/bin/env python3
"""
Executive deck outline builder.

Takes a channel-level performance CSV (typically 90 days of cross-channel
data) and produces a slide-ready text outline matching the structure in
assets/exec_deck_outline.md.

Expected CSV columns:
    - channel
    - spend
    - revenue (or conversion_value)
    - conversions
    - impressions, clicks (optional)

Optional --compare-to: pass a second CSV with the prior period's data and
the outline will include a quarter-over-quarter slide.

Usage:
    python exec_summary_builder.py current_90d.csv \
        --output outline.md

    python exec_summary_builder.py current_90d.csv \
        --compare-to prior_90d.csv \
        --output outline.md
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Current period channel-level CSV")
    p.add_argument("--channel-col", default="channel", help="Channel column (default: channel)")
    p.add_argument("--compare-to", default=None, help="Optional prior-period CSV for QoQ slide")
    p.add_argument("--period-label", default="Last 90 days", help="Label for the current period")
    p.add_argument("--prior-period-label", default="Prior 90 days", help="Label for the prior period")
    p.add_argument("--output", default="-", help="Output markdown path (default: stdout)")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def aggregate(path, channel_col):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    channels = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "conversions": 0.0, "impressions": 0.0, "clicks": 0.0})
    for r in rows:
        ch = r.get(channel_col, "(unknown)")
        channels[ch]["spend"] += to_float(r.get("spend") or r.get("cost"))
        channels[ch]["revenue"] += to_float(r.get("revenue") or r.get("conversion_value"))
        channels[ch]["conversions"] += to_float(r.get("conversions"))
        channels[ch]["impressions"] += to_float(r.get("impressions"))
        channels[ch]["clicks"] += to_float(r.get("clicks"))
    return channels


def summary_metrics(channels):
    total_spend = sum(c["spend"] for c in channels.values())
    total_revenue = sum(c["revenue"] for c in channels.values())
    total_conversions = sum(c["conversions"] for c in channels.values())
    blended_roas = total_revenue / total_spend if total_spend > 0 else 0
    blended_cpa = total_spend / total_conversions if total_conversions > 0 else 0
    return {
        "total_spend": total_spend,
        "total_revenue": total_revenue,
        "total_conversions": total_conversions,
        "blended_roas": blended_roas,
        "blended_cpa": blended_cpa,
    }


def pct_change(curr, prev):
    if prev == 0:
        return None
    return (curr - prev) / prev * 100


def main():
    args = parse_args()
    current = aggregate(args.input, args.channel_col)
    if not current:
        print("No data in current-period file.", file=sys.stderr)
        return 1
    prior = aggregate(args.compare_to, args.channel_col) if args.compare_to else None

    curr_sum = summary_metrics(current)
    prior_sum = summary_metrics(prior) if prior else None

    lines = []
    lines.append("# Marketing Performance Overview")
    lines.append(f"*{args.period_label}*\n")

    # Slide 1: Headline summary
    lines.append("---")
    lines.append("## Slide 1 — Headline summary")
    lines.append(f"**Title:** {args.period_label}: performance at a glance")
    lines.append("**Bullets:**")
    lines.append(f"- Total spend: ${curr_sum['total_spend']:,.0f}")
    lines.append(f"- Total revenue: ${curr_sum['total_revenue']:,.0f}")
    lines.append(f"- Blended ROAS: {curr_sum['blended_roas']:.2f}x")
    lines.append(f"- Total conversions: {int(curr_sum['total_conversions']):,}")
    lines.append(f"- Blended CPA: ${curr_sum['blended_cpa']:,.2f}")
    lines.append("**Callout:** *[Insert one-sentence narrative — what's the story this quarter?]*\n")

    # Slide 2..N: Channel-level deep dives
    channel_list = sorted(current.keys(), key=lambda c: -current[c]["spend"])
    for i, ch in enumerate(channel_list, start=2):
        d = current[ch]
        roas = d["revenue"] / d["spend"] if d["spend"] > 0 else 0
        cpa = d["spend"] / d["conversions"] if d["conversions"] > 0 else 0
        share_spend = d["spend"] / curr_sum["total_spend"] * 100 if curr_sum["total_spend"] > 0 else 0
        share_rev = d["revenue"] / curr_sum["total_revenue"] * 100 if curr_sum["total_revenue"] > 0 else 0

        lines.append("---")
        lines.append(f"## Slide {i} — Channel deep dive: {ch}")
        lines.append(f"**Title:** {ch}")
        lines.append("**Bullets:**")
        lines.append(f"- Spend: ${d['spend']:,.0f} ({share_spend:.1f}% of total)")
        lines.append(f"- Revenue: ${d['revenue']:,.0f} ({share_rev:.1f}% of total)")
        lines.append(f"- Conversions: {int(d['conversions']):,}")
        lines.append(f"- ROAS: {roas:.2f}x | CPA: ${cpa:,.2f}")
        lines.append(f"**Callout:** *[Insert channel-specific narrative — what's driving the numbers?]*\n")

    next_slide = len(channel_list) + 2

    # Cross-channel comparison slide
    lines.append("---")
    lines.append(f"## Slide {next_slide} — Cross-channel comparison")
    lines.append("**Title:** Where the spend is working")
    lines.append("**Table:**")
    lines.append("| Channel | Spend | Revenue | ROAS | CPA |")
    lines.append("|---|---|---|---|---|")
    for ch in channel_list:
        d = current[ch]
        roas = d["revenue"] / d["spend"] if d["spend"] > 0 else 0
        cpa = d["spend"] / d["conversions"] if d["conversions"] > 0 else 0
        lines.append(f"| {ch} | ${d['spend']:,.0f} | ${d['revenue']:,.0f} | {roas:.2f}x | ${cpa:,.2f} |")
    lines.append("**Callout:** *[Which channel is the efficiency winner? Which is volume-driving but expensive?]*\n")
    next_slide += 1

    # QoQ slide if comparing
    if prior_sum:
        lines.append("---")
        lines.append(f"## Slide {next_slide} — Quarter-over-quarter")
        lines.append(f"**Title:** {args.period_label} vs. {args.prior_period_label}")
        lines.append("**Bullets:**")
        spend_change = pct_change(curr_sum["total_spend"], prior_sum["total_spend"])
        rev_change = pct_change(curr_sum["total_revenue"], prior_sum["total_revenue"])
        roas_change = pct_change(curr_sum["blended_roas"], prior_sum["blended_roas"])
        cpa_change = pct_change(curr_sum["blended_cpa"], prior_sum["blended_cpa"])
        for label, val in [("Spend", spend_change), ("Revenue", rev_change), ("Blended ROAS", roas_change), ("Blended CPA", cpa_change)]:
            sign = "+" if val and val > 0 else ""
            lines.append(f"- {label}: {sign}{val:.1f}%" if val is not None else f"- {label}: n/a")
        lines.append("**Callout:** *[What's the QoQ story — efficiency gained, scale gained, both, neither?]*\n")
        next_slide += 1

    # Recommendations slide
    lines.append("---")
    lines.append(f"## Slide {next_slide} — Strategic recommendations")
    lines.append("**Title:** Where to focus next quarter")
    lines.append("**Bullets:** *[Fill with 3-5 specific recommendations from the analysis. Each should name a channel, a dollar amount or percent shift, and the expected impact.]*")
    lines.append("- *Recommendation 1: [What to do, why, expected impact]*")
    lines.append("- *Recommendation 2: ...*")
    lines.append("- *Recommendation 3: ...*\n")
    next_slide += 1

    # Forecast slide
    lines.append("---")
    lines.append(f"## Slide {next_slide} — Next-period forecast")
    lines.append("**Title:** What we expect if we execute on the above")
    lines.append("**Bullets:** *[Project next-period spend, revenue, conversions, blended ROAS based on recommended budget mix.]*\n")
    next_slide += 1

    # Next steps slide
    lines.append("---")
    lines.append(f"## Slide {next_slide} — Next steps")
    lines.append("**Title:** What happens this week")
    lines.append("**Bullets:** *[Concrete actions with owners and dates. Not 'monitor' — specific changes.]*")
    lines.append("- *[Action 1] — owner: [name] — by: [date]*")
    lines.append("- *[Action 2] — ...*\n")

    output_text = "\n".join(lines) + "\n"

    if args.output == "-":
        sys.stdout.write(output_text)
    else:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Wrote outline to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
