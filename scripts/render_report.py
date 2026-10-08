#!/usr/bin/env python3
"""Render a fetched-data JSON to a Markdown ecosystem report (Chinese).

Usage:
  python3 render_report.py data.json > out.md
  python3 render_report.py data.json --top 5   # limit each section
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from collections import Counter

from render_part1 import section_apiseven, section_higress_site, W
from render_part2 import section_higress_plugins, section_apisix_plugins, footer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--top", type=int, default=10)
    args = p.parse_args()
    data = json.loads(Path(args.input).read_text())
    meta = data["meta"]
    days = meta["window_days"]
    today = meta["date"]
    out = []
    out.append(W.format(days=days, date=today))
    out.append(section_apiseven(
        data["apiseven_articles"], data.get("apiseven_recent", []),
        args.top))
    out.append(section_higress_site(data["higress_site_commits"], args.top))
    out.append(section_higress_plugins(data["higress_plugins"], args.top))
    out.append(section_apisix_plugins(data["apisix_plugins"], args.top))
    out.append(footer())
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
