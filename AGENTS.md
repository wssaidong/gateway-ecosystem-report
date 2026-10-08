# AGENTS.md

> Full reference for `gateway-ecosystem-report` skill.
> This file is loaded by an agent **only after** `SKILL.md` activates it.
> Keep `SKILL.md` terse; put detail here.

# AGENTS.md

> Full reference for `gateway-ecosystem-report` skill.
> This file is loaded by an agent **only after** `SKILL.md` activates it.
> Keep `SKILL.md` terse; put detail here.

## Data Schema

The fetcher writes one JSON file with this shape:

```json
{
  "meta": {
    "date": "2026-10-08",
    "window_days": 14
  },
  "apiseven_articles": [
    {
      "title": "...",
      "slug": "/blog/...",
      "published_at": "2026-09-22",
      "tags": ["API7 网关", "..."],
      "url": "https://www.apiseven.com/blog/..."
    }
  ],
  "apiseven_recent": [ /* same shape, latest 5, even if outside window */ ],
  "higress_site_commits": [
    {
      "sha": "22975c8",
      "date": "2026-10-04T10:43:49Z",
      "author": "澄潭",
      "message": "chore(release): promote mcp-server 2.0.3 to stable for 2.2.5 (#4967)",
      "url": "https://github.com/.../commit/..."
    }
  ],
  "higress_plugins": [ /* same shape as higress_site_commits, with extra "plugin" key */ ],
  "apisix_plugins": {
    "commits": [ /* same shape */ ],
    "new_plugins": [
      {
        "name": "openapi-to-mcp",
        "tag": "3.19.0",
        "date": "2026-09-28T05:13:59Z",
        "source": "changelog:3.19.0",
        "detail": "feat: add the `openapi-to-mcp` plugin, serving..."
      }
    ]
  }
}
```

Backwards-compat: missing keys must be treated as empty, not as errors. The
renderer is defensive about every key.


## API Endpoints Used

All calls are GETs. The fetcher authenticates via the local `gh` CLI, which
applies its own stored token and returns only the API response.

| # | URL | Notes |
|---|-----|-------|
| 1 | `https://www.apiseven.com/blog` (HTML) | next.js static export; embeds `__NEXT_DATA__` JSON |
| 2 | `https://api.github.com/repos/higress-group/higress-group.github.io/commits?path=src/content/blog&since=<ISO>&sha=ai&per_page=100` | `sha=ai` is **required** (default branch is `ai`, not `main`) |
| 3 | `https://api.github.com/repos/higress-group/higress/commits?path=plugins&since=<ISO>&per_page=100` | `path=plugins` filters at the API level |
| 4a | `https://api.github.com/repos/apache/apisix/commits?path=apisix/plugins&since=<ISO>&per_page=100` | path-scoped |
| 4b | `https://api.github.com/repos/apache/apisix/releases?per_page=5` | bodies can mention new plugins |
| 4c | `https://raw.githubusercontent.com/apache/apisix/master/CHANGELOG.md` | canonical source for new-plugin announcements |

`since` is an ISO-8601 UTC timestamp `YYYY-MM-DDTHH:MM:SSZ`. The fetcher
computes it as `today - days` at midnight UTC.

## Network Constraints

This skill was developed and tested from a network that **blocks direct
HTTPS to `github.com:443`** but **allows HTTPS to `api.github.com`** and
**SSH to `github.com:22`**. Many of the choices below were made to work
in that environment. If your network is unrestricted, you can ignore the
workarounds.

| Need | Workaround | Why |
|------|------------|-----|
| Read repo data | Use `gh api` (routes to `api.github.com`) | direct `curl https://github.com/...` is blocked |
| Clone a repo | Use SSH, e.g. `git@github.com:org/repo.git` | HTTPS clone is blocked |
| Push a branch | Use SSH, same as above | same |
| Read raw files | `https://raw.githubusercontent.com/...` works | Vercel CDN, not blocked |
| Read blog HTML | `curl https://www.apiseven.com/blog` | not on the github.com block list |

If the user's network is unrestricted, the workarounds still work but are
slower; you do not need to switch them off.


## Per-Source Recipes

### 1. API7 / Apache APISIX blog

```
GET https://www.apiseven.com/blog
```

The HTML is a next.js static export. The article list lives in the
`__NEXT_DATA__` JSON block, under `pageProps.list` (current schema) or
`pageProps.articles` (legacy schema). The block opens with `"list":[` and
closes with `}]},"__N_SSG":`. Between the brackets is a JSON array of
article objects with `title`, `slug`, `published_at`, `tags`, etc.

Strategy:

1. Fetch the page with a `User-Agent` header (the site sometimes returns a
   challenge page to a bare `urllib` default UA).
2. Match the list block with one of:
   - `"list":\[(.*?)\]\},"__N_SSG":`
   - `"articles":\[(.*?)\],"page":` (fallback for older snapshots)
3. Normalise the inner string (the parser is forgiving about trailing commas
   between objects — `,}\s*,` becomes `,},`).
4. Parse the array, filter by `published_at >= today - days`, and also keep
   the 5 most-recent articles as `apiseven_recent` for the "edge of window"
   hint when the strict window is empty.

Tags come back as Chinese strings already. The `tags` array is what the
site's UI uses to colour the article chip, so do not transform it.

### 2. Higress 官网博客

```
GET https://api.github.com/repos/higress-group/higress-group.github.io/commits
    ?path=src/content/blog
    &since=<ISO>
    &sha=ai
    &per_page=100
```

The site is an Astro project. New content is added as `.md` files under
`src/content/blog/`, so `path=src/content/blog` is the right filter. The
default branch is `ai`; without `sha=ai` the call 404s.

The Astro commit is a strong signal of "new article" — there is no separate
publish date beyond the commit date.

Strategy: just list the commits, no further parsing needed. If the count
is 0, the section is empty; show a friendly "no commits in window" message
and link to the upstream release notes for the corresponding gateway
version.


### 3. Higress 插件

```
GET https://api.github.com/repos/higress-group/higress/commits
    ?path=plugins
    &since=<ISO>
    &per_page=100
```

Higress plugins live in `plugins/`. A commit's first line is conventionally
`<type>(<plugin-name>): <subject>`, e.g. `feat(mcp-server): add foo`,
`fix(ai-proxy): bar`. The fetcher extracts the plugin name from the
parenthesised segment.

Known plugin names to expect (not exhaustive — the list grows): `mcp-server`,
`mcp-session`, `mcp-stock-history-data`, `ai-proxy`, `ai-cache`,
`ai-rag`, `ai-statistics`, `ai-data-masking`, `ai-security-guard`,
`ai-load-balancer`, `ai-endpoint-picker`, `ai-token-ratelimit`,
`ai-search`, `ext-auth`, `hmac-auth-apisix`, `request-block`,
`traffic-tag`, `response-cache`, `frontend-gray`, `model-router`.

There is also a noisy contributor: the `higress-release-automation[bot]`
account, which creates the snapshot releases. Its commit messages usually
have no parenthesised scope, so the parser records them as
`(release-automation)`. The renderer groups them and shows the count but
omits the individual rows from the "Top commits" list.

Strategy:

1. Fetch the commit list.
2. For each commit, parse the first line of the message with
   `^(?:feat|fix|refactor|chore|docs|perf)\(([a-z][a-z0-9-]*)\):` to get
   the plugin scope.
3. Drop rows where the author is `higress-release-automation[bot]` **and**
   the scope is one of `{release, plugins}` (these are the release-snapshot
   PRs and are not plugin changes).
4. Group by plugin and sort by count, then by date.

### 4. Apache APISIX 插件

Two signals:

```
GET https://api.github.com/repos/apache/apisix/commits
    ?path=apisix/plugins
    &since=<ISO>
    &per_page=100
```

```
GET https://raw.githubusercontent.com/apache/apisix/master/CHANGELOG.md
```

Plus the latest 3 GitHub releases (which sometimes include a body that
mentions new plugins).

The commit path is `apisix/plugins/` and the scope grammar is identical to
Higress. New plugins are not introduced as commits on this path, though —
they land in `CHANGELOG.md` under a version's `### Plugins` section with a
line starting with `feat: add the <name> plugin`.

Strategy:

1. Fetch the commit list and parse plugin scope the same way as Higress.
2. Fetch `CHANGELOG.md` and split on `^## (\d+\.\d+\.\d+)\s*$`. Walk the
   top 5 versions, look for `### Plugins` sections, and for each line
   starting with `- feat: add the <name> plugin`, record the plugin.
3. Fetch the latest 3 GitHub releases; for each release body, also look
   for `feat: add the <name> plugin` lines. Deduplicate against the
   changelog list.
4. In the renderer, the "new plugin" list always comes from step 2+3; the
   commit list is the "Top commits" supplement.

### 5. The OpenAI/Anthropic helpers

The skill does not call any OpenAI / Anthropic API. All summarisation is
done by the calling agent. This keeps the skill free of LLM cost and
deterministic — the report is the data, not an interpretation.


## Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| All sections empty | `gh` not authenticated | run `gh auth login` |
| `higress-site` is 0 commits but the user expects articles | the site is in maintenance | link the user to the upstream `release-notes/<version>.md` |
| `apisix_plugins.commits` is non-zero but `new_plugins` is empty | no release in window | check the latest GitHub release for an out-of-window new plugin |
| `apiseven_articles` is empty but `apiseven_recent` is non-empty | strict window excludes recent content | tell the user to widen `--days` |
| HTTP 403 from `api.github.com` | rate limit hit | wait or use a different token; auth raises limit to 5000/h |
| HTML for `apiseven.com/blog` has no `__NEXT_DATA__` | bot protection triggered (rare) | retry with a fuller `User-Agent` and `Accept-Language: zh-CN` |
| `gh api` 404s on the higress site | forgot `sha=ai` | the default branch is `ai`, not `main` |

## Security

- The skill does not write to any path other than the file(s) you pass
  with `--out` / as the redirect target.
- It does not run any code from fetched content.
- It does not exfiltrate the `gh` token; `gh api` keeps the token in its
  own process.
- The fetcher reads only public repos. Do not point it at a private
  `apisix` or `higress` fork; the rate limit will trip and the result
  will be the same as a public fetch with a private quota deduction.

## Compatibility

- Python: 3.9+ (uses `from __future__ import annotations`, PEP 604 unions
  via `str | None` is avoided for portability).
- OS: any. No platform-specific calls.
- Network: needs `api.github.com` and `www.apiseven.com` reachable; the
  workarounds in §"Network Constraints" handle the common case where
  `github.com` is blocked.
- Optional: `gh` CLI on PATH and authenticated. If `gh` is missing, the
  fetcher will fall back to anonymous API calls, which still works for
  these public repos but lowers the rate limit to 60/h.

## How the Skill Was Built

This skill was authored end-to-end by an autonomous coding agent in one
session on 2026-10-08. The full development process is in the git history
of the `wssaidong/gateway-ecosystem-report` repo on GitHub. The first
report the agent produced with this skill (which doubles as the example
fixture) is `examples/2026-10-08-ecosystem.md`.

<!-- _Generated by stitching AGENTS_part1..5. Do not edit the parts directly._ -->
