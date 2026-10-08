# 🌐 API/AI 网关生态周报

_数据源：API7 博客、Higress 官网、Higress 仓库、Apache APISIX 仓库；窗口 = 近 14 天（截至 2026-10-08）。_


## 1️⃣ API7 / Apache APISIX 博客

> 近 2 周（14 天）**窗口内没有新文章**。最新一篇是 2026-09-22 的 3.10.7 系列文章，已超 14 天窗口。

> 窗口外最近 5 篇（供参考，可能仍在传播）：

> - **2026-09-22** · [API7 网关 3.10.7：弥合从客户端到上游的信任缺口](https://www.apiseven.com/blog/api7-3.10.7-client-upstream-trust)  
>   _API7 网关 · API 安全 · 身份认证 · TLS_
> - **2026-09-15** · [API7 网关 3.10.7：用证据降低升级不确定性](https://www.apiseven.com/blog/api7-3.10.7-upgrade-evidence)  
>   _API7 网关 · API 网关升级 · 可观测性 · API 管理_
> - **2026-09-08** · [API7 网关 3.10.6：按查询成本治理 GraphQL](https://www.apiseven.com/blog/api7-3.10.6-graphql-cost-governance)  
>   _API7 网关 · GraphQL · 限流 · API 治理_
> - **2026-09-07** · [AISIX 1.0.0 发布：让 AI 安全规则可测试，决策有依据](https://www.apiseven.com/blog/aisix-1-0-0-measurable-ai-guardrails)  
>   _AISIX · AI 网关 · AI 安全防护_
> - **2026-09-02** · [API7 网关 3.10.6：缩小自定义插件发布的影响范围](https://www.apiseven.com/blog/api7-3.10.6-custom-plugin-blast-radius)  
>   _API7 网关 · API 网关 · 自定义插件 · API 管理_
>
> 用 `--days 21` 可把 9-22 这篇纳入严格窗口。

## 2️⃣ Higress 官网博客 (`higress-group.github.io`)

> 近 2 周 `src/content/blog/` 路径 **没有任何提交**——官网 Astro 站点文章处于维护期，近期新内容主要走 higress 仓库的 release-notes。

> 注：官网默认分支是 `ai`，不是 `main`；`src/content/blog/` 之外是站点构建/Astro 代码。

## 3️⃣ Higress 插件 (`plugins/` 路径近 2 周提交)

共 **43** 个提交；按插件聚合计数：

  - `(release-automation)`: 24
  - `mcp-session`: 3
  - `ai-proxy`: 3
  - `mcp-server`: 3
  - `release`: 1
  - `plugins`: 1
  - `ai-statistics`: 1
  - `ai-data-masking`: 1

### Top commits

- `2026-10-04` · `release` · 澄潭 · chore(release): promote mcp-server 2.0.3 to stable for 2.2.5 (#4967) ([22975c8](https://github.com/higress-group/higress/commit/22975c83b858ee392e4dd912b8f47dd4dcc1128f))
- `2026-10-02` · `plugins` · 澄潭 · refactor(plugins): retire simple-jwt-auth to wasm-go examples (#4920) ([dad155c](https://github.com/higress-group/higress/commit/dad155c66d849da068dfc7004f412364aac785a0))
- `2026-09-29` · `mcp-session` · 澄潭 · fix(mcp-session): write back assembled SSE fragments when path rewrite is disabled (#4878) ([ddbaea0](https://github.com/higress-group/higress/commit/ddbaea08fee3c0a6f78efdf4a0d207632c818776))
- `2026-09-29` · `(release-automation)` · cyberslack_lee · fix main.go bug( no command-ok) (#4644) ([943b31b](https://github.com/higress-group/higress/commit/943b31bc3c012d5c845c6b6e14246f813d0c6927))
- `2026-09-29` · `ai-statistics` · Srikanth Patchava · fix(ai-statistics): make request body buffer limit configurable (#4282) ([ef1a57b](https://github.com/higress-group/higress/commit/ef1a57b128270bceca045ca55a7224bd248c8098))
- `2026-09-29` · `ai-proxy` · 0 · fix(ai-proxy): detect hunyuan embeddings API paths (#4220) ([99aaa5d](https://github.com/higress-group/higress/commit/99aaa5d2d81b48bf427c955146f4fd69d8a2fa18))
- `2026-09-29` · `(release-automation)` · 澄潭 · docs: clarify allowTools is route-scoped (#4854) ([38ac299](https://github.com/higress-group/higress/commit/38ac29958474ba06549d96d76988b9fbdc0098ad))
- `2026-09-29` · `(release-automation)` · 澄潭 · fix: require authentication for RAG MCP server write path (#4853) ([37b20cb](https://github.com/higress-group/higress/commit/37b20cb1a4f67349b8fb6f06011872111efe9ac1))
- `2026-09-29` · `(release-automation)` · 澄潭 · refactor: migrate deprecated wrapper.HasRequestBody() to ctx.HasRequestBody() (#4852) ([0a8ae29](https://github.com/higress-group/higress/commit/0a8ae29f191e0673ab25f9d1fe09d80d4aeb64b3))
- `2026-09-29` · `(release-automation)` · 澄潭 · fix: replace instead of append X-Mse-Consumer consumer identity header (#4855) ([a3714ff](https://github.com/higress-group/higress/commit/a3714ff53fa20a9f83473c21b06aebd576f0abf7))
- `2026-09-29` · `(release-automation)` · 澄潭 · fix: query-safe path joining for ext-auth envoy mode and ai-proxy basePath (#4833) ([9644191](https://github.com/higress-group/higress/commit/964419155c4fee45b2e7d42ee1b7e1aeec57ce06))
- `2026-09-29` · `(release-automation)` · 澄潭 · fix: hmac-auth-apisix fails closed for attached rules with empty allow list (#4835) ([b7fb876](https://github.com/higress-group/higress/commit/b7fb87625b9c426bf285c558ad0a72c45c7135f7))

## 4️⃣ Apache APISIX 插件

### 🆕 新增插件（来自 CHANGELOG/release notes）

- **openapi-to-mcp** (in `3.19.0`, changelog:3.19.0)
  - feat: add the `openapi-to-mcp` plugin, serving an HTTP API to MCP clients from its OpenAPI document over Streamable HTTP and HTTP+SSE [#13942](https://github.com/apache/apisix/pull/13942)
- **websocket-proxy** (in `3.19.0`, changelog:3.19.0)
  - feat(websocket): add the `websocket-proxy` plugin to customize proxy behaviors, starting with `client_max_payload_len` / `upstream_max_payload_len` for `ws`/`wss` upstreams [#13972](https://github.com/apache/apisix/pull/13972)

### 近 2 周 `apisix/plugins/` 提交（2 个）

  - `prometheus`: 1
  - `ai-rate-limiting`: 1

### Top commits

- `2026-10-08` · `prometheus` · AlinsRan · feat(prometheus): add service and service_id to the stream metrics (#13992) ([2ee8dfa](https://github.com/apache/apisix/commit/2ee8dfa810b03da1972b88e024f46c61b1e1716e))
- `2026-09-28` · `ai-rate-limiting` · Shreemaan Abhishek · feat(ai-rate-limiting): expose nested usage fields to cost_expr (#13984) ([c6b2adc](https://github.com/apache/apisix/commit/c6b2adc32ed358ee68c83b91de21d951b9c000a0))

---

## 🛠 数据源 & 复现

- 抓取脚本：`scripts/fetch_data.py`（依赖 `gh` CLI 已登录）
- 渲染脚本：`scripts/render_report.py`
- 窗口默认 14 天，可用 `--days` 调整；可用 `--date YYYY-MM-DD` 锁定基准日
