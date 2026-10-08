"""CLI entry point.

Two subcommands:

  python3 -m gateway_ecosystem_report --days 14 --out data.json
  python3 -m gateway_ecosystem_report render data.json --top 12 > report.md
"""
from __future__ import annotations
import argparse
import datetime
import json
import sys
from pathlib import Path

from .fetchers_apiseven import fetch_apiseven_blog
from .fetchers_higress_site import fetch_higress_site_commits
from .fetchers_higress_plugins import fetch_higress_plugins
from .fetchers_apisix import fetch_apisix_plugins
from .render_part1 import W, section_apiseven, section_higress_site
from .render_part2 import (
    section_higress_plugins,
    section_apisix_plugins,
    footer,
)


def _fetch(args: argparse.Namespace) -> int:
    today = (
        datetime.date.fromisoformat(args.date)
        if args.date else datetime.date.today()
    )
    print(f"date={today} window={args.days}d", file=sys.stderr)

    in_w, recent = fetch_apiseven_blog(args.days, today)

    payload = {
        "meta": {"date": today.isoformat(), "window_days": args.days},
        "apiseven_articles": in_w,
        "apiseven_recent": recent,
        "higress_site_commits": fetch_higress_site_commits(args.days, today),
        "higress_plugins": fetch_higress_plugins(args.days, today),
        "apisix_plugins": fetch_apisix_plugins(args.days, today),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"wrote {args.out}", file=sys.stderr)
    print(f"  apiseven articles (in window): {len(in_w)}", file=sys.stderr)
    print(f"  apiseven recent (context): {len(recent)}", file=sys.stderr)
    print(f"  higress-site commits: "
          f"{len(payload['higress_site_commits'])}", file=sys.stderr)
    print(f"  higress plugin commits: "
          f"{len(payload['higress_plugins'])}", file=sys.stderr)
    print(f"  apisix plugin commits: "
          f"{len(payload['apisix_plugins']['commits'])}", file=sys.stderr)
    print(f"  apisix new plugins: "
          f"{len(payload['apisix_plugins']['new_plugins'])}", file=sys.stderr)
    return 0


def _render(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text())
    meta = data.get("meta", {})
    days = meta.get("window_days", "?")
    today = meta.get("date", "?")
    out = [
        W.format(days=days, date=today),
        section_apiseven(
            data.get("apiseven_articles", []),
            data.get("apiseven_recent", []),
            args.top,
        ),
        section_higress_site(data.get("higress_site_commits", []), args.top),
        section_higress_plugins(data.get("higress_plugins", []), args.top),
        section_apisix_plugins(data.get("apisix_plugins", {}), args.top),
        footer(),
    ]
    sys.stdout.write("\n".join(out))
    return 0


def build_report(days: int = 14, top: int = 10,
                 today: datetime.date | None = None) -> str:
    """Programmatic entry: fetch + render in one call. Returns Markdown."""
    today = today or datetime.date.today()
    in_w, recent = fetch_apiseven_blog(days, today)
    payload = {
        "meta": {"date": today.isoformat(), "window_days": days},
        "apiseven_articles": in_w,
        "apiseven_recent": recent,
        "higress_site_commits": fetch_higress_site_commits(days, today),
        "higress_plugins": fetch_higress_plugins(days, today),
        "apisix_plugins": fetch_apisix_plugins(days, today),
    }
    out = [
        W.format(days=days, date=today.isoformat()),
        section_apiseven(payload["apiseven_articles"],
                         payload["apiseven_recent"], top),
        section_higress_site(payload["higress_site_commits"], top),
        section_higress_plugins(payload["higress_plugins"], top),
        section_apisix_plugins(payload["apisix_plugins"], top),
        footer(),
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gateway-ecosystem-report",
        description="Fetch and render the API/AI gateway ecosystem digest.",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_fetch = sub.add_parser("fetch", help="fetch data only")
    p_fetch.add_argument("--days", type=int, default=14)
    p_fetch.add_argument("--date", default=None,
                         help="today, ISO; default = system date")
    p_fetch.add_argument("--out", required=True)
    p_fetch.set_defaults(func=_fetch)

    p_render = sub.add_parser("render", help="render an existing data.json")
    p_render.add_argument("input")
    p_render.add_argument("--top", type=int, default=10)
    p_render.set_defaults(func=_render)

    # Backwards-compat: `python3 -m gateway_ecosystem_report --days N --out X`
    # is equivalent to `python3 -m gateway_ecosystem_report fetch --days N --out X`.
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--date", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--top", type=int, default=10)

    args = parser.parse_args(argv)

    if args.cmd == "fetch":
        return _fetch(args)
    if args.cmd == "render":
        return _render(args)
    # Top-level flags -> treat as fetch
    if args.out:
        return _fetch(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
