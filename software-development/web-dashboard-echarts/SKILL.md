---
name: web-dashboard-echarts
description: "Use when 开发/维护 FastAPI+ECharts Web 看板：慢任务前端异步化、图表渲染坑、主题切换、多维雷达图。"
version: 1.0.0
tags: [fastapi, echarts, frontend, async, dashboard, javascript]
---

# FastAPI + ECharts Web 看板前端

适用：「FastAPI 后端 + static/index.html + 本地 echarts.min.js」型看板工具（如 GitHub 仓库体检工具）。
核心：**慢后端任务不能阻塞整页** + **ECharts 渲染防坑** + 复用 local-web-service-debugging 做验证闭环。

## 触发场景

- 看板有慢后端任务（AI 评分 / 长抓取 / 大聚合）导致整页 loading 干等
- ECharts 图表渲染异常：横轴挤成一团、图表内容缩成 0 宽
- 需要给看板加缩放/可读性优化

## 1. 前端异步化：核心秒出 + 慢任务后台补

两段式架构（实测：总等待 73s → 核心 11s 可交互 + 慢任务 5s 后台补）：

### 后端
- 主端点加开关：`/api/analyze?use_ai=false` 只返回核心数据（秒出）
- 新增独立慢任务端点 `/api/score`：
  1. 先查磁盘缓存（24h）→ 命中直接返回（`elapsed_ms: 0`）
  2. 再取主端点刚写入的**内存缓存**（key 与主端点一致，如 `{owner}/{repo}|False`）里的 repo_summary/数据 → **避免重复拉源数据**
  3. 都没有才自己拉
- 内存缓存 key 必须与主端点完全一致，否则后台端点会重复干活（白拉一遍源数据）

### 前端（顺序是关键！）
1. fetch 主端点 `use_ai=false`
2. **先 `classList.remove('hidden')` 显示容器 → 再 render()**（否则 ECharts 0 宽度，见 §2.1）
3. `requestAnimationFrame(() => Object.values(charts).forEach(c => c && c.resize()))`
4. 后台 fetch 慢任务端点，期间渲染 loading 转圈（复用已有 `.spinner` 样式，内联在目标区域）
5. 结果回来再渲染慢任务区域；失败渲染兜底文案（`renderAI(null)` 显示「不可用」）
6. 慢任务端点不要走 `use_ai=true` 老路——它等价于整页等

## 2. ECharts 渲染坑（高频）

### 2.1 容器 hidden 时 init → 图表 0 宽度、内容挤成一团
- 症状：图表挤成一团 / 横轴标签叠爆，但数据 JSON 正常
- 根因：`echarts.init()` 在 `display:none` 容器执行，容器宽度为 0
- 修复：**先显示容器再 init**，之后 requestAnimationFrame 批量 resize

### 2.2 横轴标签太多挤成一团（52 周类数据）
- 动态间隔：`const labelStep = n > 30 ? Math.ceil(n / 12) : 0;`
- `axisLabel: { interval: labelStep, hideOverlap: true }`
- 日期标签用完整格式 `YYYY/M/D`（避免跨年歧义）
- 加 dataZoom（滚轮缩放 + 底部滑块）：
```js
dataZoom: [
  { type: 'inside', start: 0, end: 100 },
  { type: 'slider', height: 18, bottom: 8, start: 0, end: 100,
    borderColor: '#30363d', backgroundColor: 'rgba(255,255,255,.02)',
    fillerColor: 'rgba(88,166,255,.12)', handleStyle: { color: '#58a6ff' },
    textStyle: { color: '#8b949e' } }
]
```
- `grid: { bottom: 60 }` 给 slider 留空间
- tooltip 自定义 formatter：`formatter: params => params[0].name + '<br/>值：' + params[0].value`

## 3. 验证闭环

1. `python -m py_compile main.py` 语法门
2. 杀旧进程 + 后台重启 + health 检查 → **见 local-web-service-debugging**（MSYS taskkill 坑在它的 references/windows-process-kill-msys.md）
3. API 实测：分别测「核心端点首次耗时」「慢任务端点耗时」「二次访问缓存命中耗时」（time curl -w），用 python json 解析核对关键字段
4. 前端交互实测：browser_navigate → 点击 → 等核心数据时间 → snapshot 确认各 panel → browser_vision 视觉确认横轴可读性与 dataZoom
5. MSYS curl 0 字节伪象 → 用 python urllib 复核真实字节数（详见 local-web-service-debugging）
6. browser_console 求值复杂 JS 用**单行表达式**（多行 IIFE 报 `SyntaxError: Unexpected end of input`）；新前端特性逐项用 python 脚本查 HTML 落位 + console 查全局状态（charts/lastData/localStorage）

## 实测参考（2026-08 GitHub 体检工具）

- 慢任务=AI 评分（多 provider 并发竞争，见 ai_score 模式：asyncio.wait FIRST_COMPLETED + cancel 其余 + 磁盘缓存 24h + 内存缓存 10min）
- 新仓库全流程：核心 10.98s（纯 GitHub 拉取，串行 API 调用是瓶颈，下一步可并发化压到 5-6s）+ 评分 5.13s 后台补；二次访问 54ms/42ms

## 4. GitHub 多请求并发化（第二轮优化，实测 10.98s → 5.3-6.8s）

- 模式：首个依赖请求（repo 元数据）串行，其余 7-8 路 `asyncio.gather` 并发；每路内 try/except HTTPException 兜底返回默认值
- 多页 stargazers 也并发：先拿第 1 页 + Link last 页数 → `asyncio.gather` 并发拉剩余页（原串行 for）
- 共享 calls 列表跨协程 append 安全（CPython list.append 原子）
- 效果：flask 5.28s / fastapi 6.77s（含 1 次 202 重试）；大仓库不再线性叠加 RTT
- 实测参考基准：串行时代 flask 全链路含 AI 评分约 59s；并发后核心 5.3s

## 5. GitHub 数据磁盘缓存（三级缓存：内存 10min → 磁盘 6h → GitHub API）

- `.gh_cache/{owner}__{repo}.json`，TTL 由 `GH_CACHE_TTL` 环境变量控制（默认 6h）
- 取数统一走 `load_repo_data()`：内存 → 磁盘 → API，写盘同时写内存
- `/api/analyze` 与 `/api/score` 都走它 → 重启服务后二次访问依旧秒出（14ms 实测）
- 打包/交付时必须排除 `.gh_cache/` 与 `.ai_cache/` 运行时缓存目录

## 6. .env 配置化 + 限流等待重试

- 零依赖 .env 加载器（无需 python-dotenv）：读 BASE_DIR/.env，已存在环境变量优先不覆盖；提供 .env.example 模板
- 403 限流重试：`remaining=="0"` 时读 `X-RateLimit-Reset`，窗口 ≤30s 且还有重试次数则 `asyncio.sleep(wait+0.5)` 后重试，否则抛 429
- 前端评分失败降级：`fetchScore` 用 AbortController 30s 超时兜底，失败 `renderAI(null)` 显示「评分暂不可用 + 🔄 重试按钮」（retryScore 重调当前 url）

## 7. 重启服务坑（第二轮实测）

- shell 环境可能残留旧 `PORT=8748` 环境变量 → 新代码默认 8010 也被覆盖，必须显式 `PORT=8010 python main.py`
- MSYS 杀进程：`MSYS_NO_PATHCONV=1 taskkill /F /PID <pid>`（`//PID` 与 `cmd //c` 都不可靠，详见 local-web-service-debugging/references/windows-process-kill-msys.md）
- `terminal(background=true)` 返回的 PID 是 bash 包装进程，不是真实服务 PID → 用 `netstat -ano | grep ":<port>" | grep LISTEN` 取真实 PID 再 taskkill（否则报「找不到进程」）

## 8. 主题切换（深色/浅色）+ ECharts 颜色跟随

- CSS 变量方案：`:root` 定义深色，`html[data-theme="light"] { --bg/--card/--text/... }` 覆盖；切换按钮只改 `data-theme` + localStorage 记忆
- **图表颜色必须走 CSS 变量**：ECharts setOption 里硬编码的 axisLabel/splitLine/borderColor/backgroundColor 在切主题后不会变 → 加 helper `cssVar(name) = getComputedStyle(document.documentElement).getPropertyValue(name).trim()` 取色
- 组件专属变量（`--chart-border`/`--lang-bar-bg`/`--commit-border`/`--table-border`）与语义色（`--muted`/`--accent`/`--border`）分开定义，图表引用前者、UI 引用后者
- 切主题后必须 `reRenderCharts()`：用保存的 lastData 重跑各 render + 重绘雷达图，再 requestAnimationFrame resize；AI 数据也要存 lastAI 供重绘
- 打印/PDF 导出：`@media print` 隐藏 header/search/toolbar，`.panel,.card { break-inside: avoid }` 防跨页

## 9. 多维评分雷达图（LLM 结构化输出增强）

- 给 AI prompt 加新字段（如 5 维 dims）后，**LLM 常不遵守新格式**（实测 gpt-5.4 仍返回旧 JSON 无 dims）→ 双保险：
  1. 提高 max_tokens（600→800）给新字段留空间
  2. 加确定性兜底函数：LLM 没返回 dims 时从仓库指标（stars/forks/issues/releases/archived/homepage/wiki/topics）推导，保证前端永远有图
- **缓存多读路径坑**：兜底注入若只加在 ai_score() 主函数，`/api/score` 端点直接 `_ai_cache_get()` 命中返回会绕过它 → 每个读缓存返回的路径都要补兜底
- 旧缓存兼容：命中缓存时检测新字段缺失 → 补算并回写缓存（前端也需判 dims 缺失时隐藏雷达图）
- 前端雷达图：容器已可见时 init 无 0 宽问题；indicator `{name, max:100}` + series type radar；值用 `Math.min(100, Math.max(0, Number(v)||0))` 夹取
