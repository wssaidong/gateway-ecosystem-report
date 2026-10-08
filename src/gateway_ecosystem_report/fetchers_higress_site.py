"""Source 2: Higress 官网博客 — `src/content/blog/` commits on `ai` branch.

The site is an Astro project; the default branch is `ai` (not `main`).
"""
from __future__ import annotations
import datetime as _dt

from .gh import gh


def fetch_higress_site_commits(days: int, today: _dt.date) -> list[dict]:
    since = (today - _dt.timedelta(days=days)).isoformat() + "T00:00:00Z"
    data = gh(
        "repos/higress-group/higress-group.github.io/commits"
        f"?path=src/content/blog&since={since}&sha=ai&per_page=100"
    ) or []
    out = []
    for c in data:
        out.append({
            "sha": c["sha"][:7],
            "date": c["commit"]["author"]["date"],
            "author": (c["commit"]["author"]["name"]
                       or c.get("author", {}).get("login", "?")),
            "message": c["commit"]["message"].split("\n")[0],
            "url": c["html_url"],
        })
    return out
