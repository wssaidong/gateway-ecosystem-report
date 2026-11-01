"""Source 5: Kong Gateway — `Kong/kong` 项目动向、提交内容与版本更新.

Three signals, at the same granularity as the other gateway sources:

1. 项目动向 — repo metadata (stars / open issues / pushed_at) plus the
   whole-repo commit list in window, grouped by conventional-commit scope.
   The `changelog/unreleased/` directory size is the "what is queued for
   the next release" hint.
2. 提交内容 — the commit rows themselves (same shape as the other sources,
   with `scope` instead of `plugin`).
3. 版本更新 — the latest GitHub releases plus per-version entries parsed
   from the repo-root `CHANGELOG.md`. The release *body* is boilerplate
   (download links + a pointer at the release-branch changelog), so the
   changelog file is the canonical content source.
"""
from __future__ import annotations
import datetime as _dt
import re as _re
import sys
import urllib.request as _u
from typing import Optional

from .gh import gh
from .patterns import KONG_COMMIT_RE, KONG_REF_RE  # re-exported for tests

__all__ = ["fetch_kong"]

REPO = "Kong/kong"
CHANGELOG_URL = (
    "https://raw.githubusercontent.com/Kong/kong/master/CHANGELOG.md"
)
VERSIONS_KEPT = 5
RELEASES_KEPT = 5


def _scope(msg: str) -> str:
    """`chore(ci/cd): x` → `ci/cd`; `fix: x` → `fix`; prose → `misc`."""
    m = KONG_COMMIT_RE.match(msg)
    if m:
        return m.group(2) or m.group(1)
    return "misc"


def _repo() -> dict:
    r = gh(f"repos/{REPO}") or {}
    return {
        "stars": r.get("stargazers_count"),
        "open_issues": r.get("open_issues_count"),
        "default_branch": r.get("default_branch", "master"),
        "pushed_at": r.get("pushed_at"),
    }


def _commits(since_iso: str) -> list:
    raw = gh(f"repos/{REPO}/commits?since={since_iso}&per_page=100") or []
    out = []
    for c in raw:
        msg = c["commit"]["message"].split("\n")[0]
        out.append({
            "sha": c["sha"][:7],
            "date": c["commit"]["author"]["date"],
            "author": c["commit"]["author"]["name"] or "?",
            "message": msg,
            "scope": _scope(msg),
            "url": c["html_url"],
        })
    return out


def _releases() -> list:
    rels = gh(f"repos/{REPO}/releases?per_page={RELEASES_KEPT}") or []
    rels.sort(key=lambda r: r.get("published_at", ""), reverse=True)
    return [
        {
            "tag": r.get("tag_name", ""),
            "published_at": r.get("published_at"),
            "url": r.get("html_url", ""),
        }
        for r in rels[:RELEASES_KEPT]
    ]


def parse_changelog(cl: str, max_versions: int = VERSIONS_KEPT) -> list:
    """Parse `CHANGELOG.md` into per-version entry lists.

    Grammar: `## <version>` → `### <component>` (Kong / Kong-Manager)
    → `#### <category>` (Features / Fixes / Dependencies / …)
    → `##### <area>` (Core / Plugin / Admin API / …), entries as
    `- text` lines with a trailing ` [#NNNN](url)` reference.
    """
    sections = _re.split(r"^## (\d+\.\d+\.\d+)\s*$", cl, flags=_re.MULTILINE)
    out = []
    for i in range(1, len(sections) - 1, 2):
        ver = sections[i]
        # The last version block runs to EOF and swallows non-version
        # headings (`## Previous releases`); cut at the next `## `.
        body = sections[i + 1].split("\n## ")[0]
        component = category = area = ""
        entries = []
        for line in body.splitlines():
            if line.startswith("##### "):
                area = line[6:].strip()
            elif line.startswith("#### "):
                category = line[5:].strip()
            elif line.startswith("### "):
                component = line[4:].strip()
            elif line.startswith("- "):
                text = line[2:].strip()
                ref_m = KONG_REF_RE.search(text)
                entry = {
                    "component": component,
                    "category": category,
                    "area": area,
                    "text": KONG_REF_RE.sub("", text).strip(),
                }
                if ref_m:
                    entry["ref"] = f"#{ref_m.group(1)}"
                    entry["ref_url"] = ref_m.group(2)
                entries.append(entry)
            elif entries and line.startswith(" "):
                # Continuation line: a ` [#NNNN](url)` reference lives on
                # its own indented line; other wrapped text joins the entry.
                stripped = line.strip()
                if not stripped:
                    continue
                ref_m = KONG_REF_RE.search(stripped)
                if ref_m and "ref" not in entries[-1]:
                    entries[-1]["ref"] = f"#{ref_m.group(1)}"
                    entries[-1]["ref_url"] = ref_m.group(2)
                elif not ref_m:
                    entries[-1]["text"] += " " + stripped
        if entries:
            out.append({"version": ver, "entries": entries})
        if len(out) >= max_versions:
            break
    return out


def _changelog(releases: list) -> list:
    try:
        cl = _u.urlopen(CHANGELOG_URL, timeout=20).read().decode(
            "utf-8", "ignore"
        )
    except Exception as e:
        sys.stderr.write(f"kong changelog fetch: {e}\n")
        return []
    by_tag = {r["tag"]: r.get("published_at") for r in releases}
    versions = parse_changelog(cl)
    for v in versions:
        v["date"] = by_tag.get(v["version"])
        counts: dict = {}
        for e in v["entries"]:
            counts[e["category"]] = counts.get(e["category"], 0) + 1
        v["counts"] = counts
    return versions


def _unreleased_count() -> Optional[int]:
    items = gh(f"repos/{REPO}/contents/changelog/unreleased")
    if not isinstance(items, list):
        return None
    return len(items)


def fetch_kong(days: int, today: _dt.date) -> dict:
    since = (today - _dt.timedelta(days=days)).isoformat() + "T00:00:00Z"
    releases = _releases()
    return {
        "repo": _repo(),
        "commits": _commits(since),
        "releases": releases,
        "changelog": _changelog(releases),
        "unreleased_count": _unreleased_count(),
        "since": since,
    }
