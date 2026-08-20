---
name: markdown-to-html
description: "Use when 把 Markdown(含Mermaid导图)转成自包含单文件HTML. 内联渲染+无头验证。"
version: 1.0.0
author: Hermes & Iris
license: MIT
platforms: [windows, macos, linux]
---

# Markdown → 自包含单文件 HTML

## 触发条件
- 用户要求把 .md（尤其含 Mermaid mindmap / 图表 / 长清单 / 目录结构）转成 HTML
- 交付要求：单文件、离线可开、双击即用、不依赖 CDN

## 核心方案
1. **完整读取 md**：mindmap 代码块、清单区（`## 二、`）、口诀/结论区都要解析，别只取一部分
2. **下载 Mermaid v11 并内联进 HTML**（离线可用，约 3.5MB）：
   ```bash
   curl -sL -o mermaid.min.js "https://unpkg.com/mermaid@11/dist/mermaid.min.js"
   ```
3. **生成 HTML 骨架**：
   - `<pre class="mermaid">{html.escape(mindmap)}</pre>` — mermaid 通过 textContent 读原文，转义后渲染正确（含 `<br/>` 节点文本）
   - 内联 `<script>{mermaid_js}</script>` + `mermaid.initialize({startOnLoad:true, theme:"dark", mindmap:{padding:14,useMaxWidth:true}, themeVariables:{...}})`
   - 深色主题 + sticky 左侧目录（锚点跳转）+ 多列可点击链接清单（`target="_blank"`）+ 返回顶部按钮
4. **静态校验（Python）**：DOCTYPE、标签配对（open==close）、链接数、锚点数、口诀区/清单区存在
5. **无头语法验证（关键）**：Node + jsdom + 官方 mermaid npm 包跑 `mermaid.parse()` — PASS 即浏览器渲染不会语法报错。脚本见 `scripts/verify-mermaid-node.mjs`
6. **清理**：内联后删除下载的 mermaid.min.js，保持工作目录整洁

## 验证脚本
`scripts/verify-mermaid-node.mjs` — Node 无头验证任意 HTML 内所有 Mermaid 块：
```bash
cd <workdir> && npm install mermaid@11 jsdom --no-audit --no-fund --loglevel=error
node verify-mermaid-node.mjs "E:/path/to/out.html"
```

## 陷阱（全部踩过）
1. **unpkg 的 mermaid.min.js 是 esbuild UMD 变体**，Node 里 `require()`/`import()` 直接崩（`__esbuild_esm_mermaid_nm` undefined）；要验证语法就 `npm install mermaid@11` 后 `import('mermaid')` — 别在验证脚本里加载下载的 min.js
2. **Node 22 `global.navigator` 等是只读 getter**：直接赋值崩 `TypeError: Cannot set property navigator`；用 try/catch + `Object.defineProperty(global, k, {value, writable:true, configurable:true})` 兜底
3. **ESM 脚本里用 CJS 包（jsdom/fs）**：先 `import { createRequire } from "module"`，`const require = createRequire(import.meta.url)`
4. **jsdom 不实现 SVG `getBBox`**：`mermaid.render()` 必然报 `getBBox is not a function` — 这是 jsdom 限制，**验证只用 `mermaid.parse()`，别用 render**；真实渲染留给浏览器
5. **目录正则陷阱**：`^###\s+` 不会匹配 `####`（第 4 个 `#` 不是空白，`\s+` 失败）— 需先匹配 `^####\s+`（子类）再匹配 `^###\s+`（大类），或统一 `^#{3,4}\s+`
6. **头部/标签的链接数别手写死**：从生成后的 HTML 里 `count('<li><a href=')` 动态计算，避免与清单实际条数不一致（曾出现 146 vs 156）
7. **md 加粗符号 `**` 嵌入 HTML 前要剥掉**（`re.sub(r"\*\*(.*?)\*\*", r"\1", text)`），否则页面显示字面星号
8. **browser_exec 首次连 Chrome 会弹「Allow remote debugging」授权窗，需主人手动点 Allow**：无人值守/群聊环境下别依赖它做验证，直接用 Node parse 路径兜底；可告知主人点完后可补截图
9. 内联 3.5MB JS 首屏渲染约 2 秒，交付时提醒用户「打开后稍等片刻」

## 交付口径
- 单文件 HTML 路径（Windows 用 `<C:/...>` 尖括号包裹）
- 说明功能表（交互导图/目录/可点击链接/离线/响应式）
- 明确验证状态：静态检查全绿 + mermaid.parse PASS + 浏览器截图（如已做）
