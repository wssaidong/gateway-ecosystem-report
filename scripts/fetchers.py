# Source-specific fetchers used by fetch_data.py
import sys


def fetch_apiseven_blog(days, today):
    """Return (in_window, recent_context) — context is the latest 3 articles
    even if they fall outside the window, for the report's "edge of window" hint."""
    import re as _re, json as _json, urllib.request as _u
    req = _u.Request(
        "https://www.apiseven.com/blog",
        headers={"User-Agent": "Mozilla/5.0 gateway-ecosystem-report/1.0"},
    )
    html = _u.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    m = _re.search(r'"list":\[(.*?)\]\},"__N_SSG":', html, _re.DOTALL)
    if not m:
        m = _re.search(r'"articles":\[(.*?)\],"page":', html, _re.DOTALL)
    if not m:
        sys.stderr.write("apiseven: could not find list/articles block\n")
        return [], []
    raw = m.group(1)
    raw = _re.sub(r",}\s*,", ",},", raw)
    arr = _json.loads("[" + raw + "]")
    import datetime as _dt
    cutoff = today - _dt.timedelta(days=days)
    in_window, all_rows = [], []
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


def fetch_higress_site_commits(days, today, gh):
    import datetime as _dt
    since = (today - _dt.timedelta(days=days)).isoformat() + "T00:00:00Z"
    data = gh(
        f"repos/higress-group/higress-group.github.io/commits"
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


def fetch_higress_plugins(days, today, gh, PLUGIN_RE):
    import datetime as _dt
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


def fetch_apisix_plugins(days, today, gh, NEW_PLUGIN_RE):
    import datetime as _dt, re as _re, urllib.request as _u
    since = (today - _dt.timedelta(days=days)).isoformat() + "T00:00:00Z"
    raw = gh(
        f"repos/apache/apisix/commits?path=apisix/plugins&since={since}&per_page=100"
    ) or []
    commits = []
    for c in raw:
        msg = c["commit"]["message"].split("\n")[0]
        m = PLUGIN_RE.match(msg) if False else _re.match(
            r"^(?:feat|fix|refactor|chore|docs|perf)\(([a-z][a-z0-9-]*)\):", msg
        )
        plugin = m.group(1) if m else "core"
        commits.append({
            "sha": c["sha"][:7],
            "date": c["commit"]["author"]["date"],
            "author": c["commit"]["author"]["name"] or "?",
            "message": msg,
            "plugin": plugin,
            "url": c["html_url"],
        })

    new_plugins = []
    rel = gh("repos/apache/apisix/releases?per_page=5") or []
    if rel:
        rel.sort(key=lambda r: r.get("published_at", ""), reverse=True)
        for r in rel[:3]:
            body = r.get("body", "")
            for m in NEW_PLUGIN_RE.finditer(body):
                new_plugins.append({
                    "name": m.group(2),
                    "tag": r.get("tag_name", ""),
                    "date": r.get("published_at"),
                    "source": f"release:{r.get('tag_name', '')}",
                })

    try:
        cl = _u.urlopen(
            "https://raw.githubusercontent.com/apache/apisix/master/CHANGELOG.md",
            timeout=20,
        ).read().decode("utf-8", "ignore")
    except Exception as e:
        cl = ""
        sys.stderr.write(f"apisix changelog fetch: {e}\n")

    if cl:
        sections = _re.split(r"^## (\d+\.\d+\.\d+)\s*$", cl, flags=_re.MULTILINE)
        for i in range(1, len(sections) - 1, 2):
            ver = sections[i]
            body = sections[i + 1]
            ps = _re.search(r"### Plugins\s*\n(.+?)(?=\n### |\n## |\Z)", body, _re.DOTALL)
            if not ps:
                continue
            for line in ps.group(1).splitlines():
                m = NEW_PLUGIN_RE.match(line.strip("- "))
                if m:
                    name = m.group(2)
                    if not any(p["name"] == name for p in new_plugins):
                        new_plugins.append({
                            "name": name,
                            "tag": ver,
                            "source": f"changelog:{ver}",
                            "detail": line.strip("- ").strip(),
                        })
    return {"commits": commits, "new_plugins": new_plugins}
