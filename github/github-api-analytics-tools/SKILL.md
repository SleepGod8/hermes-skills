---
name: github-api-analytics-tools
description: Use when 用 GitHub REST API 做仓库分析/健康检查/指标看板 Web 工具。
---

# GitHub API 分析类 Web 工具

适用：输入仓库 URL → 拉取 GitHub REST API → 聚合指标 → 可视化 + AI 评分 这类工具（仓库体检、指标看板、分析服务）。架构：FastAPI 后端 + 原生 HTML/JS + ECharts（本地 vendoring 离线可用）+ httpx 调 GitHub API v3。

## 1. GitHub API 调用要点

- 固定 header：`Accept: application/vnd.github+json`、`X-GitHub-Api-Version: 2022-11-28`、`User-Agent`
- token 走环境变量 `GITHUB_PERSONAL_ACCESS_TOKEN`，禁止硬编码
- **403 必须分流**：先读 `x-ratelimit-remaining` 头——为 `0` 才是限流；否则是权限问题（fine-grained PAT 缺 scope），此时自动降级匿名重试一次（`use_token=False`）
- **计数接口**（contributors / pulls / releases）：`per_page=1` + 解析 `Link` header 的 `rel="last"` 拿总数，避免拉全量；单页时 `rel="last"` 无 page 参数 → 返回 1
- **🔴 contributors 计数不要传 `anon=true`**（2026-08 实测踩坑）：`/contributors?anon=true` 会把「无 GitHub 账号的匿名提交者」（只有 email 的提交人，API 返回 login=ANON）也数进去，导致数字比 GitHub 网页侧边栏的 Contributors 数偏大。**默认（不带 anon）口径 = 网页侧边栏口径**，网页/用户核对时以默认值为准
- **网页侧边栏 Contributors N 是「宽口径展示数」，可能比 API 多出「从未提交过代码」的人**（2026-08 深度实测修正）：dsh-liang-skin 网页侧边栏 4 人，但多出的 Lichtspektrum 在该仓库 **0 commit / 0 PR / 0 issue / 0 fork / 提交邮箱零交集**，唯一关联是 star 过该 repo + README 致谢其为素材来源——侧边栏仍把他计入。**不要假设侧边栏多出来的人 = 「通过 commit email 关联的提交者」**（此假设已被实测推翻）。**API（REST contributors + GraphQL author.user + Insights 图表页）三方一致 = 真实提交者数，以 API 为准**；被质疑时给出 API 返回的具体 login 列表作证据，并主动解释「侧边栏把 README 致谢/star 过的人也计入了」
- **stats/commit_activity**：首次可能返回 202（后台计算中），sleep ~1.5s 后重试
- 网络异常指数退避重试（0.5s / 1s），每接口独立 try/except，失败不拖垮整体

## 2. Star 趋势三档方案（最容易踩的坑）

1. GitHub `stargazers` 接口需 `Accept: application/vnd.github.star+json`，且 **fine-grained PAT 必须开 Starring scope**，否则 403 `Resource not accessible by personal access token`
2. 匿名访问 stargazers 现在返回 **401 Requires authentication**（不再是公开接口）——所以无权限 token + 匿名都拿不到官方 star 历史
3. 可靠降级：后端代理 `https://api.star-history.com/svg?repos=owner/repo&type=Date` 返回 SVG（白底图 → 前端包白底容器，深色主题下别直接裸放），带内存缓存 + 失败优雅降级文案

实现顺序：后端先试 stargazers（采样最多 6 页：首页+末页+中间均匀采样，聚合成 ≤60 个点）→ 返回空数组时前端 fallback 到 `/api/star-history` 代理。

## 3. AI 评分多 provider fallback

- 顺序：ZhipuGLM（**glm-4.5 优先**，glm-4.6v-flash 高频 429）→ DashScope(qwen-plus) → ASLNet(gpt-5.4 / gpt-5.5；**池内无 gpt-4o-mini**，用了会 404 model_not_found) → 本地 Ollama(qwen2.5:7b)
- Zhipu key 可从 Hermes config.yaml 正则自动发现：`name:\s*ZhipuGLM.*?api_key:\s*(\S+)`，实现开箱即用
- 429/500 指数退避重试 2 次（1.5s / 3s）；`response_format={"type":"json_object"}` 强制 JSON；返回带 `model` 字段便于展示
- 前端优雅降级：AI 不可用时显示"未配置/调用失败"，不阻塞主体分析
- 性能预期：AI 评分 30-40s（含重试），接口总耗时约 40-100s → 前端必须有 loading 态，按钮置灰

## 4. 启动与交付

- **本机 Hermes 环境预设 `PORT=8748`** → 启动必须显式 `PORT=8000 python main.py`，README 写明，避免被环境变量劫持端口
- ECharts 本地化：从 bootcdn 下载 echarts.min.js 到 static/（约 1MB，离线可用，不依赖 CDN）
- 交付物：PROJECT_CONSTITUTION.md（工程宪法，含验收标准）+ README（运行说明）+ zip 打包 + 实测证据（真实 curl 输出，不采信自报）
- 前置检查：`python --version`、`pip list | grep fastapi/uvicorn/httpx`、`env | grep GITHUB` 确认 token 存在

## 5. 用户质疑「数据是不是编的」：排查路径

当用户拿网页/自己数的人数质疑分析结果（典型：「风险里说 X 人，我查了是 Y 人，是不是唬人？」）：

1. **先看 AI 有没有编数**：AI 评分文案（pros/cons/summary）是**照抄 payload 里的数字**生成的，不是 AI 自己编的。查 `.ai_cache/<repo>.json` 里 payload 实际值 → 数字一致 = 不是 AI 的锅
2. **再对真实 GitHub API 验证工具算的数**：直接 curl/httpx 打 `GET /repos/{owner}/{repo}/contributors`（不带 anon），对比 `Link header last` 页数。工具数 ≠ API 数 → 工具的统计口径 bug；工具数 = API 数 → 口径差异
3. **区分三种「数」**：① commit author 去重数（按 email，用户常用）② contributors API 数（按账号聚合，工具用）③ 网页侧边栏 Contributors 数（按 email 关联账号，GitHub 展示）。三者天然不同，口径对齐即可，不是造假
4. **修复数据源 bug 后必须清磁盘缓存**：`.gh_cache/`（6h）和 `.ai_cache/`（24h）TTL 长，**改完代码不删缓存，旧值还会继续吐给用户**。顺序：patch 代码 → `rm -rf .gh_cache .ai_cache` → 重启服务 → 重新实测 → 重跑 `/api/score` 确认 AI 文案跟着新数据变
5. **当用户拿「侧边栏某个人」质疑「工具怎么没统计他」时，用证据链证明该人是否真提交过代码**（全部 0 命中 = 侧边栏虚标、工具没错）。逐项 curl（带 `GITHUB_PERSONAL_ACCESS_TOKEN`）：
   - contributors：`GET /repos/{o}/{r}/contributors`（不带 anon）→ 拿 login 列表
   - commits 聚合：`GET /repos/{o}/{r}/commits?per_page=100` → 按 `author.login` / `committer.login` 去重计数（`web-flow` = GitHub 合并 bot 不算人；author 邮箱另存，用于后续邮箱对比）
   - commit 搜索：`search/commits?q=repo:{o}/{r}+author:{login}` 与 `+committer:{login}`（需 `Accept: application/vnd.github+json`）→ total_count=0 = 无提交痕迹
   - PR / issue：`GET /repos/{o}/{r}/pulls?state=all` + `issues?state=all` → 无该人
   - fork 双向：`GET /repos/{o}/{r}/forks`（谁 fork 了本 repo）+ `GET /users/{login}/repos`（该人仓库列表，查是否 fork 过）；repo 元数据 `fork`/`parent` 字段
   - 邮箱对比：嫌疑人在**自己仓库**的 commit author/committer 邮箱 vs 目标 repo 全部提交邮箱 → 零交集则彻底排除
   - 用户事件：`GET /users/{login}/events/public` → 对该 repo 若只有 WatchEvent(started) 而无 Push/PullRequest/Fork 事件 = 只是 star 过
   - 交叉验证：GraphQL `repository.defaultBranchRef.target.history` 按 `author.user.login` 去重 + 浏览器开 Insights → Contributors 图表页（默认 Last 3 months、排除 merge commits）→ 应与 API 一致
   - 兜底解释：README 致谢（「灵感/素材来源」）是侧边栏虚标的常见来源；工具按 API 官方口径统计「实际提交过代码的账号」，不要为对齐侧边栏改口径

## 6. 验证清单

- `curl /api/health` → 200
- `curl '/api/analyze?url=https://github.com/xxx&use_ai=false'` → repo 核心字段非空（stars/forks/languages/commit_activity/contributors/open_prs/releases_count/recent_commits）
- `use_ai=true` → ai_score 含 score/grade/summary/pros/cons/suggestions/model
- 错误路径：非法 URL → 400 中文提示；仓库不存在 → 404；star-history 代理 → 200 + SVG 内容
- 浏览器：console 无 JS 错误、图表渲染无溢出

## 参考

- `references/github-repo-health-checker.md`：2026-08 仓库体检工具实例（端点清单、payload 结构、实测数据、踩坑过程）
- `references/contributor-count-verification.md`：贡献者口径核查证据链 + dsh-liang-skin 侧边栏 4 vs API 3 实测案例（含全部 curl/GraphQL probes）
