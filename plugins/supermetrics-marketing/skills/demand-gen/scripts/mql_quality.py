#!/usr/bin/env python3
"""
Lead quality measurement by source.

Computes lead → MQL → SQL conversion rates per source, plus time-to-MQL
and total spend per source. Surfaces sources producing volume without
quality.

Expected CSV columns:
    - source (lead source / channel name)
    - lead_created_date
    - mql_date (empty if never reached MQL)
    - sql_date (empty if never reached SQL)
    - spend (optional, can also be passed via separate spend CSV)

Usage:
    python mql_quality.py leads.csv --output quality.csv
    python mql_quality.py leads.csv --spend-csv spend.csv --output quality.csv
"""

import argparse
import sys
import csv
from collections import defaultdict
from datetime import datetime
from statistics import median


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Leads CSV")
    p.add_argument("--source-col", default="source")
    p.add_argument("--spend-csv", default=None, help="Optional separate spend CSV (channel,spend)")
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
    sources = defaultdict(lambda: {"leads": 0, "mqls": 0, "sqls": 0, "ttmqls": [], "spend": 0.0})

    with open(args.input, newline="") as f:
        for r in csv.DictReader(f):
            src = r.get(args.source_col, "(unknown)")
            sources[src]["leads"] += 1
            lead_date = parse_date(r.get("lead_created_date") or r.get("lead_date"))
            mql_date = parse_date(r.get("mql_date"))
            sql_date = parse_date(r.get("sql_date"))
            if mql_date:
                sources[src]["mqls"] += 1
                if lead_date:
                    sources[src]["ttmqls"].append((mql_date - lead_date).days)
            if sql_date:
                sources[src]["sqls"] += 1
            sources[src]["spend"] += to_float(r.get("spend"))

    if args.spend_csv:
        with open(args.spend_csv, newline="") as f:
            for r in csv.DictReader(f):
                src = r.get("source") or r.get("channel") or ""
                if src in sources:
                    sources[src]["spend"] = to_float(r.get("spend") or r.get("cost"))

    out_rows = []
    for src, d in sources.items():
        mql_rate = d["mqls"] / d["leads"] * 100 if d["leads"] > 0 else 0
        sql_rate = d["sqls"] / d["mqls"] * 100 if d["mqls"] > 0 else 0
        lead_to_sql = d["sqls"] / d["leads"] * 100 if d["leads"] > 0 else 0
        cpl = d["spend"] / d["leads"] if d["leads"] > 0 else None
        cpmql = d["spend"] / d["mqls"] if d["mqls"] > 0 else None
        median_ttmql = median(d["ttmqls"]) if d["ttmqls"] else None

        out_rows.append({
            "source": src,
            "leads": d["leads"],
            "mqls": d["mqls"],
            "sqls": d["sqls"],
            "mql_rate_pct": round(mql_rate, 1),
            "sql_rate_pct": round(sql_rate, 1),
            "lead_to_sql_rate_pct": round(lead_to_sql, 1),
            "median_days_to_mql": median_ttmql if median_ttmql is not None else "n/a",
            "spend": round(d["spend"], 2),
            "cpl": round(cpl, 2) if cpl is not None else "n/a",
            "cost_per_mql": round(cpmql, 2) if cpmql is not None else "n/a",
        })

    out_rows.sort(key=lambda r: -r["lead_to_sql_rate_pct"])

    fields = ["source", "leads", "mqls", "sqls", "mql_rate_pct", "sql_rate_pct", "lead_to_sql_rate_pct",
              "median_days_to_mql", "spend", "cpl", "cost_per_mql"]
    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    else:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} sources to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
