#!/usr/bin/env python3
"""Fetch the last N days of API/AI gateway ecosystem signals to a single JSON file.

Sources:
  1. API7 blog                  -> articles[]
  2. Higress 官网博客 (ai 分支) -> commits in src/content/blog
  3. Higress 插件               -> commits in plugins/
  4. APISIX 插件                -> commits in apisix/plugins/ + CHANGELOG 里的 ### Plugins 段

Usage:
  python3 fetch_data.py --days 14 --out report.json [--date 2026-10-08]
"""
from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from pathlib import Path
from typing import Any
import urllib.request

GH = ["gh", "api", "-H", "Accept: application/vnd.github+json"]


def gh(path: str) -> Any:
    out = subprocess.run(GH + [path], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


PLUGIN_RE = re.compile(r"^(?:feat|fix|refactor|chore|docs|perf)\(([a-z][a-z0-9-]*)\):")
NEW_PLUGIN_RE = re.compile(
    r"^feat(?:\(([a-z][a-z0-9-]*)\))?:\s*add the [`'\"]([a-z][a-z0-9-]*)[`'\"][^.]*plugin"
)

from fetchers import (
    fetch_apiseven_blog,
    fetch_higress_site_commits,
    fetch_higress_plugins,
    fetch_apisix_plugins,
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--date", default=None,
                   help="today, ISO; default = system date")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    today = (datetime.date.fromisoformat(args.date)
             if args.date else datetime.date.today())
    print(f"date={today} window={args.days}d", file=sys.stderr)

    payload = {
        "meta": {"date": today.isoformat(), "window_days": args.days},
        "apiseven_articles": [],
        "apiseven_recent": [],
        "higress_site_commits": fetch_higress_site_commits(args.days, today, gh),
        "higress_plugins": fetch_higress_plugins(
            args.days, today, gh, PLUGIN_RE),
        "apisix_plugins": fetch_apisix_plugins(
            args.days, today, gh, NEW_PLUGIN_RE),
    }
    in_w, recent = fetch_apiseven_blog(args.days, today)
    payload["apiseven_articles"] = in_w
    payload["apiseven_recent"] = recent
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"wrote {args.out}", file=sys.stderr)
    print("  apiseven articles (in window):", len(payload["apiseven_articles"]))
    print("  apiseven recent (context):", len(payload["apiseven_recent"]))
    print("  higress-site commits:", len(payload["higress_site_commits"]))
    print("  higress plugin commits:", len(payload["higress_plugins"]))
    print("  apisix plugin commits:", len(payload["apisix_plugins"]["commits"]))
    print("  apisix new plugins:", len(payload["apisix_plugins"]["new_plugins"]))


if __name__ == "__main__":
    main()
