#!/usr/bin/env python3
"""
Cross-platform video content ranker.

Normalizes engagement metrics within each platform and produces a
composite ranking. Each platform reports metrics differently — this
script normalizes by platform percentile before combining.

Expected CSV columns:
    - title (video title or identifier)
    - platform (YouTube, TikTok, Instagram, LinkedIn, etc.)
    - publish_date
    - views
    - completion_rate (or average_view_duration_pct)  # 0-100 or 0-1
    - engagement_rate  # likes + comments + shares / views, 0-1 or 0-100
    - clicks (optional, click-through to external link)
    - conversions (optional)

Usage:
    python video_content_ranker.py videos.csv --output ranked.csv
"""

import argparse
import sys
import csv
from collections import defaultdict


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Video performance CSV")
    p.add_argument("--output", default="-")
    return p.parse_args()


def to_float(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").replace("$", "").replace("%", ""))
    except ValueError:
        return 0.0


def percentile_rank(value, sorted_list):
    """Return percentile (0-100) of value within sorted_list."""
    if not sorted_list:
        return 50
    n = len(sorted_list)
    rank = sum(1 for v in sorted_list if v < value)
    return (rank / n * 100) if n > 0 else 50


def main():
    args = parse_args()

    with open(args.input, newline="") as f:
        rows = list(csv.DictReader(f))

    videos = []
    for r in rows:
        views = to_float(r.get("views"))
        completion = to_float(r.get("completion_rate") or r.get("average_view_duration_pct"))
        engagement = to_float(r.get("engagement_rate"))
        # Normalize completion/engagement: if value > 1, assume it's already a percentage
        if completion > 1:
            completion = completion / 100
        if engagement > 1:
            engagement = engagement / 100

        videos.append({
            "title": r.get("title", "(untitled)"),
            "platform": r.get("platform", "(unknown)"),
            "publish_date": r.get("publish_date", ""),
            "views": views,
            "completion_rate": completion,
            "engagement_rate": engagement,
            "clicks": to_float(r.get("clicks")),
            "conversions": to_float(r.get("conversions")),
        })

    # Compute per-platform percentiles
    by_platform = defaultdict(list)
    for v in videos:
        by_platform[v["platform"]].append(v)

    for plat, plat_videos in by_platform.items():
        views_sorted = sorted([v["views"] for v in plat_videos])
        completion_sorted = sorted([v["completion_rate"] for v in plat_videos])
        engagement_sorted = sorted([v["engagement_rate"] for v in plat_videos])
        for v in plat_videos:
            v["views_percentile"] = round(percentile_rank(v["views"], views_sorted), 1)
            v["completion_percentile"] = round(percentile_rank(v["completion_rate"], completion_sorted), 1)
            v["engagement_percentile"] = round(percentile_rank(v["engagement_rate"], engagement_sorted), 1)
            v["composite_score"] = round(
                v["views_percentile"] * 0.3 +
                v["completion_percentile"] * 0.35 +
                v["engagement_percentile"] * 0.35, 1
            )

    # Sort: by platform first, then composite score within
    videos.sort(key=lambda v: (v["platform"], -v["composite_score"]))

    out_rows = []
    for v in videos:
        out_rows.append({
            "platform": v["platform"],
            "title": v["title"],
            "publish_date": v["publish_date"],
            "composite_score": v["composite_score"],
            "views": int(v["views"]),
            "views_percentile": v["views_percentile"],
            "completion_rate_pct": round(v["completion_rate"] * 100, 1),
            "completion_percentile": v["completion_percentile"],
            "engagement_rate_pct": round(v["engagement_rate"] * 100, 2),
            "engagement_percentile": v["engagement_percentile"],
            "clicks": int(v["clicks"]),
            "conversions": int(v["conversions"]),
        })

    fields = ["platform", "title", "publish_date", "composite_score",
              "views", "views_percentile",
              "completion_rate_pct", "completion_percentile",
              "engagement_rate_pct", "engagement_percentile",
              "clicks", "conversions"]
    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} videos across {len(by_platform)} platforms", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
