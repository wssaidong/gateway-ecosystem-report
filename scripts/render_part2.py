# render_part2.py - plugin sections
from collections import Counter


def section_higress_plugins(commits, top):
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
        out.append(f"- `{c['date'][:10]}` · `{c['plugin']}` · "
                   f"{c['author']} · {c['message']} ([{c['sha']}]({c['url']}))")
    out.append("")
    return "\n".join(out)


def section_apisix_plugins(data, top):
    commits = data["commits"]
    new_plugins = data["new_plugins"]
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
        out.append(f"### 近 2 周 `apisix/plugins/` 提交（{len(commits)} 个）\n")
        by_plugin = Counter(c["plugin"] for c in commits)
        for p, n in by_plugin.most_common(8):
            out.append(f"  - `{p}`: {n}")
        out.append("")
        out.append("### Top commits\n")
        for c in commits[:top]:
            out.append(f"- `{c['date'][:10]}` · `{c['plugin']}` · "
                       f"{c['author']} · {c['message']} ([{c['sha']}]({c['url']}))")
        out.append("")
    else:
        out.append("> 近 2 周 `apisix/plugins/` 路径 **没有提交**。\n")
    return "\n".join(out)


def footer():
    return ("---\n\n"
            "## 🛠 数据源 & 复现\n\n"
            "- 抓取脚本：`scripts/fetch_data.py`（依赖 `gh` CLI 已登录）\n"
            "- 渲染脚本：`scripts/render_report.py`\n"
            "- 窗口默认 14 天，可用 `--days` 调整；可用 `--date YYYY-MM-DD` 锁定基准日\n")
