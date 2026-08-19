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

## 5. 验证清单

- `curl /api/health` → 200
- `curl '/api/analyze?url=https://github.com/xxx&use_ai=false'` → repo 核心字段非空（stars/forks/languages/commit_activity/contributors/open_prs/releases_count/recent_commits）
- `use_ai=true` → ai_score 含 score/grade/summary/pros/cons/suggestions/model
- 错误路径：非法 URL → 400 中文提示；仓库不存在 → 404；star-history 代理 → 200 + SVG 内容
- 浏览器：console 无 JS 错误、图表渲染无溢出

## 参考

- `references/github-repo-health-checker.md`：2026-08 仓库体检工具实例（端点清单、payload 结构、实测数据、踩坑过程）
