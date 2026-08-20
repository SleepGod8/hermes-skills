---
name: docs-to-knowledge-map
description: 用户要求写文档站思维导图/知识点整理时使用。程序化提取标题+真实链接生成MD。
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [docs, mindmap, mermaid, web-extraction, knowledge-map, 思维导图]
related_skills: [markdown-viewer, web-document-extraction, technical-tutorial-authoring]
---

# Docs → Knowledge Map (官方文档站思维导图)

## 触发条件

- 用户给出**普通文档站链接**（Docusaurus/Vitepress/readthedocs 等 SSR 页面，如 `*.com.cn/docs/...`、`docs.example.com/...`），要求写「知识点思维导图」「知识地图」「知识点整理」
- 要求输出 Markdown 思维导图（Mermaid mindmap 语法）+ 可点击的详细条目清单
- ⚠️ 与 `web-document-extraction` 的分工：那个管 **Canvas 渲染**受限文档（腾讯文档 textPool 解码）；本技能管**普通 HTML 文档站**的结构化提取。先判断页面类型再选技能。

## 核心原则

1. **程序化提取，不逐页点浏览器**：普通文档站直接 curl 抓 HTML + 正则解析，几秒完成，且拿到的是**页面真实链接**
2. **详细清单必须由真实 href 程序化生成，绝不手写/推断 URL**——手猜 slug 必 404（本次实测踩坑，见 Pitfall 1）
3. 页面结构（h2/h3 分类 + 各分类下链接）本身就是思维导图的骨架

## 工作流程

### Step 1: 抓取页面
```bash
curl -sL --max-time 60 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "URL" \
  -o "C:/Users/<user>/AppData/Local/Temp/page.html" -w "HTTP %{http_code} size %{size_download}\n"
```
- ⚠️ Windows/MSYS 下**不要写 `/tmp/...`**——原生 curl 不认 MSYS 路径，`wc` 报 No such file（Pitfall 2）
- fetch MCP 工具可能 Connection closed → curl 是可靠回退
- HTTP 200 且 size 非 0 即成功

### Step 2: 解析结构（execute_code 正则）
- 提取 h1-h4 标题序列（`<h([1-4])...>(.*?)</h\1>`，去 HTML 标签、html.unescape、剔除「Was this page helpful?」类噪音）
- 对每个标题块，取其到下一标题之间的所有 `/docs/...` 链接（href + 文本），按 href 去重
- 结果存 JSON（分类块列表 + 全链接映射），供下一步程序化生成
- 代码骨架见 `references/extraction-skeleton.py`（本次实测模板）

### Step 3: 生成 Mermaid mindmap
- 按标题层级缩进：`root((主题))` 中心节点 → h2 一级分支 → h3 二级分支 → 知识点叶子
- 节点文本**精简**（如「如何：递归分割文本」→「递归 / 字符」），保留 `/`、`+` 等常见符号没问题
- mindmap 用 ` ```mermaid ` 代码围栏包裹，Typora/VS Code/GitHub 均可渲染

### Step 4: 程序化生成详细清单（关键）
- 遍历分类块，h2 为主编号（`### N. 分类`），h3 为子编号（`#### N.M 子类`），条目用真实 href 拼 `[标题](https://域{href})`
- **编号逻辑坑**：遇到无链接的标题块直接跳过；section 计数器只在「有链接的 h2」处递增，避免出现空的「### 1. xxx」头（Pitfall 3）
- 全量链接用提取到的 `all_links` 映射，不手写

### Step 5: 合并输出 + 验证
- 最终 MD = 标题头（来源/日期/渲染方式说明）→ Mermaid mindmap → 详细清单 → 速记口诀（可选）
- 验证：`final.count("https://域名")` 应等于或接近实际链接数；抽查若干条 URL 拼写
- 保存到用户工作目录（如 `E:/Hermes workspace/<主题>知识点思维导图.md`）

## Pitfalls

1. **手写/推断文档 URL slug**：第一次交付时手写了一批英文路径（如 `sql_prompting`），部分与页面真实路径不符（真实是 `tool_calling` 不是 `function_calling` 等）。**必须从页面正则提取全部真实 href 后程序化生成清单**，再手工校验。推断的链接即使格式正确也可能 404。
2. **Windows curl 输出到 `/tmp` 失败**：MSYS bash 里 `-o /tmp/x.html` 会写到一个 MSYS 虚拟路径，原生 curl 不认，随后 `wc` 报 No such file。用 `C:/Users/<user>/AppData/Local/Temp/` 原生路径，或 `$LOCALAPPDATA/Temp`。
3. **编号错位**：程序化生成章节编号时，若先输出「### 1. xxx」再判断链接为空，会产生孤立空标题。先判断 `if not links: continue`，再递增计数器。
4. **页面含零宽字符**：标题文本可能带 `\u200b`（零宽空格），`html.unescape` 后要 `.replace('\u200b','')`，否则分类名显示异常。
5. **Mermaid mindmap 节点文本**：避免在节点里用 `()`、`[]` 等会被解析为形状/链接的字符；中文括号没问题；`root((LangChain<br/>How-To 手册))` 这种中心节点写法 OK。

## Verification Checklist

- [ ] 页面抓取 HTTP 200 + size 非 0
- [ ] 标题层级完整（h2/h3 分类齐全）
- [ ] 详细清单所有链接来自页面真实 href（可写脚本比对 all_links 集合）
- [ ] 无空编号标题（「### 1. 」后必有条目）
- [ ] 最终 MD 大小合理（本次 146 条链接 → 20KB）
