"""Source 1: API7 / Apache APISIX blog.

Fetches the apiseven.com/blog HTML, extracts the `__NEXT_DATA__` JSON
embedded by next.js, and returns both the in-window articles and the
five most-recent articles for the report's "edge of window" hint.
"""
from __future__ import annotations
import datetime as _dt
import json as _json
import re as _re
import sys
import urllib.request as _u
from typing import Any

from .patterns import LIST_RE, ARTICLES_RE  # re-exported for tests


def fetch_apiseven_blog(days: int, today: _dt.date) -> tuple[list[dict], list[dict]]:
    """Return (in_window, recent_context) for the API7 blog.

    - `in_window` is the list of articles whose `published_at` is within
      the last `days` days.
    - `recent_context` is the latest 5 articles regardless of window; the
      renderer shows this when `in_window` is empty so the report does
      not go silent on a slow-publishing week.
    """
    req = _u.Request(
        "https://www.apiseven.com/blog",
        headers={"User-Agent": "Mozilla/5.0 gateway-ecosystem-report/1.0"},
    )
    html = _u.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    m = LIST_RE.search(html) or ARTICLES_RE.search(html)
    if not m:
        sys.stderr.write("apiseven: could not find list/articles block\n")
        return [], []

    # Articles are individual objects inside the array; the next.js export
    # occasionally leaves a trailing comma between objects. Normalise that
    # before json.loads — the parser is otherwise strict.
    raw = m.group(1)
    raw = _re.sub(r",}\s*,", ",},", raw)
    arr = _json.loads("[" + raw + "]")

    cutoff = today - _dt.timedelta(days=days)
    in_window: list[dict] = []
    all_rows: list[dict] = []
    for a in arr:
        d = a.get("published_at", "")
        try:
            dt = _dt.date.fromisoformat(d)
        except (ValueError, TypeError):
            continue
        row = {
            "title": a.get("title", ""),
            "slug": a.get("slug", ""),
            "published_at": d,
            "tags": a.get("tags", []),
            "url": "https://www.apiseven.com" + a.get("slug", ""),
        }
        all_rows.append(row)
        if dt >= cutoff:
            in_window.append(row)
    in_window.sort(key=lambda x: x["published_at"], reverse=True)
    all_rows.sort(key=lambda x: x["published_at"], reverse=True)
    return in_window, all_rows[:5]
