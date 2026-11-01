"""Plugin and Kong sections of the renderer."""
from __future__ import annotations
from collections import Counter


def section_higress_plugins(commits: list, top: int) -> str:
    out = ["## 3️⃣ Higress 插件 (`plugins/` 路径近 2 周提交)\n"]
    if not commits:
        out.append("> 近 2 周 **没有针对 `plugins/` 路径的提交**。\n")
        return "\n".join(out)
    out.append(f"共 **{len(commits)}** 个提交；按插件聚合计数：\n")
    by_plugin = Counter(c["plugin"] for c in commits)
    for p, n in by_plugin.most_common(8):
        out.append(f"  - `{p}`: {n}")
    out.append("")
    out.append("### Top commits\n")
    for c in commits[:top]:
        out.append(
            f"- `{c['date'][:10]}` · `{c['plugin']}` · "
            f"{c['author']} · {c['message']} ([{c['sha']}]({c['url']}))"
        )
    out.append("")
    return "\n".join(out)


def section_apisix_plugins(data: dict, top: int) -> str:
    commits = data.get("commits", [])
    new_plugins = data.get("new_plugins", [])
    out = ["## 4️⃣ Apache APISIX 插件\n"]
    if new_plugins:
        out.append("### 🆕 新增插件（来自 CHANGELOG/release notes）\n")
        for p in new_plugins:
            tag = p.get("tag", "?")
            out.append(f"- **{p['name']}** (in `{tag}`, {p.get('source','?')})")
            if p.get("detail"):
                out.append(f"  - {p['detail'][:300]}")
        out.append("")
    else:
        out.append("> 近 2 周 **没有新插件**进入 master。\n")
    if commits:
        out.append(
            f"### 近 2 周 `apisix/plugins/` 提交（{len(commits)} 个）\n"
        )
        by_plugin = Counter(c["plugin"] for c in commits)
        for p, n in by_plugin.most_common(8):
            out.append(f"  - `{p}`: {n}")
        out.append("")
        out.append("### Top commits\n")
        for c in commits[:top]:
            out.append(
                f"- `{c['date'][:10]}` · `{c['plugin']}` · "
                f"{c['author']} · {c['message']} ([{c['sha']}]({c['url']}))"
            )
        out.append("")
    else:
        out.append("> 近 2 周 `apisix/plugins/` 路径 **没有提交**。\n")
    return "\n".join(out)


def _truncate(text: str, n: int) -> str:
    """Cut at n chars without splitting a markdown `[…](…)` link."""
    if len(text) <= n:
        return text
    cut = text[:n]
    tail = cut.rsplit(")", 1)[-1]
    if "[" in tail:  # an unclosed link opened after the last `)`
        cut = cut[:cut.rfind("[")]
    return cut.rstrip(" ,;") + "…"


def _kong_version_bullet(v: dict, since: str, top: int) -> list:
    """One version → header line with category counts + entry rows."""
    date = v.get("date")
    in_window = bool(date and since and date >= since)
    marker = "窗口内 ✅" if in_window else "窗口外"
    counts = v.get("counts", {})
    summary = " · ".join(f"{k} ×{n}" for k, n in counts.items()) or "无条目"
    head = (f"- **{v.get('version', '?')}**（{date[:10] if date else '日期未知'}，"
            f"{marker}）：{summary}")
    rows = []
    for e in v.get("entries", [])[:top]:
        ref = ""
        if e.get("ref_url"):
            ref = f" ([{e['ref']}]({e['ref_url']}))"
        where = f"{e['category']}/{e['area']}" if e.get("area") else e["category"]
        rows.append(f"  - `[{where}]` {_truncate(e['text'], 200)}{ref}")
    return [head] + rows


def section_kong(data: dict, top: int) -> str:
    out = ["## 5️⃣ Kong Gateway (`Kong/kong`)\n"]
    if not data:
        out.append("> 这份 data.json 早于 Kong 追踪（v1.1.0 加入），没有 `kong` 键。\n")
        return "\n".join(out)

    repo = data.get("repo", {})
    commits = data.get("commits", [])
    releases = data.get("releases", [])
    changelog = data.get("changelog", [])
    since = data.get("since", "")

    # --- 项目动向 ---
    out.append("### 项目动向\n")
    bits = []
    if repo.get("stars") is not None:
        bits.append(f"⭐ {repo['stars']:,}")
    if repo.get("open_issues") is not None:
        bits.append(f"open issues {repo['open_issues']:,}")
    if repo.get("default_branch"):
        bits.append(f"默认分支 `{repo['default_branch']}`")
    if repo.get("pushed_at"):
        bits.append(f"最近推送 `{repo['pushed_at'][:10]}`")
    if bits:
        out.append("- " + " · ".join(bits))
    if commits:
        out.append(f"- 窗口内全仓库提交 **{len(commits)}** 个，按 scope 聚合：")
        by_scope = Counter(c["scope"] for c in commits)
        for s, n in by_scope.most_common(8):
            out.append(f"  - `{s}`: {n}")
    else:
        out.append("- 窗口内全仓库 **没有提交**（`master` 节奏平缓，多为按需维护）。")
    if data.get("unreleased_count") is not None:
        n = data["unreleased_count"]
        out.append(
            f"- 下一版本待发布 changelog 条目：**{n}** 个"
            "（`changelog/unreleased/`，演进方向参考）"
        )
    out.append("")

    # --- 提交内容 ---
    out.append("### 提交内容（Top commits）\n")
    if commits:
        for c in commits[:top]:
            out.append(
                f"- `{c['date'][:10]}` · `{c['scope']}` · "
                f"{c['author']} · {c['message']} ([{c['sha']}]({c['url']}))"
            )
    else:
        out.append("> 窗口内没有提交可列；版本更新看下方 CHANGELOG 摘要。")
    out.append("")

    # --- 版本更新 ---
    out.append("### 版本更新（release / CHANGELOG 摘要）\n")
    if changelog:
        in_window = [v for v in changelog if v.get("date") and v["date"] >= since]
        # 展开窗口内的版本；窗口全空时展开最新一版作上下文。
        expand = in_window if in_window else changelog[:1]
        for v in changelog[:3]:
            if v in expand:
                out.extend(_kong_version_bullet(v, since, top))
            else:
                counts = v.get("counts", {})
                summary = " · ".join(f"{k} ×{n}" for k, n in counts.items())
                date = v.get("date")
                out.append(
                    f"- **{v['version']}**"
                    f"（{date[:10] if date else '日期未知'}，窗口外）：{summary}"
                )
        if not in_window:
            out.append("> 窗口内没有新版本；以上为最近版本要点（窗口外参考）。")
    elif releases:
        out.append("> CHANGELOG.md 拉取失败，仅有 release 列表：")
        for r in releases[:3]:
            out.append(
                f"- **{r['tag']}**（{r['published_at'][:10]}）— 正文是下载链接"
                "样板，要点见 release 分支 CHANGELOG"
            )
    else:
        out.append("> 没有抓到 release / CHANGELOG 数据。")
    out.append("")
    return "\n".join(out)


def footer() -> str:
    return (
        "---\n\n"
        "## 🛠 数据源 & 复现\n\n"
        "- 抓取脚本：`python3 -m gateway_ecosystem_report`\n"
        "- 渲染脚本：`python3 -m gateway_ecosystem_report render <data.json>`\n"
        "- 窗口默认 14 天，可用 `--days` 调整；可用 `--date YYYY-MM-DD` 锁定基准日\n"
        "- 完整说明见 [`AGENTS.md`](AGENTS.md)\n"
    )
