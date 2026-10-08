# gateway-ecosystem-report

[![skills.sh](https://skills.sh/b/wssaidong/gateway-ecosystem-report)](https://skills.sh/wssaidong/gateway-ecosystem-report)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](./pyproject.toml)

A Chinese weekly digest of the API/AI gateway ecosystem. Pulls the last 14 days
from the API7 / AISIX blog, the Higress site, the Higress plugin repository,
and the Apache APISIX plugin repository, then renders a single Markdown report.

## Install

```bash
npx skills add wssaidong/gateway-ecosystem-report
```

Or use it without installing:

```bash
npx skills use wssaidong/gateway-ecosystem-report --agent claude-code
```

Supports Claude Code, Codex, Cursor, GitHub Copilot, Windsurf, Gemini, Cline,
and 70+ other agents (see the [skills.sh agent list](https://www.skills.sh/)).

## What it covers

| Source | What it tracks |
|--------|----------------|
| [API7 / AISIX blog](https://www.apiseven.com/blog) | new articles on the API7 gateway or AISIX AI gateway |
| [Higress 官网博客](https://higress-group.github.io) (`ai` branch) | new entries under `src/content/blog/` |
| [Higress 插件仓库](https://github.com/higress-group/higress) | commits under `plugins/` |
| [Apache APISIX 仓库](https://github.com/apache/apisix) | commits under `apisix/plugins/` + new plugins announced in `CHANGELOG.md` |

## Quickstart (CLI)

```bash
git clone https://github.com/wssaidong/gateway-ecosystem-report
cd gateway-ecosystem-report
pip install -e .

# 1. fetch the data
python3 -m gateway_ecosystem_report --days 14 \
    --out examples/2026-10-08-data.json

# 2. render the report
python3 -m gateway_ecosystem_report render \
    examples/2026-10-08-data.json --top 12 \
    > examples/2026-10-08-ecosystem.md
```

A pre-generated sample is in `examples/2026-10-08-ecosystem.md`.

## Quickstart (Python)

```python
from gateway_ecosystem_report import build_report
md = build_report(days=14, top=10)
print(md)
```

## What "good output" looks like

```markdown
# 🌐 API/AI 网关生态周报

_数据源：API7 博客、Higress 官网、Higress 仓库、Apache APISIX 仓库；窗口 = 近 14 天（截至 2026-10-08）。_

## 1️⃣ API7 / Apache APISIX 博客
…
## 2️⃣ Higress 官网博客 (higress-group.github.io)
…
## 3️⃣ Higress 插件 (plugins/ 路径近 2 周提交)
共 43 个提交；按插件聚合计数：
  - (release-automation): 24
  - mcp-session: 3
  - ai-proxy: 3
  - mcp-server: 3
…
## 4️⃣ Apache APISIX 插件
### 🆕 新增插件（来自 CHANGELOG/release notes）
- openapi-to-mcp (in 3.19.0, changelog:3.19.0)
- websocket-proxy (in 3.19.0, changelog:3.19.0)
```

## Repository layout

```
gateway-ecosystem-report/
├── SKILL.md                  # the skill itself (loaded by agents)
├── AGENTS.md                 # full reference, loaded only after activation
├── README.md                 # this file
├── LICENSE                   # MIT
├── CHANGELOG.md              # version history
├── metadata.json             # skills.sh indexer metadata
├── pyproject.toml            # build config + console script
├── src/gateway_ecosystem_report/
│   ├── __init__.py
│   ├── __main__.py           # `python3 -m gateway_ecosystem_report`
│   ├── cli.py                # argparse, build_report()
│   ├── patterns.py           # shared regex patterns
│   ├── gh.py                 # `gh api` wrapper
│   ├── fetchers_*.py         # one file per data source
│   ├── render_part1.py       # apiseven + higress-site sections
│   ├── render_part2.py       # plugin sections
│   └── py.typed
├── tests/
│   ├── test_patterns.py      # regex unit tests (stdlib)
│   ├── test_render.py        # end-to-end render tests (stdlib)
│   └── __init__.py
└── examples/
    ├── 2026-10-08-data.json      # real fetch output
    └── 2026-10-08-ecosystem.md   # real rendered report
```

## Running the tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

The test suite is stdlib-only — no `pytest` required.

## Network constraints

This skill was developed and tested from a network where direct HTTPS to
`github.com:443` is blocked but `api.github.com` and `github.com:22` (SSH)
are reachable. All GitHub API calls go through `gh api`; cloning and
pushing use SSH. If your network is unrestricted, the same code works
without modification.

## Contributing

PRs welcome. The most useful contributions:

1. **New data sources** — write a new `fetchers_<source>.py` and a
   matching `render_*` section, then add a `test_*.py` case using
   fixture data.
2. **Better filters** — the current "new plugin" detector for APISIX
   only looks at `CHANGELOG.md`'s `### Plugins` section; if you have a
   better signal (e.g. `apisix/plugins/` directory diff between tags),
   wire it in `fetchers_apisix.py`.
3. **Translations** — `SKILL.md` is in English (per the agent skills
   spec). The rendered report is intentionally Chinese. If you want
   another language for the rendered report, refactor the strings in
   `render_part1.py` / `render_part2.py` to a translations module.

## License

MIT — see [`LICENSE`](./LICENSE).
