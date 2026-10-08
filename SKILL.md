---
name: gateway-ecosystem-report
description: 抓取 API/AI 网关生态 2 周动态生成中文周报。覆盖 API7/AISIX、Higress、APISIX.
license: MIT
metadata:
  author: wssaidong
  version: "1.0.0"
  argument-hint: [days=14]
compatibility: Requires `gh` CLI authenticated, Python 3.9+, network access to api.github.com and www.apiseven.com.
---

# Gateway Ecosystem Report

Generate a Chinese weekly digest of activity in the API/AI gateway ecosystem
over the last 14 days. Covers the four high-signal sources for the open-source
gateways that ship most of the world's API traffic.

## When to Use

Activate this skill when the user asks for any of:

- "API/AI 网关周报" / "API 网关生态周报" / "网关最近动态"
- "Higress 插件最近更新了啥" / "APISIX 新插件"
- "API7 / AISIX 最新博客" / "网关生态动态"
- A weekly ecosystem status report on these four projects

Do NOT activate for: deploying these gateways, configuring individual plugins,
performance tuning, or comparing gateway features. Those have their own skills.

## Data Sources

| # | Source | Path / URL | Window default |
|---|--------|-----------|----------------|
| 1 | API7 / Apache APISIX blog | `https://www.apiseven.com/blog` | 14 days |
| 2 | Higress 官网博客 | `https://higress-group.github.io` (`ai` branch, `src/content/blog`) | 14 days |
| 3 | Higress 插件 | `https://github.com/higress-group/higress` (path `plugins/`) | 14 days |
| 4 | Apache APISIX 插件 | `https://github.com/apache/apisix` (path `apisix/plugins/` + `CHANGELOG.md`) | 14 days |

For a full reference on the API endpoints, common pitfalls, and the parsing
details for each source, see [`AGENTS.md`](AGENTS.md).

## How to Use

### One-shot via the bundled CLI

```bash
# from the skill repo root
python3 -m gateway_ecosystem_report \
    --days 14 \
    --out reports/$(date +%F)-data.json

python3 -m gateway_ecosystem_report render \
    reports/$(date +%F)-data.json \
    --top 12 > reports/$(date +%F)-ecosystem.md
```

### Step by step (when the user wants to read along)

1. **Fetch** data for the 4 sources into one JSON file.
2. **Render** the JSON to a Chinese Markdown report.
3. **Surface** the report to the user; offer to widen `--days` if every section
   is empty (very common for the Higress site blog, which ships no new content
   for weeks at a time).

### Programmatic (when called from another agent)

```python
from gateway_ecosystem_report import build_report

md = build_report(days=14, top=10)
print(md)
```

## Report Shape

The Markdown report always has four sections, in this order:

1. **API7 / Apache APISIX 博客** — recent articles (or "edge of window"
   context if the strict window is empty).
2. **Higress 官网博客** — `src/content/blog/` commits on `ai` branch.
3. **Higress 插件** — commits under `plugins/`, grouped by plugin name.
4. **Apache APISIX 插件** — `apisix/plugins/` commits plus newly announced
   plugins from `CHANGELOG.md`.

If any section is empty, the report still emits the section header and an
explanation pointing at the next action the user can take (widen the window,
check the upstream release notes, etc.).

## Common Edge Cases

- **APISIX 多数 commit 是 bug fix** — 14 天内"新增插件"几乎不会出现。要查"上
  一个 release 引入了什么新插件"，用 `CHANGELOG.md` 的 `### Plugins` 段。
- **Higress 官网博客窗口内可能为零** — 站点 Astro 在 `ai` 分支维护，文章
  发布节奏稀疏。新的功能内容在 `higress-group/higress` 的 `release-notes/` 下。
- **`api.github.com` 是绕过直连墙的关键** — 在受限网络里，`curl github.com`
  不通但 `gh api`（走 api.github.com）通；git push 走 SSH（22 端口）通。
- **API7 的 AI 网关产品叫 AISIX** — 不是 APISIX；博客站
  `https://www.apiseven.com/blog` 同时承载 API7 网关和 AISIX 两条产品线的文章。
- **apiseven 博客列表用 next.js 静态导出** — HTML 嵌入的 `__NEXT_DATA__` JSON
  是唯一可信源；不要再调列表 API（404）。列表 key 是 `pageProps.list`（旧版
  `pageProps.articles`），块尾是 `}]},"__N_SSG":`。
- **higress-group.github.io 默认分支是 `ai`** — 不是 `main`；API `contents`
  调用必须 `?ref=ai`，否则 404。

## Output Contract

- `data.json` is a stable JSON schema (see `AGENTS.md` § "Data Schema").
- `ecosystem.md` is valid GFM using only headers, lists, and code blocks.
- The CLI is idempotent: re-running on the same day overwrites the same file
  paths.

## Full Reference

For API endpoint details, the data schema, and the complete edge-case list,
see [`AGENTS.md`](AGENTS.md).
