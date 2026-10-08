"""Source 4: Apache APISIX 插件 — commits under `apisix/plugins/` + CHANGELOG.

Two signals:

1. Per-commit data from `path=apisix/plugins&since=…` (same shape as the
   Higress plugin fetcher).
2. Newly announced plugins from `CHANGELOG.md`'s `### Plugins` section
   under each `## X.Y.Z` heading, deduplicated against the latest 3
   GitHub release bodies.
"""
from __future__ import annotations
import datetime as _dt
import re as _re
import sys
import urllib.request as _u

from .gh import gh
from .patterns import PLUGIN_RE, NEW_PLUGIN_RE  # re-exported for tests


def _plugin_scope(msg: str) -> str:
    m = PLUGIN_RE.match(msg)
    return m.group(1) if m else "core"


def _commits(since_iso: str) -> list[dict]:
    raw = gh(
        f"repos/apache/apisix/commits?path=apisix/plugins&since={since_iso}&per_page=100"
    ) or []
    out = []
    for c in raw:
        msg = c["commit"]["message"].split("\n")[0]
        out.append({
            "sha": c["sha"][:7],
            "date": c["commit"]["author"]["date"],
            "author": c["commit"]["author"]["name"] or "?",
            "message": msg,
            "plugin": _plugin_scope(msg),
            "url": c["html_url"],
        })
    return out


def _new_plugins_from_releases() -> list[dict]:
    rels = gh("repos/apache/apisix/releases?per_page=5") or []
    rels.sort(key=lambda r: r.get("published_at", ""), reverse=True)
    out = []
    for r in rels[:3]:
        body = r.get("body", "")
        for m in NEW_PLUGIN_RE.finditer(body):
            out.append({
                "name": m.group(2),
                "tag": r.get("tag_name", ""),
                "date": r.get("published_at"),
                "source": f"release:{r.get('tag_name', '')}",
            })
    return out


def _new_plugins_from_changelog() -> list[dict]:
    try:
        cl = _u.urlopen(
            "https://raw.githubusercontent.com/apache/apisix/master/CHANGELOG.md",
            timeout=20,
        ).read().decode("utf-8", "ignore")
    except Exception as e:
        sys.stderr.write(f"apisix changelog fetch: {e}\n")
        return []
    sections = _re.split(r"^## (\d+\.\d+\.\d+)\s*$", cl, flags=_re.MULTILINE)
    out = []
    for i in range(1, len(sections) - 1, 2):
        ver = sections[i]
        body = sections[i + 1]
        ps = _re.search(r"### Plugins\s*\n(.+?)(?=\n### |\n## |\Z)", body, _re.DOTALL)
        if not ps:
            continue
        for line in ps.group(1).splitlines():
            m = NEW_PLUGIN_RE.match(line.strip("- "))
            if m:
                out.append({
                    "name": m.group(2),
                    "tag": ver,
                    "source": f"changelog:{ver}",
                    "detail": line.strip("- ").strip(),
                })
    return out


def fetch_apisix_plugins(days: int, today: _dt.date) -> dict:
    since = (today - _dt.timedelta(days=days)).isoformat() + "T00:00:00Z"
    commits = _commits(since)

    # Deduplicate new-plugin announcements across release bodies and CHANGELOG.
    seen: dict[str, dict] = {}
    for p in _new_plugins_from_releases() + _new_plugins_from_changelog():
        if p["name"] not in seen:
            seen[p["name"]] = p
    return {"commits": commits, "new_plugins": list(seen.values())}
