"""Source 3: Higress 插件 — commits under `plugins/`.

Parses the conventional-commit plugin scope from the commit message first
line. Filters out the `higress-release-automation[bot]` rows that have no
plugin scope (they are the release-snapshot PRs).
"""
from __future__ import annotations
import datetime as _dt

from .gh import gh
from .patterns import PLUGIN_RE  # re-exported for tests

__all__ = ["fetch_higress_plugins"]


def fetch_higress_plugins(days: int, today: _dt.date) -> list[dict]:
    since = (today - _dt.timedelta(days=days)).isoformat() + "T00:00:00Z"
    data = gh(
        f"repos/higress-group/higress/commits?path=plugins&since={since}&per_page=100"
    ) or []
    out = []
    for c in data:
        msg = c["commit"]["message"].split("\n")[0]
        m = PLUGIN_RE.match(msg)
        plugin = m.group(1) if m else "(release-automation)"
        author = c["commit"]["author"]["name"] or ""
        if "release-automation" in author and (not m or plugin in ("release", "plugins")):
            continue
        out.append({
            "sha": c["sha"][:7],
            "date": c["commit"]["author"]["date"],
            "author": author or "?",
            "message": msg,
            "plugin": plugin,
            "url": c["html_url"],
        })
    return out
