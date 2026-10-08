---
name: gateway-ecosystem-report
description: 抓取 API/AI 网关生态近 2 周信号并生成中文报告。覆盖 API7 博客、Higress 官网博客与插件仓库、Apache APISIX 插件仓库。当用户要求生成"网关生态周报"、"API 网关生态动态"、"Higress/APISIX 最新进展"时调用。
---

# Gateway Ecosystem Report

把"近 2 周"作为硬性窗口（默认 = 当天 - 14 天）。数据源全部走 GitHub API（`gh api`，api.github.com 在受限网络下通常可用），不要 `git clone`，也不要直接 `curl github.com`。

## 4 个数据源

1. **API7 / Apache APISIX 博客** — `curl -sL https://www.apiseven.com/blog`，从嵌入的 `__NEXT_DATA__` JSON 中提取 `articles[]`，按 `published_at` 过滤近 2 周。
2. **Higress 官网** — `gh api repos/higress-group/higress-group.github.io/commits?path=src/content/blog&since=<14d_ago>&sha=ai&per_page=100`，拿到 `src/content/blog` 路径下的近 2 周提交（默认分支是 `ai`，不是 `main`）。
3. **Higress 插件** — `gh api repos/higress-group/higress/commits?path=plugins&since=<14d_ago>&per_page=100`；从提交信息里识别 `feat(<plugin>):` / `fix(<plugin>):` / 新插件名（`mcp-server`、`ai-endpoint-picker`、`ai-load-balancer` 等）。
4. **Apache APISIX 插件** — `gh api repos/apache/apisix/commits?path=apisix/plugins&since=<14d_ago>&per_page=100`；新插件名 = changelog 里 `### Plugins` 段下 `feat: add the <name> plugin` 的条目；额外扫 `apisix/plugins/` 目录确认是否多出新子目录。

## 关键陷阱

- **higress-group.github.io 默认分支是 `ai`**，不是 `main` — 走 `contents` API 时必须带 `?ref=ai`，否则 404。
- **higress-group.github.io 没有公开发新文章**的时候也会有提交 — 必须看 `path=src/content/blog` 而不是仓库根。
- **apisix 多数 commit 是 bug fix**，新插件只出现在 minor/major release 的 `CHANGELOG.md` 里。同步拉 `https://raw.githubusercontent.com/apache/apisix/master/CHANGELOG.md` 抓 `## X.Y.Z` 段下 `### Plugins` 子节里的 `feat: add the <plugin> plugin`。
- **`aisix` vs `apisix`** — API7 的新 AI 网关产品叫 **AISIX**（不是 APISIX），按文章标题区分。
- **GitHub API 速率** — 5000/小时，auth 后的 `gh api` 默认共享用户配额，足够用。
- **apiseven 博客列表用 next 静态导出**，HTML 里 `__NEXT_DATA__` 包含完整 `articles[]`，不要再调列表 API。

## 输出

调用方负责渲染 Markdown 报告；本 skill 提供 `scripts/fetch_data.py`（抓数据 → JSON）和 `scripts/render_report.py`（JSON → Markdown）两个可执行入口。
