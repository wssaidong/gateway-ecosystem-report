"""Plugin sections of the renderer."""
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


def footer() -> str:
    return (
        "---\n\n"
        "## 🛠 数据源 & 复现\n\n"
        "- 抓取脚本：`python3 -m gateway_ecosystem_report`\n"
        "- 渲染脚本：`python3 -m gateway_ecosystem_report render <data.json>`\n"
        "- 窗口默认 14 天，可用 `--days` 调整；可用 `--date YYYY-MM-DD` 锁定基准日\n"
        "- 完整说明见 [`AGENTS.md`](AGENTS.md)\n"
    )
