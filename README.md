# gateway-ecosystem-report

每周（可手动触发）抓取 API/AI 网关生态的关键信号，生成一份中文生态报告。

## 覆盖范围

- **API7 / Apache APISIX 博客** — https://www.apiseven.com/blog 近 2 周新文章
- **Higress 官网** — https://higress-group.github.io 仓库 `src/content/blog` 路径的近 2 周提交
- **Higress 插件** — https://github.com/higress-group/higress 近 2 周新增/重要变更的 Wasm 插件
- **Apache APISIX 插件** — https://github.com/apache/apisix 近 2 周新增的插件

## 使用

```bash
# 1. 抓数据 + 生成报告（需要 gh 已登录、有访问 github.com 的网络或能访问 api.github.com）
python3 scripts/fetch_data.py --days 14 --out reports/$(date +%F)-ecosystem.json
python3 scripts/render_report.py reports/$(date +%F)-ecosystem.json > reports/$(date +%F)-ecosystem.md

# 2. 只看摘要（每节 Top 5）
python3 scripts/render_report.py reports/$(date +%F)-ecosystem.json --top 5
```

## Skill

`SKILL.md` 描述了完整的抓取与渲染流程，agent 可以在聊天中按需调用。

## 报告样例

见 `reports/2026-10-08-ecosystem.md`。
