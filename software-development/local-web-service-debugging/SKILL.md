---
name: local-web-service-debugging
description: "Use when 本地服务响应异常/端口被占/交付前验证服务在跑。端口归属+MSYS curl坑。"
version: 1.0.0
tags: [debugging, windows, fastapi, uvicorn, msys, port, validation]
---

# 本地 Web 服务调试与验证（Windows）

核心信条：**看到 HTTP 200 先问"这是谁的 200"**。本地开发时端口被其他进程占用，curl 打到错误服务会产生一串伪象（0 bytes / Unauthorized / 接口全 None），浪费大量时间。

## 触发条件

- 服务"启动成功"但响应异常：200 但内容不对 / Unauthorized / 0 bytes / 接口全 None
- 端口冲突（WinError 10013 / 10048 / Address already in use）
- 交付前需要"已实测通过"的本地服务验证

## 第一步：验证端口归属（调试前必做）

```bash
netstat -ano | grep :8010 | grep LISTENING    # 拿 PID
powershell -Command "Get-Process -Id <PID> | Select-Object ProcessName, Path | Format-List"
```

确认 LISTENING 进程就是自己的 uvicorn/python，**再**看响应内容。响应头是快速信号：
- 自己的 FastAPI：`server: uvicorn`
- 别人的服务：`date` / `content-length` / CSP 头与预期不符

实测教训（2026-08，GitHub 体检工具）：`PORT=8748 python main.py` 启动后 8748 实际被 **Hermes Studio**（Hermes Studio.exe）占用，所有 curl 打到的都是 Studio 的页面——"首页 200 / health Unauthorized / AI 评分返回 None" 全是**另一个服务的响应**，排查了半小时才发现端口归属错了。服务其实没在跑，重启到空闲端口（8010）后一次全通。

## 第二步：MSYS git-bash curl 输出坑

- `curl -o /dev/null -w "%{size_download}"` 在 MSYS 下可能误报 0 bytes → 用 `curl -s -i` 看真实 `Content-Length` 头
- `curl -o /tmp/x.json` 写入的 `/tmp` 与 read_file/head 看到的路径不一致（MSYS 路径映射）→ 输出到**相对路径或项目目录**，别用 `/tmp`
- 判断下载成功：`-w "%{http_code} %{size_download}"` + 文件真实存在

## 第三步：全链路验收清单（交付前）

1. 首页：`curl -s -i http://127.0.0.1:PORT/` → 200 + Content-Length 正确
2. 健康检查：`/api/health` → 返回自己的服务名（不是 `{"error":"Unauthorized"}`）
3. 核心 API：带真实参数调一遍，用 Python 解析 JSON 核对关键字段非空
4. AI/慢接口：缓存命中后重测，记录耗时（如 `ai_elapsed_ms`）
5. 前端：浏览器打开 → 输入→点按钮→等待 → accessibility snapshot 各 panel 齐全 + `browser_console` 确认 **0 JS 错误** + 用 `document.querySelectorAll` / `img.complete && img.naturalWidth>0` 验证 canvas 与 fallback 图片真实加载
   - **`.loading` 元素常驻但 `display:none`**：`!!document.querySelector('.loading')` 永远 true，判断"是否还在加载"必须 `[...document.querySelectorAll('.loading')].some(e => getComputedStyle(e).display !== 'none')`——否则会把已完成的页面误判为卡住
   - **等异步结果**：browser_console 的 expression 里用 `new Promise(r => setTimeout(() => r(JSON.stringify({...})), N))` 做延时轮询（如 4s/8s/10s 递增），别用死等
   - **localStorage 记忆别猜 key 名**：主题/历史等记忆 key（实测为 `gh_theme`/`gh_history`，不是 `theme`/`repoHistory`）用 `for (let i=0;i<localStorage.length;i++){...localStorage.key(i)...}` 枚举拿真实 key
   - **记忆持久化验证**：单次切换只证明写入；要 `browser_navigate` 刷新同 URL 后看按钮图标（🌙/☀️）+ `getComputedStyle(document.body).backgroundColor` 是否保持——刷新后仍在才算记忆成功
   - **浏览器会话会重置 localStorage**：跨会话/重开浏览器 localStorage 可能全空，历史/主题记忆验证要在同一次浏览器会话内完成，别拿上次会话的数据当现状
   - **图表重绘验证**：主题切换/数据更新后 `document.querySelectorAll('canvas').length` 应保持预期数量（如 3 = 雷达+语言分布+活跃度），再配合 `browser_vision` 做视觉确认（浅色背景、五边形、无遮挡）
6. 端口冲突时找空闲端口：`for p in 8010 8011 8012; do netstat -ano | grep ":$p " | grep LISTENING || echo "$p FREE"; done`

## 交付打包要点

- README 写清：依赖安装、启动命令、默认端口、可选配置（token/API key）、已知限制、实测记录
- 打包前清理测试残留文件（`verify_*.svg`、探针 `*.json`）
- PowerShell 打包：`Compress-Archive -Path 'dir\*' -DestinationPath 'x.zip' -Force`，再用 `[System.IO.Compression.ZipFile]::OpenRead` 列出条目验证内容
- 推送远程 / 发布前先问用户（红线）

## 常见伪象对照表

| 现象 | 真实原因 | 快速判别 |
|------|----------|----------|
| 首页 200 但 0 bytes | MSYS `/dev/null` 写入伪象 或 打错服务 | `curl -s -i` 看 Content-Length |
| `/api/health` 返回 Unauthorized | 端口被别的服务占用，打到了别人 | 验 PID / 看 `server` 头 |
| 接口全返回 None / 404 | 服务没起来或端口错 | netstat 验归属 |
| AI 评分超慢 | 429 限流重试（免费 key） | 看重试日志 / ai_elapsed_ms |
