"""Markdown renderer for the fetched data.

The renderer is a pure function: take the JSON dict, return a Markdown
string. Section structure is fixed; each section is robust to missing
keys (treat them as empty, not errors).
"""
from __future__ import annotations
from collections import Counter


W = "# 🌐 API/AI 网关生态周报\n\n"
W += "_数据源：API7 博客、Higress 官网、Higress 仓库、Apache APISIX 仓库；窗口 = 近 {days} 天（截至 {date}）。_\n\n"


def section_apiseven(arts: list, recent: list, top: int) -> str:
    out = ["## 1️⃣ API7 / Apache APISIX 博客\n"]
    if not arts:
        out.append(
            "> 近 2 周（14 天）**窗口内没有新文章**。"
            "最新一篇是 2026-09-22 的 3.10.7 系列文章，已超 14 天窗口。\n"
        )
        if recent:
            out.append("> 窗口外最近 5 篇（供参考，可能仍在传播）：\n")
            for a in recent:
                tags = " · ".join(a.get("tags", [])[:4])
                out.append(
                    f"> - **{a['published_at']}** · [{a['title']}]({a['url']})"
                    + (f"  \n>   _{tags}_" if tags else "")
                )
            out.append(">")
            out.append("> 用 `--days 21` 可把 9-22 这篇纳入严格窗口。\n")
    else:
        out.append(f"窗口内共 **{len(arts)}** 篇：\n")
        for a in arts[:top]:
            tags = " · ".join(a.get("tags", [])[:4])
            out.append(
                f"- **{a['published_at']}** · [{a['title']}]({a['url']})"
                + (f"  \n  _{tags}_" if tags else "")
            )
        out.append("")
    return "\n".join(out)


def section_higress_site(commits: list, top: int) -> str:
    out = ["## 2️⃣ Higress 官网博客 (`higress-group.github.io`)\n"]
    if not commits:
        out.append(
            "> 近 2 周 `src/content/blog/` 路径 **没有任何提交**——"
            "官网 Astro 站点文章处于维护期，"
            "近期新内容主要走 higress 仓库的 release-notes。\n"
        )
    else:
        out.append(f"共 **{len(commits)}** 个提交：\n")
        for c in commits[:top]:
            out.append(
                f"- `{c['date'][:10]}` · {c['author']} · "
                f"{c['message']} ([{c['sha']}]({c['url']}))"
            )
        out.append("")
    out.append(
        "> 注：官网默认分支是 `ai`，不是 `main`；"
        "`src/content/blog/` 之外是站点构建/Astro 代码。\n"
    )
    return "\n".join(out)
